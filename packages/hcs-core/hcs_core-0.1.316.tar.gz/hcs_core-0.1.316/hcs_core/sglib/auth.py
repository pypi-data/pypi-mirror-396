"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import hashlib
import json
import logging
import threading
import time

import jwt
from authlib.integrations.httpx_client import OAuth2Client

from hcs_core.ctxp import CtxpException, profile
from hcs_core.ctxp.jsondot import dotdict, dotify

from .csp import CspClient

log = logging.getLogger(__name__)


def _is_auth_valid(auth_data):
    leeway = 60
    return auth_data and time.time() + leeway < auth_data["expires_at"]


_login_lock = threading.Lock()


def login(force_refresh: bool = False, verbose: bool = False):
    """Ensure login state, using credentials from the current profile. Return oauth token."""
    return _populate_token_with_cache(profile.current().csp, force_refresh, verbose)


def refresh_oauth_token(old_oauth_token: dict, csp_url: str):
    with OAuth2Client(token=old_oauth_token) as client:
        log.debug("Refresh auth token...")
        token_url = csp_url + "/csp/gateway/am/api/auth/token"
        from .login_support import identify_client_id

        csp_specific_req_not_oauth_standard = (identify_client_id(csp_url), "")
        new_token = client.refresh_token(token_url, auth=csp_specific_req_not_oauth_standard)
        log.debug(f"New auth token: {new_token}")
        if not new_token:
            raise Exception("CSP auth refresh failed.")
        if "cspErrorCode" in new_token:
            raise Exception(f"CSP auth failed: {new_token.get('message')}")

    return new_token


def _has_credential(auth_config: dict):
    return (
        auth_config.get("apiToken")
        or auth_config.get("api_token")
        or auth_config.get("clientId")
        or auth_config.get("client_id")
        or auth_config.get("basic")
    )


def get_auth_cache(auth_config: dict):
    cache, hash, token = _get_auth_cache(auth_config)
    return token


def _get_auth_cache(auth_config: dict):
    text = json.dumps(auth_config, default=vars)
    hash = hashlib.md5(text.encode("ascii"), usedforsecurity=False).hexdigest()
    auth_cache = profile.auth.get()
    token = auth_cache.get(hash, None)
    if token and not _is_auth_valid(token):
        token = None
    return auth_cache, hash, token


def save_auth_cache(auth_config: dict, token: dict):
    """Save the auth token to the profile auth cache."""
    cache, hash, _ = _get_auth_cache(auth_config)
    if not token:
        if hash in cache:
            del cache[hash]
        return
    if not token.get("expires_at"):
        token["expires_at"] = int(time.time() + token["expires_in"])
    cache[hash] = token
    profile.auth.set(cache)


def _populate_token_with_cache(auth_config: dict, force_refresh: bool = False, verbose: bool = False):
    if verbose:
        print("_populate_token_with_cache")
    with _login_lock:
        cache, hash, token = _get_auth_cache(auth_config)
        if token and not force_refresh:
            if verbose:
                print("Using cached auth token.")
            return token

        # invalid token. Refresh or recreate it.
        if token:
            # try using refresh token if possible
            if auth_config.get("provider", "vmwarecsp") == "vmwarecsp":
                if verbose:
                    print("Provider: vmwarecsp.")
                try:
                    token = refresh_oauth_token(token, auth_config.url)
                except Exception as e:
                    log.debug(f"Failed to refresh OAuth token: {e}")
                    token = None
            else:
                # hcs auth-service. Does not support refresh token.
                if verbose:
                    print("Provider: hcs auth-service.")
                token = None

        if not token:
            if _has_credential(auth_config):
                if verbose:
                    print("Config:", auth_config)
                token = CspClient.create(**auth_config).oauth_token()
                if verbose:
                    print("Token:", json.dumps(token, indent=4))
            else:
                if auth_config.get("browser"):
                    from .login_support import login_via_browser

                    token = login_via_browser(auth_config.url, auth_config.orgId)
                    if not token:
                        raise CtxpException("Browser auth failed.")
                else:
                    raise CtxpException("Browser auth was never attempted and no client credentials or API token provided.")

        if not token.get("expires_at"):
            token["expires_at"] = int(time.time() + token["expires_in"])

        cache[hash] = token
        profile.auth.set(cache)
    return token


class CustomOAuth2Client(OAuth2Client):
    def __init__(self, auth_config: dict):
        super().__init__()
        self.auth_config = auth_config

    def ensure_token(self):
        # pylint: disable=access-member-before-definition
        if self.token is None or not super().ensure_active_token():
            self.token = _populate_token_with_cache(self.auth_config)


def oauth_client(auth_config: dict = None):
    if not auth_config:
        auth_config = profile.current().csp
    return CustomOAuth2Client(auth_config)


def details(get_org_details: bool = False) -> dotdict:
    """Get the auth details, for the current profile"""
    oauth_token = login()
    if not oauth_token:
        return
    return details_from_token(oauth_token, get_org_details)


def details_from_token(oauth_token, get_org_details: bool = False):
    decoded = jwt.decode(oauth_token["access_token"], options={"verify_signature": False})
    org_id = decoded["context_name"]
    ret = {"token": oauth_token, "jwt": decoded, "org": {"id": org_id}}

    if get_org_details:
        csp_client = CspClient(url=profile.current().csp.url, oauth_token=oauth_token)
        try:
            org_details = csp_client.get_org_details(org_id)
        except Exception as e:
            org_details = {"error": f"Fail retrieving org details: {e}"}
        ret["org"].update(org_details)
    return dotify(ret)


def get_org_id_from_token(oauth_token: str) -> str:
    decoded = jwt.decode(oauth_token["access_token"], options={"verify_signature": False})
    return decoded["context_name"]
