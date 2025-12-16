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
import hcs_core.ctxp.cli_options as cli
from hcs_core.ctxp.extension import ensure_extension


@click.group(hidden=True)
def test():
    """Test."""


@test.command()
def demo():
    ensure_extension("hcs-ext-demo")
    import hcs_ext_demo.main as demo

    print(demo.description())


@test.command()
@cli.limit
@click.option("--sim-ret", required=False)
@click.argument("sim_err", required=False)
def env(sim_ret: int, sim_err, limit, **kwargs):
    import os

    if sim_ret:
        return f"return with sim_ret: {sim_ret}", int(sim_ret)

    if sim_err:
        raise Exception("simulated error: " + sim_err)

    return {k: v for k, v in os.environ.items() if k.lower().startswith("hcs_")}
