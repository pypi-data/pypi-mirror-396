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
import yumako
from hcs_core.ctxp import recent, util
from hcs_core.sglib import cli_options as cli

from hcs_cli.service.org_service import details


def _format_org_table(data):
    for d in data:
        d["updatedAtStale"] = yumako.time.stale(d["updatedAt"])
        d["createdAtStale"] = yumako.time.stale(d["createdAt"])
        # d["stale"] = v

        util.colorize(
            d,
            "customerType",
            {
                "INTERNAL": "bright_blue",
                "EXTERNAL": "bright_green",
            },
        )
        util.colorize(
            d,
            "markedForDeletion",
            {"true": "grey"},
        )

        util.colorize(d, "errorVMs", lambda n: "red" if n > 0 else None)

    fields_mapping = {
        "orgId": "Org Id",
        "orgName": "Org Name",
        "customerName": "Customer Name",
        "location": "Location",
        "customerType": "Customer Type",
        "markedForDeletion": "Deleted",
        "createdAtStale": "Created",
        "updatedAtStale": "Updated",
    }
    return util.format_table(data, fields_mapping)


@click.command("list")
@cli.limit
@click.option("--internal", is_flag=True, help="Filter only internal orgs")
@click.option("--external", is_flag=True, help="Filter only external orgs")
@click.option("--deleted", is_flag=True, help="Filter only deleted orgs")
@click.option("--location", type=str, required=False, help="Filter by location, in comma separated format")
@cli.search
@cli.formatter(_format_org_table)
def list_orgs(internal: bool, external: bool, deleted: bool, location: str, search: str, **kwargs):
    """List all org details"""

    if search:
        has_custom_filter = internal or external or deleted or location
        if has_custom_filter:
            raise click.UsageError("Cannot use --search with other custom filters")
        # if deleted:
        #     search += " AND markedForDeletion $eq true"
    else:
        if internal and external:
            raise click.UsageError("Cannot use --internal and --external together")
        search_clauses = []
        # if internal:
        #     search_clauses.append('customerType $eq INTERNAL')
        # if external:
        #     search_clauses.append('customerType $eq EXTERNAL')
        # if not deleted:
        #     search_clauses.append('markedForDeletion $eq true')
        if location:
            locations = [r.strip().upper() for r in location.split(",") if r.strip()]
            if locations:
                if len(locations) == 1:
                    search_clauses.append(f"location $eq {locations[0]}")
                else:
                    in_clause = ",".join(locations)
                    search_clauses.append(f"location $in {in_clause}")
        if search_clauses:
            search = " AND ".join(search_clauses)

    def fn_filter(d):
        if internal and d.get("customerType") != "INTERNAL":
            return False
        if external and d.get("customerType") != "EXTERNAL":
            return False
        if deleted and not d.get("markedForDeletion"):
            return False
        return True

    ret = details.list(org_id=None, fn_filter=fn_filter, search=search, **kwargs)
    recent.helper.default_list(ret, "org-details")
    return ret
