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

from datetime import datetime, timedelta

import click
import hcs_core.sglib.cli_options as cli
import yumako
from hcs_core.ctxp import recent

import hcs_cli.service as hcs
from hcs_cli.service.task import TaskModel, recent_task


@click.group
def operator():
    """Commands for intelligent operator."""
    pass


@operator.command
@cli.org_id
@click.argument("name", required=False)
@click.option("--text", "-t", is_flag=True, required=False, type=bool, help="Print human readable logs")
@click.option("--params", "-p", required=False, type=str, help="Parameter for the operator")
@cli.wait
def run(org: str, name: str, text: bool, wait: str, params: str, **kwargs):
    """Run a specific operator for a specific org."""
    org_id = cli.get_org_id(org)
    task = hcs.scm.operator.run(org_id=org_id, name=name, params=params)

    recent.set("scm.operator", name)
    recent_task(task=task, namespace="scm")  # keep track of recent task

    if wait == "0":
        return task

    ret = hcs.task.wait(org_id=org_id, namespace="scm", task=task, timeout=wait)
    if text:
        _print_human_readable_log(ret)
        return
    return ret


def _print_error(text: str):
    click.echo(click.style(text, fg="bright_red"))


def _print_human_readable_log(d: TaskModel):
    ret = d.log
    time_started = ret.time_started
    time_completed = ret.time_completed

    if time_completed:
        delta = timedelta(milliseconds=time_completed - time_started)
        delta_display = "completed: " + yumako.time.display(delta)
    else:
        delta = timedelta(milliseconds=datetime.now().timestamp() * 1000 - time_started)
        delta_display = click.style("pending", fg="bright_blue") + ": " + yumako.time.display(delta)

    start_time = datetime.fromtimestamp(time_started / 1000)
    stale = yumako.time.display(datetime.now() - start_time)
    print("----------------------------------------------------------------------------------")
    print(start_time.strftime("%Y-%m-%d %H:%M:%S"), stale, "ago,", delta_display, f" task={d.key}")
    print("----------------------------------------------------------------------------------")
    props = ret.properties
    code = props.get("code")
    if code and code != 0:
        _print_error(f"Code: {code}")
    stdout = props.get("stdout")
    if stdout:
        click.echo(click.style(stdout, fg="white"))
    stderr = props.get("stderr")
    if stderr:
        _print_error(stderr)
    exception = props.get("exception")
    if exception:
        _print_error("Exception:" + exception)


@operator.command
@cli.org_id
@click.argument("name", required=False)
@click.option("--text", "-t", is_flag=True, required=False, type=bool, help="Print human readable format.")
@click.option("--limit", "-l", type=int, required=False, default=1, help="Optionally, the number of records to fetch.")
def logs(org: str, name: str, text: bool, limit: int, **kwargs):
    """Get logs of an operator."""
    org_id = cli.get_org_id(org)
    name = recent.require("scm.operator", name)

    data = hcs.scm.operator.logs(org_id=org_id, name=name, limit=limit)
    if not data:
        return

    data = list(reversed(data))
    if text:
        for d in data:
            _print_human_readable_log(d)
            print()
        return
    return data
