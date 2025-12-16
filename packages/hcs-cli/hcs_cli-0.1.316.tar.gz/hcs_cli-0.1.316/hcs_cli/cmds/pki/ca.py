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

from hcs_cli.service.pki import certificate


@click.command()
@click.option("--label", "-l", "ca_label", type=str, required=False)
@click.option("--all", "-a", is_flag=True, default=False, help="Get all root CAs.")
def ca(ca_label: str, all: bool):
    """Get the certificate of the root CA."""

    if ca_label and all:
        raise click.BadParameter("You cannot specify both --label and --all. Use one or the other.")
    if all:
        return certificate.get_all_root_ca()
    ca_map = certificate.get_all_root_ca()
    if not ca_label:
        ca_label = "omnissa"
    return ca_map.get(ca_label)
