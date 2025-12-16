import json
import logging
import sys
import time
from datetime import datetime, timezone

import click
import httpx
from yumako import env

log = logging.getLogger(__name__)

_record = None
_enabled = None
_app_name = ""


def disable():
    global _enabled
    _enabled = False


def _is_disabled():
    global _enabled
    if _enabled is None:
        _enabled = env.bool("HCS_CLI_TELEMETRY", True)
    return not _enabled


def _get_version():
    try:
        from importlib.metadata import version

        return version("hcs-cli")
    except Exception as e:
        log.debug(f"Failed to get hcs-cli version: {e}")
        return "unknown"


def _get_record():
    global _record
    if _record is None:
        _record = {
            "@timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "app": _app_name,
            "command": None,
            "options": [],
            "return": -1,
            "error": None,
            "time_ms": -1,
            "version": _get_version(),
            "env": {
                "python_version": sys.version,
                "platform": sys.platform,
                "executable": sys.executable,
            },
        }
    return _record


def start(app_name: str = None):
    if _is_disabled():
        return

    global _app_name
    _app_name = app_name
    _get_record()


def update(cmd_path: str, params: dict):
    if _is_disabled():
        return

    record = _get_record()
    record["command"] = cmd_path
    record["options"] = [k.replace("_", "-") for k, v in params.items() if v]


def end(return_code: int = 0, error: Exception = None):
    if _is_disabled():
        return

    record = _get_record()
    if error:
        if isinstance(error, click.exceptions.Exit):
            return_code = error.exit_code
        elif isinstance(error, SystemExit):
            return_code = error.code
        else:
            record["error"] = str(error)
            if return_code == 0:
                return_code = 1
    record["return"] = return_code
    record["time_ms"] = int((time.time() - datetime.fromisoformat(record["@timestamp"]).timestamp()) * 1000)

    _fix_missing_commands(record)
    _injest(record)
    return record


def _fix_missing_commands(record):
    if record["command"]:
        return

    args = sys.argv[1:]

    # this does not work for all cases, but only as best effort.
    options_started = False
    options = record["options"]
    command = [_app_name]
    for arg in args:
        if arg.startswith("-"):
            options_started = True

        if options_started:
            if arg.startswith("--"):
                options.append(arg[2:])
            elif arg.startswith("-"):
                options.append(arg[1:])
            else:
                # value. For privacy no logging.
                continue
        else:
            command.append(arg)

    record["command"] = " ".join(command)


def _injest(doc):

    # print('TELEMETRY end', json.dumps(doc, indent=4), flush=True)

    try:
        response = httpx.post(
            "https://collie.omnissa.com/es/hcs-cli/_doc",
            auth=("append_user", "public"),
            headers={"Content-Type": "application/json"},
            content=json.dumps(doc),
            timeout=4,
            verify=False,
        )
        response.raise_for_status()
    except Exception as e:
        log.debug(f"Telemetry ingestion failed: {e}", exc_info=True)
        return
