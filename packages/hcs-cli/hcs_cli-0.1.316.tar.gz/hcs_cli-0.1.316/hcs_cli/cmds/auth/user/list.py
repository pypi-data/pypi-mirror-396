"""
Copyright 2025 Omnissa Inc.
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

from hcs_cli.service import auth


@click.command(name="list")
@cli.org_id
@click.option("--username", type=str, help="u1ad1")
@click.option("--top", type=int, help="3")  # returns 3 records with a nextLink. to return all records no need to include this option
def list_users(org: str, username: str, top: int):
    """Users search from Active directory"""
    # https://cloud-sg.horizon.omnissa.com/auth/v2/admin/users/search?org_id=f8d70804-1ce7-49a1-a754-8cae2e79ae10&top=-1
    # {"userName":"u1ad"} filters users starting with u1a
    # if payload is {}, it returns all users
    org_id = cli.get_org_id(org)
    payload = {}
    if username is not None:
        payload["userName"] = username
    if top is None:
        top = -1
    return auth.admin.search.users(org_id, payload, top)
