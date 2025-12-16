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
import re
import sys
from os import path

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import data_util, recent
from hcs_core.sglib.client_util import wait_for_res_status

import hcs_cli.service.scm as scm


@click.group
def plan():
    """Commands for calendar plans."""
    # return scm.health()
    pass


@plan.command
@click.option("--template", help="Filter plan by template.")
@click.option("--task", help="Filter plan by task class name.")
@click.option("--namespace", help="Filter plan by namespace name.")
@click.option("--meta", help="Filter plan by metadata.")
@click.option("--data", help="Filter plan by data.")
@cli.org_id
def list(org: str, template: str, task: str, namespace: str, meta: str, data: str, **kwargs):
    """List named calendar plans."""
    org = cli.get_org_id(org)
    if task:
        kwargs["task"] = task
    if namespace:
        kwargs["namespace"] = namespace
    if template:
        kv = f"templateId={template}"
        if data:
            data += "," + kv
        else:
            data = kv
    if meta:
        kwargs["meta"] = meta
    if data:
        kwargs["data"] = data
    ret = scm.plan.list(org_id=org, **kwargs)
    if ret and len(ret) == 1:
        recent.set("scm.plan", ret[0]["name"])
    return ret


@plan.command
@cli.org_id
@click.argument("name", required=False)
def get(org: str, name: str, **kwargs):
    """Get a named calendar plan."""
    org = cli.get_org_id(org)
    name = recent.require("scm.plan", name)
    p = scm.plan.get(org_id=org, id=name)
    if not p:
        return "", 1
    return p


@plan.command
@cli.org_id
@click.argument("name", required=False)
@cli.confirm
def delete(org: str, name: str, confirm: bool, **kwargs):
    """Delete a named calendar plan, or specific daily or slot config."""
    org = cli.get_org_id(org)
    name = recent.require("scm.plan", name)

    ret = scm.plan.get(org_id=org, id=name, **kwargs)
    if not ret:
        return "", 1

    if not confirm:
        click.confirm(f"Delete calendar plan {name}?", abort=True)

    ret = scm.plan.delete(org_id=org, id=name, **kwargs)
    if ret is None:
        return "", 1


@plan.command
@cli.org_id
@cli.limit
@click.option("--day", required=False, help="Search by day-identifier. Example: Monday")
@click.option("--time", required=False, help="Search by time. Example: 13:30")
@click.option("--slot", required=False, help="Search by time slot. Example: Mon/13:30")
@click.option(
    "--state",
    "-s",
    required=False,
    type=str,
    help="Search by task state, as comma-separated values. E.g. 'init,running,success,error', or 'all'.",
)
@click.argument("name", required=False)
def tasks(org: str, limit: int, day: str, time: str, slot: str, name: str, state: str, **kwargs):
    """Get tasks of a named calendar plan."""
    org = cli.get_org_id(org)

    name = recent.require("scm.plan", name)

    if (day or time) and slot:
        return "day/time and slot can not be used together", 1

    if slot:
        slot = _formalize_slot_name(slot)
        day, time = slot.split("/")

    if not state:
        state = "success,error"
    elif state.lower() == "all" or state.lower() == "any":
        state = "init,running,success,error"
    else:
        pass  # use API defaults.

    ret = scm.plan.tasks(org_id=org, id=name, limit=limit, day=day, slot=time, states=state, **kwargs)
    if ret is None:
        return "", 1
    return ret


@plan.command
@cli.org_id
@click.argument("name", required=False)
@click.argument("task-key", required=False)
def task(org: str, name: str, task_key: str, **kwargs):
    """Get task by key."""
    org = cli.get_org_id(org)
    name = recent.require("scm.plan", name)
    task_key = recent.require("task.key", task_key)

    ret = scm.plan.get_task(org_id=org, id=name, task_key=task_key, **kwargs)
    if ret is None:
        return "", 1
    return ret


@plan.command
@cli.org_id
@click.option(
    "--file",
    "-f",
    type=click.File("rt"),
    default=sys.stdin,
    help="Specify the template file name. If not specified, STDIN will be used.",
)
@click.option(
    "--predefined",
    "-p",
    required=False,
    help="Use a predefined template.",
)
def create(org: str, file, predefined: str, **kwargs):
    """Create a named calendar plan."""
    org = cli.get_org_id(org)

    if predefined:
        file_name = path.join(path.dirname(__file__), f"../../payload/scm/{predefined}.json")
        file_name = path.abspath(file_name)
        with open(file_name, "rt") as f:
            text = f.read()
    else:
        with file:
            text = file.read()

    try:
        payload = json.loads(text)
    except Exception as e:
        msg = "Invalid template: " + str(e)
        return msg, 1

    name = payload["name"]
    recent.set("scm.plan", name)

    return scm.plan.create(org_id=org, name=name, payload=payload, **kwargs)


@plan.command
@cli.org_id
@click.argument("name", required=False)
@click.option("--slot", "-s", required=False, type=str, help="Example: Mon/13:30")
@click.option("--config", "-c", required=False, type=str, help='Example: {"mydata":1}')
@click.option("--delete", "-d", is_flag=True, help="Delete a specific slot by time slot.")
@click.option("--file", "-f", help="Specify the path of file of the updated plan.")
def update(org: str, name: str, slot: str, config: str, delete: bool, file: str, **kwargs):
    """Update a named calendar plan, or its slot config."""

    if file:
        if slot:
            return "--file is in use, --slot is not allowed", 1
        if config:
            return "--file is in use, --config is not allowed", 1
        if delete:
            return "--file is in use, --delete is not allowed", 1
        if name:
            return "--file is in use, name is not necessary", 1
        update = data_util.load_data_file(file)
        if not update:
            return "Invalid file: " + file, 1
        name = update.get("name")
        if not name:
            return "Invalid file: name not found in file", 1
        recent.set("scm.plan", name)

        org = cli.get_org_id(org)
        existing_plan = scm.plan.get(org_id=org, id=name)
        if not existing_plan:
            return "Plan not found: " + name, 1

        actual_update = data_util.get_delta(existing_plan, update)
        # writable_fields = ["enabled", "timezone", "calendar", "meta"]
        # for key in actual_update.keys():
        #     if key not in writable_fields:
        #         return f"Error: Key '{key}' is not allowed to be updated", 1
        # recalculate the delta meta if any
        if "meta" in actual_update:
            delta_meta = data_util.get_delta(existing_plan["meta"], update["meta"])
            if delta_meta:
                actual_update["meta"] = delta_meta
        return scm.plan.update(org_id=org, name=name, payload=actual_update, **kwargs)
    else:
        if not slot:
            return "--slot is required", 1

    if not delete and not config:
        return "Must specify --config when not deleting", 1

    org = cli.get_org_id(org)
    name = recent.require("scm.plan", name)

    slot = _formalize_slot_name(slot)

    plan_payload = scm.plan.get(org_id=org, id=name)
    if not plan_payload:
        return "Plan not found: " + name, 1

    if delete:
        return scm.plan.delete_slot(org_id=org, name=name, slot=slot, **kwargs)

    slot_config = json.loads(config)

    default_config = plan_payload["data"]
    if slot_config == default_config:
        slot_config = {}
    existing = plan_payload["calendar"].get(slot)
    if existing == slot_config:
        return plan_payload
    return scm.plan.update_slot(org_id=org, name=name, slot=slot, payload=slot_config, **kwargs)


@plan.command
@cli.org_id
@click.argument("name", required=False)
def enable(org: str, name: str, **kwargs):
    """Enable a named calendar plan."""
    org = cli.get_org_id(org)
    name = recent.require("scm.plan", name)
    p = scm.plan.get(org_id=org, id=name)
    if not p:
        return "Plan not found: " + name, 1
    if p["enabled"]:
        return p
    payload = {"enabled": True}
    return scm.plan.update(org_id=org, name=name, payload=payload, **kwargs)


@plan.command
@cli.org_id
@click.argument("name", required=False)
def disable(org: str, name: str, **kwargs):
    """Disable a named calendar plan."""
    org = cli.get_org_id(org)
    name = recent.require("scm.plan", name)
    p = scm.plan.get(org_id=org, id=name)
    if not p:
        return "Plan not found: " + name, 1
    if not p["enabled"]:
        return p
    payload = {"enabled": False}
    return scm.plan.update(org_id=org, name=name, payload=payload, **kwargs)


@plan.command
@cli.org_id
@click.argument("name", required=False)
@click.option("--slot", "-s", required=False, type=str, help="Run with config at this time slot. Example: Mon/13:30.")
@click.option("--config", "-c", required=False, type=str, help='Run with a custom config. Example: {"mydata":1}')
@cli.wait
def run(org: str, name: str, slot: str, config: str, wait: str, **kwargs):
    """Run task now, with slot config or custom config."""
    org = cli.get_org_id(org)
    name = recent.require("scm.plan", name)

    if slot and config:
        return "--slot and --config can not be used together", 2

    while True:
        if slot:
            slot = _formalize_slot_name(slot)
            ret = scm.plan.run(org_id=org, id=name, slot=slot, payload={})
            if not ret:
                "", 1
            break

        if config:
            slot_config = json.loads(config)
            ret = scm.plan.run(org_id=org, id=name, payload=slot_config)
            if not ret:
                return "", 1
            break

        ret = scm.plan.run(org_id=org, id=name, payload={})
        if not ret:
            return "", 1
        break

    # print(json.dumps(ret, indent=4))
    task_key = ret["group"] + ":" + ret["key"]
    recent.set("scm.task_key", task_key)

    if wait and wait != "0":
        return _wait_for_task(org, name, task_key, wait)
    else:
        return ret


def _wait_for_task(org_id: str, name: str, task_key: str, timeout: str):

    return wait_for_res_status(
        resource_name=name + "/" + task_key,
        fn_get=lambda: scm.plan.get_task(org_id, name, task_key),
        get_status=lambda t: t["log"]["state"],
        status_map={"ready": "Success", "error": "Error", "transition": ["Running", "Init"]},
        timeout=timeout,
        polling_interval="10s",
    )


def _formalize_slot_name(slot: str):
    slot = slot.strip().lower()
    if slot.find("/") < 0:
        raise ValueError("Invalid slot format. Example: with weekday name 'Mon/13:30', or with day of month '11/13:30'")
    day, time = slot.split("/")
    if day == "mon":
        day = "monday"
    elif day == "tue":
        day = "tuesday"
    elif day == "wed":
        day = "wednesday"
    elif day == "thu":
        day = "thursday"
    elif day == "fri":
        day = "friday"
    elif day == "sat":
        day = "saturday"
    elif day == "sun":
        day = "sunday"

    pattern = "^(?:[01]?[0-9]|2[0-3]):[0-5][0-9]$"
    p = re.compile(pattern)
    if not p.match(time):
        # try parse as day of month
        try:
            day = int(day)
            if day < 1 or day > 31:
                raise ValueError("Invalid day of month. Must be between 1 and 31")
        except ValueError:
            raise ValueError("Invalid time format. Example: 13:30")
    return day + "/" + time
