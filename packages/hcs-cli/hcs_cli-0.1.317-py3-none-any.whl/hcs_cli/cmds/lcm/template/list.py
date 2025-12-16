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

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import recent, util
from hcs_core.util import duration

from hcs_cli.service.lcm import template


def _restrict_readable_length(data: dict, name: str, length: int):
    text = data.get(name)
    if not text:
        return
    if len(text) > length:
        data[name] = text[: length - 3] + "..."


def _format_template_table(data):
    for d in data:
        updatedAt = d["updatedAt"]
        v = duration.stale(updatedAt)
        if duration.from_now(updatedAt).days >= 1:
            v = click.style(v, fg="bright_black")
        d["stale"] = v

        if d["status"] == "PARTIALLY_PROVISIONED":
            d["status"] = "*PP"

        util.colorize(
            d,
            "status",
            {
                "READY": "green",
                "ERROR": "red",
                "EXPANDING": "bright_blue",
                "SHRINKING": "bright_yellow",
                "DELETING": "bright_black",
                "PARTIALLY_PROVISIONED": "magenta",
                "*PP": "magenta",
            },
        )

        util.colorize(d, "errorVMs", lambda n: "red" if n > 0 else None)

        _restrict_readable_length(d, "name", 12)
        _restrict_readable_length(d, "templateType", 13)

    fields_mapping = {
        "id": "Id",
        "name": "Name",
        "status": "Status",
        "stale": "Stale",
        "templateType": "Type",
        "sparePolicy.limit": "Limit",
        "sparePolicy.min": "Min",
        "sparePolicy.max": "Max",
        "capacityInfo.provisionedVMs": "Prov",
        "capacityInfo.consumedVMs": "Used",
        "capacityInfo.provisioningVMs": "Crt",
        "capacityInfo.deletingVMs": "Del",
        "capacityInfo.errorVMs": "Err",
        "capacityInfo.maintenanceVMs": "Mnt",
    }
    columns_to_sum = ["Limit", "Prov", "Used", "Crt", "Del", "Err", "Mnt"]
    return util.format_table(data, fields_mapping, columns_to_sum)


@click.command("list")
@cli.org_id
@cli.limit
@click.option("--type", "-t", type=str, required=False, help="Optionally, specify cloud provider type.")
@click.option("--name", "-n", type=str, required=False, help="Optionally, specify name pattern to find.")
@cli.formatter(_format_template_table)
def list_templates(org: str, limit: int, type: str, name: str, **kwargs):
    """List templates"""
    if org == "all":
        ret = template.list_all(limit=limit, name=name, type=type)
    else:
        ret = template.list_all(limit=limit, org_id=cli.get_org_id(org), name=name, type=type)
    recent.helper.default_list(ret, "template")
    return ret
