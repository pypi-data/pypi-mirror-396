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

from hcs_cli.service import admin
from hcs_cli.support.constant import provider_labels


def _get(label: str, org_id: str, id: str):
    ret = admin.provider.get(label, id, org_id=org_id)
    if ret:
        return ret
    ret = admin.provider.list(label=label, org_id=org_id, search="name $eq " + id)
    if ret:
        return ret[0]
    return None


@click.command()
@click.argument("id", type=str, required=False)
@click.option("--label", type=click.Choice(provider_labels, case_sensitive=False), required=False)
@cli.org_id
def get(label: str, id: str, org: str, **kwargs):
    """Get provider by ID or name"""
    org_id = cli.get_org_id(org)
    id = recent.require("provider", id)

    if label:
        ret = _get(label, org_id, id)
        return ret if ret else ("", 1)

    for label in provider_labels:
        ret = _get(label, org_id, id)
        if ret:
            return ret
    return "", 1
