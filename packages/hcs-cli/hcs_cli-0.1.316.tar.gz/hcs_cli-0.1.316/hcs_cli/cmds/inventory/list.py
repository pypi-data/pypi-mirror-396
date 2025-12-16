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

import sys

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import recent

from hcs_cli.service import inventory
from hcs_cli.support.vm_table import format_vm_table


@click.command()
@cli.org_id
@cli.limit
@click.option(
    "--agent-status",
    "agentStatus",
    type=str,
    required=False,
    help="Filter by agent status, in comma separated list, e.g. UNAVAILABLE,ERROR,AVAILABLE,INIT,UNKNOWN,DOMAIN_ERR,CUSTOMIZATION_FAILURE,WAIT_FOR_HYBRID_JOIN,CUSTOM_SCRIPT_RUNNING,CUSTOM_SCRIPT_ERROR",
)
@click.option(
    "--power-state",
    "powerState",
    type=str,
    required=False,
    help="Filter by power state, in comma separated list, e.g. PoweredOn,PoweringOn,PoweredOff,PoweringOff,Unknown",
)
@click.option(
    "--lifecycle-status",
    "lifecycleStatus",
    type=str,
    required=False,
    help="Filter by lifecycle status, in comma separated list, e.g. PROVISIONING,PROVISIONED,DELETING,ERROR,MAINTENANCE,DELETING,ERROR,CUSTOMIZING,AGENT_UPDATING,AGENT_REINSTALLING",
)
@click.option(
    "--session-placement-status",
    "sessionPlacementStatus",
    type=str,
    required=False,
    help="Filter by session placement status, in comma separated list, e.g. AVAILABLE,DRAINING,QUIESCING,REPRISTINING,UNAVAILABLE",
)
@click.option(
    "--hibernate-state",
    "hibernateState",
    type=str,
    required=False,
    help="Filter by hibernate state, in comma separated list, e.g. Hibernated,Hibernating,UnKnown,None",
)
@click.option("--vm-ids", "vmIds", type=str, required=False, help="Comma separated VM IDs.")
@click.option("--max-agent-version", "maxAgentVersion", type=str, required=False, help="Filter by max agent version.")
@click.option("--powered-on-after", "poweredOnAfter", type=int, required=False, help="epoch milliseconds")
@click.option("--powered-on-before", "poweredOnBefore", type=int, required=False, help="epoch milliseconds")
@click.option(
    "--uem-enrollment-status",
    "uemEnrollmentStatus",
    type=click.Choice(["PENDING", "CACHED", "SUCCESS", "COMPLETED", "INPROGRESS", "FAILED", "UNKNOWN"]),
    required=False,
    help="Filter by UEM enrollment status.",
)
@click.argument("template_id", type=str, required=False)
@cli.formatter(format_vm_table)
def list(org: str, template_id: str, **kwargs):
    """List template VMs"""
    template_id = recent.require("template", template_id)
    fields = _trick_capture_field_option()
    if fields:
        kwargs["fields"] = fields
    ret = inventory.list(template_id, cli.get_org_id(org), **kwargs)
    recent.helper.default_list(ret, "vm")
    if not ret:
        return ""
    return ret


def _trick_capture_field_option():
    for arg in sys.argv:
        if arg.startswith("--field="):
            return arg.split("=", 1)[1]
        if arg == "--field":
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                return sys.argv[idx + 1]
            else:
                return None
        if arg == "--ids":
            return "id"
