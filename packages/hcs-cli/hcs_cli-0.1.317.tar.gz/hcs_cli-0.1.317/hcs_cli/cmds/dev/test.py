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

import logging
import time

import click
import hcs_core.sglib.cli_options as cli

from hcs_cli.service import scm

log = logging.getLogger("test")


@click.command(hidden=True)
@cli.org_id
def test(org: str, **kwargs):
    while True:
        try:
            h = scm.health()
        except Exception:
            raise
        log.info(f"tick: {h}")
        time.sleep(60)
