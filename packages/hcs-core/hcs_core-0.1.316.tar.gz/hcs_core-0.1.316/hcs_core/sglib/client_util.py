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

import json
import logging
import sys
import threading
import time
from typing import Callable, Iterator

from hcs_core.ctxp import CtxpException, panic, profile
from hcs_core.sglib.ez_client import EzClient
from hcs_core.util import duration, exit
from hcs_core.util.query_util import PageRequest, with_query

log = logging.getLogger(__name__)

_caches = {}

_client_instance_lock = threading.RLock()


def _get_service_override(service_name: str):
    profile_data = profile.current()
    override = profile_data.get("override", {})
    service_override = {}
    for k, v in override.items():
        if service_name == k.lower():
            service_override = v

    if not service_override:
        if service_name == "org-service":
            service_override = override.get("org", {})
        elif service_name.find("-") >= 0:
            camel_name = "".join(word.capitalize() for word in service_name.split("-"))
            camel_name = camel_name[0].lower() + camel_name[1:]
            service_override = override.get(camel_name, {})
    return service_override


def _lazy_init(service_name: str, hdc: str = None, region: str = None):  # make it deferred so no need to initialize profile
    if region and hdc:
        raise Exception("region and hdc cannot be specified at the same time.")

    profile_data = profile.current()

    service_override = _get_service_override(service_name)
    service_override_url = service_override.get("url")
    if service_override_url:
        log.debug(f"Using per-service override for {service_name}: {service_override_url}")
        url = service_override_url
    else:
        if hdc:
            # prod only
            hdc = hdc.upper()
            if hdc == "US":
                url = profile_data.hcs.url
            elif hdc == "EU":
                url = profile_data.hcs.url.replace("cloud-sg-us", "cloud-sg-eu")
            elif hdc == "JP":
                url = profile_data.hcs.url.replace("cloud-sg-us", "cloud-sg-jp")
            else:
                raise CtxpException(f"Invalid HDC name: {hdc}. Supported HDC names: US, EU, JP.")
        elif region:
            url = _get_region_url(region)
            if not url:
                panic("Missing profile property: hcs.regions")
        else:
            url = profile_data.hcs.url
    url = url.rstrip("/") + "/" + service_name

    # TODO
    client_id = service_override.get("client-id", None)
    if not client_id:
        client_id = service_override.get("clientId", None)
    client_secret = service_override.get("client-secret", None)
    if not client_secret:
        client_secret = service_override.get("clientSecret", None)
    api_token = service_override.get("api-token", None)
    if not api_token:
        api_token = service_override.get("apiToken", None)
    provider = service_override.get("provider", "vmwarecsp")
    if provider == "vmwarecsp":
        token_url = profile_data.csp.url
    elif provider == "auth-service":
        token_url = profile_data.auth["tokenUrl"]
    else:
        raise CtxpException(f"Unknown provider: {provider}. Supported providers: vmwarecsp, auth-service.")

    if client_id:
        if not client_secret:
            panic(f"Client ID is specified but missing clientSecret for service {service_name} in profile override.")
    else:
        if client_secret:
            panic(f"Client secret is specified but missing clientId for service {service_name} in profile override.")

    if client_id:
        auth_config = {
            "url": token_url,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    elif api_token:
        auth_config = {
            "url": token_url,
            "api_token": api_token,
        }
    else:
        auth_config = None

    from hcs_core.sglib import auth

    oauth_client = auth.oauth_client(auth_config=auth_config)
    return url, oauth_client


def hdc_service_client(service_name: str, hdc: str = None) -> EzClient:
    """A client for HDC service. Cached per service name, thread-safe, lazy initialization."""
    if hdc:
        hdc = hdc.upper()
        if hdc not in ["US", "EU", "JP"]:
            panic(f"Invalid HDC name: {hdc}. Supported HDC names: US, EU, JP.")
    else:
        hdc = "US"

    k = f"{service_name}#{hdc}"
    with _client_instance_lock:
        instance = _caches.get(k)
        if not instance:
            instance = EzClient(lazy_init=lambda: _lazy_init(service_name=service_name, hdc=hdc))
            _caches[k] = instance
        return instance


def _get_region_url(region: str):
    regions = profile.current().hcs.regions
    if not region:
        return regions[0].url
    for r in regions:
        if r.name.lower() == region.lower():
            return r.url
    names = []
    for r in regions:
        names.append(r.name)
    panic(f"Region not found: {region}. Available regions: {names}")


def regional_service_client(service_name: str, region: str = None):
    # 'https://dev1b-westus2-cp103a.azcp.horizon.vmware.com/vmhub'
    region_names = [r.name.lower() for r in profile.current().hcs.regions]
    if region:
        region = region.lower()
        if region not in region_names:
            panic(f"Invalid region name: {region}. Available regions: {', '.join(region_names)}")
    else:
        region = region_names[0]

    k = f"{service_name}#{region}"
    with _client_instance_lock:
        instance = _caches.get(k)
        if not instance:
            instance = EzClient(lazy_init=lambda: _lazy_init(service_name=service_name, region=region))
            _caches[k] = instance
        return instance


def is_regional_service(service_name: str):
    regional_services = ["vmhub", "connection-service"]
    return service_name in regional_services


def service_client(service_name: str, region: str = None, hdc: str = None):
    if is_regional_service(service_name):
        return regional_service_client(service_name, region)
    else:
        return hdc_service_client(service_name, hdc)


class default_crud:
    def __init__(self, client, base_context: str, resource_type_name: str):
        self._client_impl = client
        self._base_context = base_context
        self._resource_type_name = resource_type_name

    def _client(self):
        if callable(self._client_impl):
            self._client_impl = self._client_impl()
        elif isinstance(self._client_impl, str):
            self._client_impl = hdc_service_client(self._client_impl)
        else:
            pass
        if isinstance(self._client_impl, EzClient):
            return self._client_impl
        raise CtxpException(f"Invalid client implementation: {self._client_impl}")

    def get(self, id: str, org_id: str, **kwargs):
        if org_id:
            kwargs["org_id"] = org_id
            kwargs["orgId"] = org_id
        url = with_query(f"{self._base_context}/{id}", **kwargs)
        # print(url)
        return self._client().get(url)

    def list(self, org_id: str, fn_filter: Callable = None, **kwargs) -> list:
        if org_id:
            kwargs["org_id"] = org_id
            kwargs["orgId"] = org_id

        def _get_page(query_string):
            url = self._base_context + "?" + query_string
            # print(url)
            return self._client().get(url)

        return PageRequest(_get_page, fn_filter, **kwargs).get()

    def items(self, org_id: str, fn_filter: Callable = None, **kwargs) -> Iterator:
        if org_id:
            kwargs["org_id"] = org_id
            kwargs["orgId"] = org_id

        def _get_page(query_string):
            url = self._base_context + "?" + query_string
            return self._client().get(url)

        return PageRequest(_get_page, fn_filter, **kwargs).items()

    def create(self, payload: dict, headers: dict = None, **kwargs):
        url = with_query(f"{self._base_context}", **kwargs)
        # print(url)
        # import json
        # print(json.dumps(payload, indent=4))
        if isinstance(payload, str):
            return self._client().post(url, text=payload, headers=headers)
        if isinstance(payload, dict):
            return self._client().post(url, json=payload, headers=headers)
        return self._client().post(url, json=payload, headers=headers)

    def upload(self, files, **kwargs):
        url = with_query(f"{self._base_context}", **kwargs)
        return self._client().post(url, files=files)

    def delete(self, id: str, org_id: str, **kwargs):
        if org_id:
            kwargs["org_id"] = org_id
            kwargs["orgId"] = org_id
        url = with_query(f"{self._base_context}/{id}", **kwargs)
        # print(url)
        return self._client().delete(url)

    def wait_for_deleted(self, id: str, org_id: str, timeout: str, fn_is_error: Callable = None):
        name = self._resource_type_name + "/" + id

        def fn_get():
            return self.get(id, org_id)

        return wait_for_res_deleted(name, fn_get, timeout=timeout, fn_is_error=fn_is_error)

    def update(self, id: str, org_id: str, data: dict, **kwargs):
        if org_id:
            kwargs["org_id"] = org_id
            kwargs["orgId"] = org_id
        url = with_query(f"{self._base_context}/{id}")
        return self._client().patch(url, data)


def _parse_timeout(timeout: str):
    if isinstance(timeout, int):
        return timeout
    if isinstance(timeout, str):
        return duration.to_seconds(timeout)

    raise CtxpException(f"Invalid timout. Type={type(timeout).__name__}, value={timeout}")


def wait_for_res_deleted(
    resource_name: str,
    fn_get: Callable,
    timeout: str,
    polling_interval: int = 10,
    fn_is_error: Callable = None,
):
    timeout_seconds = _parse_timeout(timeout)
    polling_interval_seconds = _parse_timeout(polling_interval)
    if polling_interval_seconds < 3:
        polling_interval_seconds = 3
    start = time.time()
    while True:
        t = fn_get()
        if t is None:
            return
        if fn_is_error:
            if fn_is_error(t):
                msg = f"Failed deleting resource '{resource_name}', resource in Error state."
                raise CtxpException(msg)

        now = time.time()
        remaining_seconds = timeout_seconds - (now - start)
        if remaining_seconds < 1:
            msg = f"Timeout waiting for resource '{resource_name}' to be deleted."
            raise TimeoutError(msg)
        sleep_seconds = remaining_seconds
        if sleep_seconds > polling_interval_seconds:
            sleep_seconds = polling_interval_seconds
        time.sleep(sleep_seconds)


# flake8: noqa=E731
def wait_for_res_status(
    resource_name: str,
    fn_get: Callable,
    get_status: Callable,
    status_map: dict = None,
    is_ready: Callable = None,
    is_error: Callable = None,
    is_transition: Callable = None,
    timeout: str = "10m",
    polling_interval: str = "20s",
    not_found_as_success: bool = False,
):
    timeout_seconds = _parse_timeout(timeout)
    polling_interval_seconds = _parse_timeout(polling_interval)
    if polling_interval_seconds < 3:
        polling_interval_seconds = 3
    start = time.time()
    prefix = f"Error waiting for resource {resource_name}: "

    if isinstance(get_status, str):
        field_name = get_status
        get_status = lambda t: t[field_name]
    if status_map:
        if is_ready:
            raise CtxpException("Can not specify is_ready when status_map is provided.")
        if is_error:
            raise CtxpException("Can not specify is_error when status_map is provided.")
        if is_transition:
            raise CtxpException("Can not specify is_transition when status_map is provided.")

        ready_status = status_map["ready"]
        error_status = status_map["error"]
        transition_status = status_map["transition"]
        if isinstance(ready_status, str):
            ready_status = [ready_status]
        if isinstance(error_status, str):
            error_status = [error_status]
        if isinstance(transition_status, str):
            transition_status = [transition_status]
        is_ready = lambda s: s in ready_status
        is_error = lambda s: error_status is None or s in error_status
        is_transition = lambda s: transition_status is None or s in transition_status
    else:
        if not is_ready:
            raise CtxpException("Either status_map or is_ready must be specified.")
        if not is_error:
            raise CtxpException("Either status_map or is_error must be specified.")
        if not is_transition:
            raise CtxpException("Either status_map or is_transition must be specified.")
        ready_status = None
        error_status = None
        transition_status = None

    while True:
        t = fn_get()
        if t is None:
            if not_found_as_success:
                return
            raise CtxpException(prefix + "Not found.")
        status = get_status(t)
        if is_error(status):
            msg = prefix + f"Unexpected terminal state. Actual={status}"
            if ready_status:
                msg += f", expected={ready_status}"
            print("-- DUMP START --", file=sys.stderr)
            print(json.dumps(t, indent=4), file=sys.stderr)
            print("-- DUMP END --", file=sys.stderr)
            raise CtxpException(msg)
        if is_ready(status):
            return t
        if not is_transition(status):
            raise CtxpException(prefix + f"Unexpected status: {status}. If this is a transition, add it to status_map['transition'].")

        now = time.time()
        remaining_seconds = timeout_seconds - (now - start)
        if remaining_seconds < 1:
            msg = prefix + f"Timeout. Current: {status}."
            if ready_status:
                msg += f" Expected: {ready_status}."
            raise TimeoutError(msg)
        sleep_seconds = remaining_seconds
        if sleep_seconds > polling_interval_seconds:
            sleep_seconds = polling_interval_seconds

        exit.sleep(sleep_seconds)
