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
from hcs_core.ctxp import util
from hcs_core.util import duration

from hcs_cli.service import admin, scm


def _format_template_table(data):
    for d in data:
        updatedAt = d["reportedStatus"]["updatedAt"]
        v = duration.stale(updatedAt)
        if duration.from_now(updatedAt).days >= 1:
            v = click.style(v, fg="bright_black")
        d["stale"] = v

        if d["reportedStatus"]["status"] == "PARTIALLY_PROVISIONED":
            d["reportedStatus"]["status"] = "*PP"

        util.colorize(
            d["reportedStatus"],
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

        util.colorize(d, "addedVmHours", lambda n: "bright_red" if n and n > 0 else None)
        util.colorize(d, "reducedVmHours", lambda n: "green" if n and n > 0 else None)
        util.colorize(d, "offloadVmHours", lambda n: "bright_yellow" if n and n > 0 else None)

    fields_mapping = {
        "id": "Id",
        "name": "Name",
        "reportedStatus.status": "Status",
        "stale": "Stale",
        "templateType": "Type",
        "sparePolicy.limit": "Limit",
        "provisioned_percentage": "%Prov",
        "used_percentage": "%Used",
        "addedVmHours": "+ Hrs",
        "offloadVmHours": "Offload Hrs",
        "reducedVmHours": "- Hrs",
        "historyVmUtilizationPercent": "H.Util.",
        # "predictionVmUtilizationPercent": "P.Util.",
    }
    columns_to_sum = ["Limit", "+ Hrs", "Offload Hrs", "- Hrs"]
    return util.format_table(data, fields_mapping, columns_to_sum)


@click.command(name="list-usage", hidden=True)
@cli.org_id
@cli.formatter(_format_template_table)
def list_usage(org: str, **kwargs):
    """List template usage"""

    org_id = cli.get_org_id(org)

    search_floating = "templateType $in FLOATING,MULTI_SESSION"
    ret = admin.template.list(org_id=org_id, limit=100, search=search_floating, **kwargs)

    ret2 = []
    for template in ret:
        reported_status = template["reportedStatus"]
        created_capacity = (
            reported_status["provisionedVMs"]
            + reported_status["errorVMs"]
            + reported_status["maintenanceVMs"]
            + reported_status["agentUpdatingVMs"]
            + reported_status["agentReinstallingVMs"]
        )
        limit = template["sparePolicy"]["limit"]
        provisioned_percentage = int(created_capacity * 100 / limit)
        used_percentage = int(reported_status["consumedVMs"] * 100 / limit)

        usage = scm.template_usage(org_id, template["id"])
        if usage:
            summary = usage["summary"]
        else:
            summary = {}

        item = {
            "id": template["id"],
            "name": template["name"],
            "templateType": template["templateType"],
            "sparePolicy": template["sparePolicy"],
            "reportedStatus": reported_status,
            "provisioned_percentage": f"{provisioned_percentage}%",
            "used_percentage": f"{used_percentage}%",
            "addedVmHours": summary.get("addedVmHours"),
            "offloadVmHours": summary.get("offloadVmHours"),
            "reducedVmHours": summary.get("reducedVmHours"),
            "historyVmUtilizationPercent": f'{summary.get("historyVmUtilizationPercent", 0)}%',
            "predictionVmUtilizationPercent": f'{summary.get("predictionVmUtilizationPercent", 0)}%',
        }

        ret2.append(item)

    return ret2
