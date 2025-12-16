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
import sys
import uuid

import click
import hcs_core.sglib.cli_options as cli

from hcs_cli.service import auth, inventory, portal
from hcs_cli.support.param_util import parse_vm_path


@click.command()
@cli.org_id
@click.option(
    "--file",
    "-f",
    type=click.File("rt"),
    default=sys.stdin,
    help="Specify the template file name. If not specified, STDIN will be used.",
)
@click.option("--vm", type=str, required=False)
def assign(org: str, file, vm: str):
    """Assign user to VM"""
    org_id = cli.get_org_id(org)

    with file:
        data = file.read()

    try:
        payload = json.loads(data)
    except Exception as e:
        msg = "Invalid payload: " + str(e)
        return msg, 1

    if vm:
        template, vm_id = parse_vm_path(vm)
        payload["templateIds"] = [template]
        payload["vmId"] = vm_id

    payload["orgId"] = org_id
    return inventory.assign(payload)


@click.command()
@cli.org_id
@click.option("-pg", "--pool-group", type=str, required=True)
@click.option("-p", "--pool", type=str, required=True)
@click.option("-n", "--num-users", type=str, required=True)
def bulk_assign(org: str, pool_group: str, pool: str, num_users: int):
    """Assign  multiple users to VMs"""
    org_id = cli.get_org_id(org)
    pg = portal.pool.get(pool_group, org_id)
    payload = {
        "id": "",
        "userId": "",
        "entitlementId": pool_group,
        "templateIds": [pool],
        "allocationPolicy": "ANY",
        "sessionType": "DESKTOP",
        "username": "",
        "userPrincipalName": "",
        "userSid": "",
        "orgId": org_id,
        "location": "US",
        "templateType": pg["templateType"],
        "resume": True,
    }
    users = auth.admin.search.users(org_id, {}, -1)

    num_users = int(num_users)
    if num_users > len(users["users"]):
        print(f'max available users in AD = {len(users["users"])}, set -n less than {len(users["users"])}')
        return
    fu = users["users"][:num_users]
    dspecs = []
    for user in fu:
        payload["id"] = str(uuid.uuid4())
        payload["userId"] = user["id"]
        payload["username"] = user["userName"]
        payload["userPrincipalName"] = user["userPrincipalName"]
        payload["userSid"] = user["userSid"]
        inventory.session.assignV2(payload)
        dspecs.append(payload["id"])
    print(f"created following dspecs - {dspecs}")
