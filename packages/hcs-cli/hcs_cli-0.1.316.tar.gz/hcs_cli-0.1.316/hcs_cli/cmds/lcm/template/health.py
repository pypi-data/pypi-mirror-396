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

import hcs_cli.service.lcm.health as health_svc
from hcs_cli.service.lcm import template


@click.command()
@click.argument("id", type=str, required=False)
@cli.org_id
def health(id: str, org: str, **kwargs):
    """Get template health by ID"""

    org_id = cli.get_org_id(org)
    id = recent.require("template", id)

    ret = template.health(id, org_id, **kwargs)
    if not ret:
        return "", 1

    return ret


@click.command()
@click.argument("id", required=False)
@cli.org_id
def health_check(id: str, org: str, **kwargs):
    """Start template health check process for a specific template."""
    org_id = cli.get_org_id(org)
    id = recent.require("template", id)
    return health_svc.template.check(org_id, id, **kwargs)
