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
from hcs_core.ctxp.profile import current

from hcs_cli.service import org_service
from hcs_cli.support import use_util


@click.command()
@cli.org_id
@click.argument("smart-search", type=str, required=False)
def get(org: str, smart_search: str):
    """Get org details"""

    if not smart_search:
        org_id = cli.get_org_id(org)
        ret = org_service.details.get(org_id)
        if ret:
            return ret
        return ret, 1

    smart_search = smart_search.strip()

    if use_util.looks_like_id(smart_search):
        ret = org_service.details.list(search=f"orgId $eq {smart_search}")
    else:
        search = f"orgName $like '{smart_search}' OR orgId $like '{smart_search}' OR customerName $like '{smart_search}'"
        ret = org_service.details.list(search=search)

    id_field = "orgId"
    result = use_util.require_single(items=ret, resource_type="org", id_field=id_field, name_field="orgName", interactive=False)

    # if org changed, reset everything
    if isinstance(result, dict):
        id = result[id_field]
        if id != current:
            recent.unset_all()
            recent.set("org", id)
    return result
