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

from hcs_cli.service.lcm import template


@click.command()
@cli.org_id
@click.option("--target-capacity", "-t", type=int, required=False, default=-1, help="Target number of spare VMs.")
@click.option(
    "--protection-time",
    "-p",
    type=str,
    required=False,
    default="30m",
    help="Protection time before shrinking. E.g. 30m.",
)
@click.argument("id", type=str, required=False)
def provision(org: str, target_capacity: int, protection_time: str, id: str):
    """Suggest capacity configuration and override the default settings, within a protection time."""
    org_id = cli.get_org_id(org)
    id = recent.require("template", id)
    t = template.get(id, org_id)
    if not t:
        return

    spare_policy = t.sparePolicy
    if target_capacity == -1:
        ci = t["capacityInfo"]
        target_capacity = ci["consumedVMs"] + int((spare_policy.max + spare_policy.min) / 2)

    if target_capacity > spare_policy.limit:
        target_capacity = spare_policy.limit
    elif target_capacity < 0:
        target_capacity = 0

    if not protection_time:
        protection_time = "30m"

    return template.ensure_capacity(id, org_id, target_capacity, protection_time)
