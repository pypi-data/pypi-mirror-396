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
import os

import click
import hcs_core.sglib.cli_options as cli

from hcs_cli.service import inventory
from hcs_cli.service.admin import VM

# Create a logger
logger = logging.getLogger("restart_vms")


@click.command(name="restart_vms", hidden="false")
@cli.org_id
@click.option("--file", type=click.Path(), required=False)
@click.option("--template-id", type=str, required=False)
@click.option("--vm-ids", type=str, required=False)
@click.option("--dry-run", type=bool, is_flag=True, required=False)
def fix_vms(org: str, file: str, template_id: str, vm_ids: str, dry_run: bool):
    """fix vms"""

    if file:
        process_file(file, dry_run)
    else:
        target_org_id = org
        logger.info(f"command input: org_id: {target_org_id}, template_id: {template_id}, vm_ids: {vm_ids}")
        vms_arr = vm_ids.split(",")

        index = 0
        for vm_id in vms_arr:
            index += 1
            logger.info("\n")
            logger.info(f"{index}: get vm_id: {vm_id}")
            restart_vm(target_org_id, template_id, vm_id, dry_run)


def process_file(file: str, dry_run: bool):
    # file format:
    # <VM_ID>,<TEMPLATE_TYPE>,<TEMPLATE_ID>,<ORG_ID>
    logger.info(f"process file: {file}")
    if not os.path.isfile(file):
        logger.error(f"invalid file path {file}")
        return
    if os.path.getsize(file) <= 0:
        logger.error(f"no content in the file {file}")
        return

    with open(file, "r") as file:
        content = [line.strip() for line in file]

        index = 0
        for line in content:
            index += 1
            logger.info("\n")
            logger.info(f"{index:}: {line}")
            value_arr = line.split(",")

            vm_id = value_arr[0]
            template_id = value_arr[2]
            org_id = value_arr[3]
            restart_vm(org_id, template_id, vm_id, dry_run)


def restart_vm(org_id: str, template_id: str, vm_id: str, dry_run: bool):
    logger.info(f"org_id: {org_id}, template_id: {template_id}, vm_id: {vm_id}")
    vm = inventory.get(template_id, vm_id, org_id)
    # logger.info(f"vm: {vm}")
    if (
        vm["templateType"] != "DEDICATED"
        and vm["maxSessions"] == vm["vmFreeSessions"]
        and vm["agentStatus"] != "AVAILABLE"
        and vm["powerState"] == "PoweredOn"
    ):
        logger.info(f"vm: {vm_id} - eligible for restart")
        if dry_run:
            logger.info(f"DRY-RUN: powering on the vm: {vm_id}")
        else:
            logger.info(f"powering on the vm: {vm_id}")
            vmObj = VM(org_id, template_id, vm_id)
            vmObj.restart()
    else:
        logger.info(f"VM not eligible for restart: {vm_id}")
