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

import sys

import click
import hcs_core.plan as plan
import hcs_core.sglib.cli_options as cli

import hcs_cli.support.plan_util as plan_util


@click.command()
@click.option("--file", "-f", type=click.File("rt"), required=False, help="Specified the plan file.")
@click.option(
    "--sequential",
    "-s",
    is_flag=True,
    help="Process resources one by one, without parallism",
)
@click.option(
    "--log",
    "-l",
    is_flag=True,
    help="Output log stream instead of interactive view.",
)
@click.option(
    "--fail-fast",
    is_flag=True,
    help="Stop on the first error.",
)
@click.option(
    "--resource",
    "-r",
    type=str,
    required=False,
    help="Destroy a single resource, including all resources that depend on it.",
)
@click.option(
    "--only",
    "-1",
    is_flag=True,
    help="Used with --resource. Skip dependencies and destroy only the target resource.",
)
@cli.env
def destroy(file, resource: str, only: bool, sequential: bool, log: bool, fail_fast: bool, env: list):
    """Destroy a plan, delete associated resources."""
    if not resource:
        if only:
            raise click.UsageError("--only only works when deploying a single target specified by --resource.")

    cli.apply_env(env)

    data, additional_context = plan_util.load_plan(file)
    concurrency = 1 if sequential else 10

    interactive = sys.stdout.isatty() and not log

    job_view = None
    if interactive:
        from hcs_core.util.job_view import JobView

        job_view = JobView.create_async()
        plan.attach_job_view(job_view)

    try:
        return plan.destroy(
            data=data,
            fail_fast=fail_fast,
            target_resource_name=resource,
            include_dependencies=not only,
            concurrency=concurrency,
            additional_context=additional_context,
        )
    except (FileNotFoundError, plan.PlanException, plan.PluginException) as e:
        return str(e), 1
    finally:
        if job_view:
            job_view.close()
