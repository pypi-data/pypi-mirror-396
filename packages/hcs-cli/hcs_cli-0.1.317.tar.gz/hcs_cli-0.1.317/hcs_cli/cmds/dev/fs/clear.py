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

import hcs_cli.cmds.dev.util.log as log
from hcs_cli.cmds.dev.fs.helper.util import validate_fs_kubeconfig, validate_fs_profile
from hcs_cli.cmds.dev.fs.init import _resolve_bundled_file_path
from hcs_cli.support.exec_util import run_cli


@click.command()
@click.option(
    "--only-default",
    is_flag=True,
    default=False,
    help="Delete only default deployments created by fs init. Otherwise, all pools, edges, providers will be deleted.",
)
def clear(only_default: bool, **kwargs):
    """Clear deployments on feature stack."""

    validate_fs_profile()
    validate_fs_kubeconfig()

    # Cleanup default zero deployments
    run_cli("hcs lcm template delete -y --force zero-floating-1")
    run_cli("hcs lcm template delete -y --force zero-dedicated-1")
    run_cli("hcs lcm template delete -y --force zero-multisession-1")

    if not only_default:
        _delete_all()

    akka_plan_path = _resolve_bundled_file_path("provided_files/akka.plan.yml")
    azure_plan_path = _resolve_bundled_file_path("provided_files/azure.plan.yml")
    azsim_plan_path = _resolve_bundled_file_path("provided_files/azsim.plan.yml")
    run_cli("hcs plan destroy -f " + akka_plan_path, raise_on_error=False)
    run_cli("hcs plan destroy -f " + azure_plan_path, raise_on_error=False)
    run_cli("hcs plan destroy -f " + azsim_plan_path, raise_on_error=False)

    if not only_default:
        log.info("Second run for resiliency...")
        _delete_all()
    log.good("Done")


def _delete_all():
    # all lcm templates
    lcm_template_ids = run_cli("hcs lcm template list --ids", output_json=True)
    for tid in lcm_template_ids:
        run_cli("hcs lcm template delete -y --force " + tid)
    # all pools
    pool_ids = run_cli("hcs pool list --ids", output_json=True)
    for pid in pool_ids:
        run_cli("hcs pool delete -y --delete-templates " + pid)
    # wait for template deletion, from admin perspective
    for tid in lcm_template_ids:
        run_cli("hcs template delete -y --force --wait 5m " + tid)
    # all images
    image_ids = run_cli("hcs ims list --ids", output_json=True)
    for iid in image_ids:
        run_cli("hcs ims delete " + iid)
    # all image gold patterns
    gold_pattern_ids = run_cli("hcs ims gold-pattern list --ids", output_json=True)
    for gid in gold_pattern_ids:
        run_cli("hcs ims gold-pattern delete -y " + gid)
    # all edges
    edge_ids = run_cli("hcs edge list --ids", output_json=True)
    for eid in edge_ids:
        run_cli("hcs edge delete -y --force --delete-all --field id,status " + eid)
    # wait for edge deletion
    for eid in edge_ids:
        run_cli("hcs edge delete -y --force --delete-all -w 5m " + eid)
    # all sites
    site_ids = run_cli("hcs site list --ids", output_json=True)
    for sid in site_ids:
        run_cli("hcs site delete -y " + sid)
    # all providers
    provider_ids = run_cli("hcs provider list --ids", output_json=True)
    for pid in provider_ids:
        run_cli("hcs provider delete -y " + pid, raise_on_error=False)
