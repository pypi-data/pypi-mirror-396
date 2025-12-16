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
from hcs_core.ctxp import recent

import hcs_cli.service as hcs
from hcs_cli.support.scm.plan_editor import edit_plan


@click.command
@click.argument("id", type=str, required=False)
@cli.org_id
def template(id: str, org: str, **kwargs):
    """Calendar plan for template."""

    org_id = cli.get_org_id(org)
    id = recent.require("template", id)

    # get plan for the template

    plan_id = f"CapacityOptimization-{id}"
    plan = hcs.scm.plan.get(id=plan_id, org_id=org_id)
    if not plan:
        return None, 1

    template = hcs.template.get(org_id=org_id, id=id)

    plan["meta"]["maxCapacity"] = template["sparePolicy"]["limit"]
    calendar = plan["calendar"]
    for key in calendar:
        calendar[key]["calculatedCapacity"] = calendar[key]["idealCapacity"]
        calendar[key]["idealCapacity"] = calendar[key]["forecastCapacity"]
    edit_plan(plan, template["name"])
