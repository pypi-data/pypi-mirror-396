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

import os
from os import path
from pathlib import Path

import click

from . import cli_processor, config, profile, state, telemetry


def _get_store_path():
    if os.name == "nt":  # Windows OS
        return str(Path.home())
    uid = os.getuid()
    if uid == 0 or uid == 1000:
        return "/tmp"
    if os.path.exists("/.dockerenv"):
        return "/tmp"
    return str(Path.home())


user_home = _get_store_path()


_initialized_app_name = None


def init(app_name: str, store_path: str = user_home, config_path: str = "./config"):
    global _initialized_app_name
    if _initialized_app_name == app_name:
        return

    if _initialized_app_name is not None:
        raise ValueError(f"App {app_name} already initialized with {_initialized_app_name}")
    _initialized_app_name = app_name
    try:
        real_store_path = path.join(store_path, "." + app_name)
        state.init(real_store_path, ".state")
        profile.init(real_store_path)
        config.init(config_path)

    except Exception as e:
        # critical errors, must print stack trace.
        if _need_stack_trace(e):
            raise e
        else:
            # Other errors, no stack.
            from .util import panic

            panic(e)


# init default with env if configured
_app_name = os.environ.get("CTXP_APP_NAME")
if _app_name:
    init(_app_name)


def app_name():
    dir_name = path.dirname(state._file._path)
    name = dir_name[dir_name.rindex(os.sep) + 1 :]
    if name.startswith("."):
        return name[1:]
    raise ValueError("Unable to determine app name: " + dir_name)


def init_cli(main_cli: click.Group, commands_dir: str = "./cmds"):
    try:
        telemetry.start(_initialized_app_name)
        ret = cli_processor.init(main_cli, commands_dir)
        telemetry.end()
        return ret
    except BaseException as e:
        telemetry.end(error=e)
        if _need_stack_trace(e):
            raise e
        else:
            from .util import panic

            panic(e)


def _need_stack_trace(e) -> bool:
    program_errors = [
        LookupError,
        TypeError,
        ValueError,
        ArithmeticError,
        NameError,
        SyntaxError,
        KeyError,
        AttributeError,
    ]
    for t in program_errors:
        if isinstance(e, t):
            return True
    return False
