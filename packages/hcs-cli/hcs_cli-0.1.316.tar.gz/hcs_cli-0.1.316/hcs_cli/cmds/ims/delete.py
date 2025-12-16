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

from hcs_cli.service import ims


@click.command()
@click.argument("image_ids", type=str, required=False, nargs=-1)
@cli.org_id
@cli.wait
def delete(image_ids: list[str], org: str, wait: str, **kwargs):
    """Delete an image by ID"""

    org_id = cli.get_org_id(org)

    if not image_ids:
        image_ids = [recent.require("image", None)]

    ims.helper.delete_images(image_ids, org_id, wait)
