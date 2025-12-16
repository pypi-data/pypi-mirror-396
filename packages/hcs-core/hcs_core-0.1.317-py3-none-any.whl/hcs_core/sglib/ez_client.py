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
import os
import sys
import threading
from http.client import HTTPResponse
from typing import Callable, Optional, Type

import httpx
from authlib.integrations.httpx_client import OAuth2Client
from pydantic import BaseModel

from hcs_core.ctxp import jsondot

log = logging.getLogger(__name__)

_print_http_error = True


def parse(resp: httpx.Response):
    if not resp.content:
        return None
    content_type = resp.headers["Content-Type"]
    if content_type.startswith("text"):
        return resp.text
    if len(resp.content) > 3:
        try:
            data = resp.json()
            if isinstance(data, list):
                return [jsondot.dotify(obj) for obj in data]
            elif isinstance(data, dict):
                return jsondot.dotify(data)
        except:
            log.info("--- Fail parsing json. Dump content ---")
            log.info(resp.content)
            raise
    else:
        return None


def _raise_on_4xx_5xx(response: httpx.Response):
    if not response.is_success:
        response.read()
        if len(response.text) > 0:
            text = _try_formatting_json(response.text)
            log.debug(text)

    response.raise_for_status()


def _try_formatting_json(text: str):
    try:
        return json.dumps(json.loads(text), indent=4)
    except:
        return text


def _log_request(request):
    if not log.isEnabledFor(logging.DEBUG):
        return
    log.debug("\n")
    log.debug(f"--> {request.method} {request.url}")
    log.debug(f"--> {request.headers}")

    if len(request.content) > 0:
        text = _try_formatting_json(request.content)
        log.debug(text)


def _log_response(response: httpx.Response):
    if not log.isEnabledFor(logging.DEBUG):
        return
    request = response.request
    log.debug(f"<-- {request.method} {request.url} - {response.status_code}")
    log.debug(f"<-- {request.headers}")
    response.read()
    if len(response.text) > 0:
        text = _try_formatting_json(response.text)
        log.debug(text)
    log.debug("\n")


def _parse_resp(resp: httpx.Response):
    if not resp.content:
        return
    content_type = resp.headers["Content-Type"]
    if content_type.startswith("text"):
        return resp.text
    if content_type == "application/json" and resp.content:
        try:
            data = resp.json()
            return jsondot.dotify(data)
        except:
            log.info("--- Fail parsing json. Dump content ---")
            log.info(resp.content)
            raise
    return resp.text


def _is_404(e: httpx.HTTPStatusError) -> bool:
    return e.response.status_code == 404


def on404ReturnNone(func):
    try:
        resp = func()
        return _parse_resp(resp)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise


def _raise_http_error(e: httpx.HTTPStatusError):
    if _print_http_error:
        print(e.response.text, file=sys.stderr)
    raise e


class EzClient:
    def __init__(self, base_url: str = None, oauth_client: OAuth2Client = None, lazy_init: Callable = None) -> None:
        # self._client = httpx.Client(base_url=base_url, timeout=30, event_hooks=event_hooks)

        self._client_impl = None
        self._lazy_init = lazy_init
        self._lock = threading.Lock()

        if lazy_init:
            if base_url:
                raise ValueError("Cannot use both base_url and lazy_init")
            if oauth_client:
                raise ValueError("Cannot use both oauth_client and lazy_init")
        else:
            if not base_url:
                raise ValueError("base_url must be provided if lazy_init is not used")
            if not oauth_client:
                raise ValueError("oauth_client must be provided if lazy_init is not used")
            self._init_client(base_url, oauth_client)

    def _init_client(self, base_url: str, client: OAuth2Client):
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        client.base_url = base_url
        client.timeout = int(os.environ.get("HCS_TIMEOUT", 30))
        request_hooks = client.event_hooks["request"]
        response_hooks = client.event_hooks["response"]
        if _log_request not in request_hooks:
            request_hooks.append(_log_request)
        if _log_response not in response_hooks:
            response_hooks.append(_log_response)
        if _raise_on_4xx_5xx not in response_hooks:
            response_hooks.append(_raise_on_4xx_5xx)
        self._client_impl = client

    def _client(self):
        self._lock.acquire()
        try:
            if self._lazy_init:
                base_url, client = self._lazy_init()
                self._init_client(base_url, client)
                self._lazy_init = None

            self._client_impl.ensure_token()
            return self._client_impl
        finally:
            self._lock.release()

    def post(
        self,
        url: str,
        json: dict = None,
        text: str = None,
        files=None,
        headers: dict = None,
        type: Optional[Type[BaseModel]] = None,
        timeout: float = 30.0,
    ):
        # import json as jsonlib
        # print("->", self._client().base_url, url, jsonlib.dumps(json, indent=4))
        try:
            resp = self._client().post(url, json=json, content=text, files=files, headers=headers, timeout=timeout)
        except httpx.HTTPStatusError as e:
            _raise_http_error(e)
        data = _parse_resp(resp)
        if data and type:
            try:
                return type.model_validate(data)
            except:
                log.info("--- Fail converting model. Dump content ---")
                log.info(data)
                raise
        return data

    def get(self, url: str, headers: dict = None, raise_on_404: bool = False, type: Optional[Type[BaseModel]] = None):
        try:
            # print("->", self._client().base_url, url)
            resp = self._client().get(url, headers=headers)
            data = _parse_resp(resp)
            if data and type:
                try:
                    return type.model_validate(data)
                except:
                    log.info("--- Fail converting model. Dump content ---")
                    log.info(data)
                    raise
            return data
        except httpx.HTTPStatusError as e:
            if _is_404(e):
                if raise_on_404:
                    _raise_http_error(e)
                else:
                    pass
            else:
                _raise_http_error(e)

    def patch(self, url: str, json: dict = None, text=None, headers: dict = None):
        try:
            resp = self._client().patch(url, json=json, content=text, headers=headers)
            return _parse_resp(resp)
        except httpx.HTTPStatusError as e:
            _raise_http_error(e)
            raise

    def delete(self, url: str, headers: dict = None, raise_on_404: bool = False):
        try:
            resp = self._client().delete(url, headers=headers)
            return _parse_resp(resp)
        except httpx.HTTPStatusError as e:
            if _is_404(e):
                if raise_on_404:
                    _raise_http_error(e)
                else:
                    pass
            else:
                _raise_http_error(e)

    def put(self, url: str, json: dict = None, text=None, headers: dict = None):
        try:
            resp = self._client().put(url, json=json, content=text, headers=headers)
            return _parse_resp(resp)
        except httpx.HTTPStatusError as e:
            _raise_http_error(e)

    def close(self):
        self._client().close()

    def dump_response(self, response: HTTPResponse):
        log.info("response text: " + response.text())
