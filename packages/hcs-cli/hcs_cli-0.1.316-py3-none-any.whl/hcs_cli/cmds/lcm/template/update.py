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

import json as json_lib
import random

import click
import hcs_core.ctxp.data_util as data_util
import hcs_core.sglib.cli_options as cli
import hcs_core.util.duration as duration
from hcs_core.ctxp import recent

import hcs_cli.service.lcm as lcm


@click.command()
@click.argument("template_id", type=str, required=False)
@click.option(
    "--update",
    "-u",
    type=str,
    multiple=True,
    required=False,
    help="Specify field and value pair to update. E.g. '-u sparePolicy.max=3'.",
)
@click.option(
    "--json",
    "-j",
    type=str,
    required=False,
    help="Patch an object field. E.g. '--json sparePolicy={\"max\":3}'.",
)
@cli.org_id
@cli.wait
def update(template_id: str, update, json: str, org: str, wait: str, **kwargs):
    """Update an existing template"""

    org_id = cli.get_org_id(org)

    template_id = recent.require("template", template_id)
    template = lcm.template.get(template_id, org_id)

    if not template:
        return "Template not found: " + template_id, 1

    need_update = False
    for u in update:
        k, v = u.split("=", 1)
        current_value = data_util.deep_get_attr(template, k, False)
        if str(current_value) == str(v):
            continue
        data_util.deep_set_attr(template, k, v)
        need_update = True

    if json:
        k, v = json.split("=", 1)
        current_value = template.get(k, None)
        if json_lib.dumps(current_value) != v:
            template[k] = json_lib.loads(v)
            need_update = True

    if not need_update:
        return template

    ret = lcm.template.update(template)
    if wait != "0":
        ret = lcm.template.wait(template_id, org_id, duration.to_seconds(wait))
    return ret


def _rand_id(n: int):
    return "".join(random.choices("abcdefghijkmnpqrstuvwxyz23456789", k=n))


def _create_zerocloud_provider(org_id: str):
    data = {"name": "nanw-test-" + _rand_id(4), "orgId": org_id, "type": "ZEROCLOUD"}

    return lcm.provider.create(data)
