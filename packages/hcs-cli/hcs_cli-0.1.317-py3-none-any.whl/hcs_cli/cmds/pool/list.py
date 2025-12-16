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
import yumako
from hcs_core.ctxp import recent, util

from hcs_cli.service import portal


def _format_pool_table(data):
    for d in data:
        d["stale"] = yumako.time.stale(d["updatedAt"])
        d["templateCount"] = len(d["templates"])
        stat = d.get("_statistics")
        if stat:
            d["_session_stat"] = f"{stat['used_sessions']}/{stat['free_sessions']}/{stat['provisioned_sessions']}"
            d["_vm_stat"] = f"{stat['provisioned_vms']}/{stat['limit_vms']}"
        d["_display"] = d.get("displayName") or d["name"]

    fields_mapping = {
        "id": "Id",
        "_display": "Name",
        # "type": "Type",
        "templateType": "Template",
        "location": "Loc",
        "stale": "Update",
        "templateCount": "Tmpl",
        "_vm_stat": "VM (prov/limit)",
        "_session_stat": "Session (used/free/prov)",
    }
    columns_to_sum = ["Limit", "Prov", "Used", "Crt", "Del", "Err", "Mnt"]
    return util.format_table(data, fields_mapping, columns_to_sum)


@click.command()
@click.option("--search", "-s", type=str, required=False, help="Search condition")
@click.option("--all/--default", "-a/-d", type=bool, default=False, help="Specify whether to show deleted and internal pools.")
@click.option("--raw", is_flag=True, default=False, help="Return the raw data as API response. Do not calculate '_statistics' object.")
@cli.limit
@cli.org_id
@cli.formatter(_format_pool_table)
def list(org: str, all: bool, raw: bool, **kwargs):
    """List pools"""
    org_id = cli.get_org_id(org)
    pools = portal.pool.list(org_id, exclude_disabled_pools=not all, include_internal_pools=all, **kwargs)
    recent.helper.default_list(pools, "pool")

    if not raw:
        for p in pools:
            _statistics = {
                "limit_vms": 0,
                "provisioned_vms": 0,
                "used_sessions": 0,
                "free_sessions": 0,
                "provisioned_sessions": 0,
            }
            p["_statistics"] = _statistics
            for t in p["templates"]:
                r = t.get("reportedStatus")
                if not r:
                    continue
                _statistics["provisioned_vms"] += r.get("provisionedVMs", 0)
                _statistics["used_sessions"] += r.get("usedSessions", 0)
                _statistics["free_sessions"] += r.get("freeSessions", 0)
                _statistics["provisioned_sessions"] += r.get("provisionedSessions", 0)

                _statistics["limit_vms"] += t["sparePolicy"]["limit"]

    return pools
