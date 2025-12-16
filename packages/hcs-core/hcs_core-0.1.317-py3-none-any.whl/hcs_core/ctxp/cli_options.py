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

import click

verbose = click.option(
    "--verbose",
    "-v",
    count=True,
    default=0,
    hidden=True,
    help="Print debug logs",
)

output = click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "json-compact", "yaml", "yml", "table", "t", "text"], case_sensitive=False),
    default=None,
    hidden=True,
    help="Specify output format",
)

field = click.option(
    "--field",
    type=str,
    required=False,
    hidden=True,
    help="Specify fields to output, in comma separated field names.",
)

exclude_field = click.option(
    "--exclude-field",
    type=str,
    required=False,
    hidden=True,
    help="Specify fields to exclude from output, in comma separated field names.",
)

wait = click.option(
    "--wait",
    "-w",
    type=str,
    is_flag=False,
    flag_value="1m",
    default="0",
    help="Wait time. E.g. '30s', or '5m'. Default: 1m.",
)

search = click.option(
    "--search",
    "-s",
    type=str,
    required=False,
    help="Specify REST search. E.g. 'name $eq something'. Note: use single quote in bash/sh.",
)

sort = click.option(
    "--sort",
    type=str,
    required=False,
    help="Ascending/Descending. Format is property,{asc|desc} and default is ascending",
)

limit = click.option("--limit", "-l", type=int, required=False, default=100, help="Optionally, specify the number of records to fetch.")

ids = click.option(
    "--ids",
    "--id-only",  # to be removed.
    is_flag=True,
    type=bool,
    required=False,
    default=False,
    hidden=True,
    help="Return only id of the document",
)

first = click.option(
    "--first",
    is_flag=True,
    type=bool,
    required=False,
    default=False,
    hidden=True,
    help="Return only the first object, if the result is a list.",
)

force = click.option("--force/--grace", type=bool, default=True, help="Specify deletion mode: forceful, or graceful.")

confirm = click.option("--confirm/--prompt", "-y", type=bool, default=False, help="Confirm the operation without prompt.")

env = click.option(
    "--env",
    multiple=True,
    type=str,
    required=False,
    help="Alternative explicit in-line environment variable override in KEY=VALUE format.",
)


def apply_env(envs):
    for kv in envs:
        k, v = kv.split("=", 1)
        os.environ[k.strip()] = v.strip()


def formatter(formatter=None, columns=None):
    def decorator(f):
        f.formatter = formatter if formatter else columns
        return f

    return decorator
