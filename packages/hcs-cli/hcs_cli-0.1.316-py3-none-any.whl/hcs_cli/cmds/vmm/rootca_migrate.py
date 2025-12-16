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

import json
import logging
import os
import time
import uuid
from datetime import datetime
from enum import Enum

import click
import hcs_core.ctxp.data_util as data_util
import hcs_core.sglib.cli_options as cli

from hcs_cli.service import admin, inventory, org_service, vmhub, vmm
from hcs_cli.service.admin import VM
from hcs_cli.support.patch_util import calculate_patch

SLEEP_TIME_POWERON_VMS = 4
SLEEP_TIME_ON_PROLONGED_POWERON_VMS = 4
SLEEP_TIME_CERT_REFRESH_VMS = 1
SLEEP_TIME_MQTT_GET_UPDATE_VMS = 1
MIN_SUPPORTED_AGENT_VERSION = "24.4.0"

DEFAULT_BATCH_SIZE = 50
DEFAULT_FAILURE_THRESHOLD = 10

VMHUB_URL = "vmhub_url"
EDGE_FQDN_AUTO_GENERATED = "edge_fqdn_auto_generated"
EDGE_DEPLOYMENT_ID = "edge_deployment_id"
EDGE_MQTT_URL = "edge_mqtt_url"
REGIONAL_MQTT_URL = "regional_mqtt_url"
REGIONAL_MQTT_PORT = "443"
LOCATION = "location"
RUN_ID = "run_id"

allowed_providers = {"azure", "aws"}
supported_template_types = {"DEDICATED", "MULTI_SESSION"}

# Create a logger
logger = logging.getLogger("rootca_migrate")


@click.command(name="migrate", hidden="false")
@cli.org_id
@click.option("--file", type=click.Path(), required=False)
@click.argument("edge_ids", type=str, required=False)
@click.option("--template-id", type=str, required=False)
@click.option("--vm-ids", type=str, required=False)
# @click.argument("template_id", type=str, required=True)
# @click.argument("vm_ids", type=str, required=False)
@click.option("--batch_size", type=str, required=False)
@click.option("--failure_threshold", type=str, required=False)
@click.option("--poweredon_vms_only", type=bool, is_flag=True, required=False)
@click.option("--skip_active_session_vms", type=bool, is_flag=True, required=False)
@click.option("--run-id", type=str, required=False)
@click.option("--verbose", "--v", type=bool, is_flag=True, required=False)
def migrate(
    org: str,
    file: str,
    edge_ids: str,
    template_id: str,
    vm_ids: str,
    batch_size: str,
    failure_threshold: str,
    poweredon_vms_only: bool,
    skip_active_session_vms: bool,
    run_id: str,
    verbose: bool,
):
    """cert refresh on all vms in org/template"""

    global common_dict
    common_dict = dict()
    common_dict["BATCH_SIZE"] = DEFAULT_BATCH_SIZE
    common_dict["FAILURE_THRESHOLD"] = DEFAULT_FAILURE_THRESHOLD

    if run_id:
        common_dict["RUN_ID"] = run_id
    else:
        common_dict["RUN_ID"] = str(datetime.now().strftime("%m%d%Y%H%M%S"))

    if file:
        process_file(file, verbose)
        return
    elif org:
        process_command_input(
            org,
            edge_ids,
            template_id,
            vm_ids,
            batch_size,
            failure_threshold,
            poweredon_vms_only,
            skip_active_session_vms,
            verbose,
        )
    else:
        logger.error("--org or --file is required")
    return


def process_command_input(
    target_org_id: str,
    edge_ids: str,
    template_id: str,
    vm_ids: str,
    batch_size: str,
    failure_threshold: str,
    poweredon_vms_only: bool,
    skip_active_session_vms: bool,
    verbose: bool,
):
    logger.info("Starting RootCA migration:")
    logger.info(f"default timeout for API calls: {os.environ.get('HCS_TIMEOUT', 30)} seconds")
    if batch_size and int(batch_size) > 0:
        common_dict["BATCH_SIZE"] = int(batch_size)
    if failure_threshold and int(failure_threshold) > 0:
        common_dict["FAILURE_THRESHOLD"] = int(failure_threshold)

    # validate org id
    o = org_service.details.get(target_org_id)
    if not o:
        logger.error(f"Org {target_org_id} is invalid")
        return

    if vm_ids and not template_id:
        logger.error("--template-id is required if --vm-ids specified")
        return

    if edge_ids and template_id:
        logger.error("specify either --edge_ids or --template-id only")
        return

    if not edge_ids and not template_id:
        logger.error("Entire org migration is not supported. Specify either --edge_ids or --template-id")
        return

    logger.info("Rootca VMs Migration - Command Input:")
    logger.info(f"target_org_id: {target_org_id}")
    logger.info(f"edge_ids: {edge_ids}")
    logger.info(f"template_id: {template_id}")
    logger.info(f"vm_ids: {vm_ids}")
    logger.info(f"batch_size: {common_dict['BATCH_SIZE']}")
    logger.info(f"failure_threshold: {common_dict['FAILURE_THRESHOLD']}")
    logger.info(f"poweredon_vms_only: {poweredon_vms_only}")
    logger.info(f"skip_active_session_vms: {skip_active_session_vms}")
    logger.info(f"verbose: {verbose}")
    logger.info(f"run_id: {common_dict['RUN_ID']}\n")

    if edge_ids:
        migrate_edges(target_org_id, edge_ids, poweredon_vms_only, skip_active_session_vms, verbose)
    else:
        migrate_template_vms(target_org_id, template_id, vm_ids, poweredon_vms_only, skip_active_session_vms, verbose)
    logger.info("Ended RootCA migration")


def migrate_edges(target_org_id: str, edge_ids: str, poweredon_vms_only: bool, skip_active_session_vms: bool, verbose: bool):
    logger.info(f"Run Root CA Migration on: target_org_id = {target_org_id}, edge_ids = {edge_ids}")
    org = org_service.details.get(target_org_id)
    if not org:
        logger.error(f"Invalid org id {target_org_id}")
        return
    if not edge_ids:
        logger.error("edge_ids is not specified")
        return
    # edges = admin.edge.items(org_id=target_org_id, search="id $in " + edge_ids)
    edges = admin.edge.list(target_org_id, search="id $in " + edge_ids, size=100)
    if not edges or len(edges) == 0:
        logger.warn(f"No edges found with the org {target_org_id} and edge_ids: {edge_ids}")
        return
    for edge in edges:
        edge_id = edge["id"]
        if edge["providerLabel"].lower() not in allowed_providers:
            logger.warn(f"Pool migration is not supported on {edge.get('providerLabel')} provider edge {edge_id}, org: {target_org_id}")
            continue
        for template in admin.template.items(org_id=target_org_id, search="edgeDeploymentId $eq " + edge_id):
            template_id = template.get("id")
            # logger.info(f"RootCA migration on org_id: {target_org_id}, edge_id: {edge_id}, template_id: {template_id}")
            migrate_template_vms(target_org_id, template_id, None, poweredon_vms_only, skip_active_session_vms, verbose)


def migrate_template_vms(
    target_org_id: str,
    template_id: str,
    vm_ids: str,
    poweredon_vms_only: bool,
    skip_active_session_vms: bool,
    verbose: bool,
):
    logger.info("\n\n")
    logger.info(f"Stated RootCA Migration on org_id: {target_org_id}, template_id: {template_id}")
    # declare all global variables
    global template_key_dict
    template_key_dict = {}
    global edge_url_update_failed_vms
    edge_url_update_failed_vms = []
    global regional_mqtt_url_update_failed_vms
    regional_mqtt_url_update_failed_vms = []
    global prolonged_powering_on_vms
    prolonged_powering_on_vms = dict()
    global invalid_lcs_vms
    invalid_lcs_vms = dict()
    global un_avail_agent_status_vms
    un_avail_agent_status_vms = dict()
    global already_migrated_vms
    already_migrated_vms = []

    # get key details from template and edgeDeployment
    template = None
    try:
        template = admin.template.get(template_id, target_org_id)
        if not template:
            logger.warn(f"No template found with target_org_id: {target_org_id} and template_id: {template_id}")
            return
        if template.get("templateType") not in supported_template_types:
            warn_msg = "skipped execution on Template {0}. migration is not supported on {1} type".format(
                template["id"], template.get("templateType")
            )
            logger.warn(warn_msg)
            return
        template_key_dict = get_template_and_edge_details(template, target_org_id, verbose)
    except Exception as error:
        logger.error(error)
        return

    # disable powerPolicy on template
    power_policy_disabled_now = False

    # each batch - powerOn all the VMs and migrate each vm
    page_num = 0
    vms_count = 0
    update_power_policy_once_only = True
    while True:
        raw_list = inventory.vm.raw_list(template_id, org_id=target_org_id, vm_ids=vm_ids, size=common_dict["BATCH_SIZE"], page=page_num)
        page_num += 1
        total_pages = raw_list.get("totalPages")
        vms = raw_list.get("content")
        # tracks total VMs processed
        vms_count += len(vms)
        # disable powerPolicy only if VMs exists in the template or given vm_ids are valid
        if update_power_policy_once_only and len(vms) > 0:
            update_power_policy_once_only = False
            if not poweredon_vms_only:
                power_policy_disabled_now = disable_power_policy_on_template(template, verbose)
            else:
                logger.info(f"powerPolicy on template {template_id} is un-changed since migration is run on poweredon_vms_only")

        if verbose:
            log_vms_batch_details(raw_list)

        log_vms_info(vms, target_org_id, template_id, verbose)
        # HAIAgentVersion check on all VMs in the batch
        agent_version_chk_on_vms(vms, target_org_id, template_id, verbose)

        if poweredon_vms_only:
            remove_non_powered_on_vms(vms, target_org_id, template_id, verbose)
        else:
            power_on_vms(vms, target_org_id, template_id, verbose)

        if skip_active_session_vms:
            remove_active_session_vms(vms, target_org_id, template_id, verbose)

        # perform migration on all VMs in the batch
        try:
            # add all prolonged powering on VMs to the list to check powerState again
            vms.extend(prolonged_powering_on_vms.values())
            # perform migration
            if len(vms) > 0:
                perform_migration(template_key_dict, vms, target_org_id, template_id, page_num, verbose)
        except Exception as error:
            logger.error(error)
            if power_policy_disabled_now:
                enable_power_policy_on_template(template, verbose)
            else:
                logger.info(f"powerPolicy on template {template_id} was un-changed in the beginning, so not changed now.")
            return

        # check migration done on all batches in the template
        if page_num >= total_pages:
            break

    if len(prolonged_powering_on_vms) > 0:
        logger.warn(
            f"these {len(prolonged_powering_on_vms)} : {list(prolonged_powering_on_vms.keys())} vms are taking prolonged time to powerOn. making a final attempt to powerOn and migrate these vms."
        )
        logger.info(f"as a final attempt, sleep for {SLEEP_TIME_ON_PROLONGED_POWERON_VMS} more minutes for Vms to powerOn")
        time.sleep(60 * SLEEP_TIME_ON_PROLONGED_POWERON_VMS)
        try:
            # perform migration only on prolonged powerOn vms
            perform_migration(template_key_dict, prolonged_powering_on_vms.values(), target_org_id, template_id, page_num, verbose)
        except Exception as error:
            logger.error(error, exc_info=True)

    if len(prolonged_powering_on_vms) > 0:
        logger.warn(
            f"migration skipped on {len(prolonged_powering_on_vms)} vms since they are not poweringOn : {list(prolonged_powering_on_vms.keys())}"
        )
        send_hoc_event_skipped_vms(
            template_key_dict,
            prolonged_powering_on_vms.keys(),
            target_org_id,
            template_id,
            Action.SKIPPED_POWER_ON.name,
            HocStatus.FAILURE.value,
            "Attempt to power on vm failed for pro-longed time",
            verbose,
        )

    if len(invalid_lcs_vms) > 0:
        logger.warn(
            f"migration skipped on {len(invalid_lcs_vms)} vms since their lifecycleStatus is not PROVISIONED {json.dumps(invalid_lcs_vms)}"
        )
        send_hoc_event_skipped_vms(
            template_key_dict,
            invalid_lcs_vms.keys(),
            target_org_id,
            template_id,
            Action.SKIPPED_LIFECYCLE_NOT_PROVISIONED.name,
            HocStatus.FAILURE.value,
            "vm lifecycle status is not provisioned",
            verbose,
        )

    if len(un_avail_agent_status_vms) > 0:
        logger.warn(
            f"migration skipped on {len(un_avail_agent_status_vms)} vms since their agentStatus is not AVAILABLE {json.dumps(un_avail_agent_status_vms)}"
        )
        send_hoc_event_skipped_vms(
            template_key_dict,
            un_avail_agent_status_vms.keys(),
            target_org_id,
            template_id,
            Action.SKIPPED_UNAVAILABLE.name,
            HocStatus.FAILURE.value,
            "vm lifecycle status is not provisioned",
            verbose,
        )

    if len(already_migrated_vms) > 0:
        logger.warn(f"Skipped migration on already migrated VMs: {len(already_migrated_vms)}: {already_migrated_vms}")
        send_hoc_event_skipped_vms(
            template_key_dict,
            already_migrated_vms,
            target_org_id,
            template_id,
            Action.SKIPPED_ALREADY_MIGRATED.name,
            HocStatus.SUCCESS.value,
            "vm has been already migrated",
            verbose,
        )

    if power_policy_disabled_now:
        enable_power_policy_on_template(template, verbose)
    else:
        logger.info(f"powerPolicy on template {template_id} was un-changed in the beginning, so not changed now.")
    if vms_count == 0:
        if vm_ids:
            logger.warn(f"No VMs found with org_id: {target_org_id}, template_id: {template_id}, vm_ids: {vm_ids}")
        else:
            logger.warn(f"No VMs found with org_id: {target_org_id}, template_id: {template_id}")

    logger.info(f"Finished RootCA Migration on org_id: {target_org_id}, template_id: {template_id}")
    return


def send_hoc_event_skipped_vms(
    template_key_dict: dict,
    vms: dict,
    target_org_id: str,
    template_id: str,
    action: str,
    hoc_status: str,
    e: str,
    verbose: bool,
):
    logger.warn(f"sending hoc event for {len(vms)} vms: {vms}")
    for vm in vms:
        cmd_id = str(uuid.uuid4())
        vm_dict = inventory.get(template_id, vm, target_org_id)
        logger.warn(f"sending hoc event for vm: {vm_dict}")
        vmm.hoc_event.send_before_after_info(
            vm_dict,
            vm_dict,
            template_key_dict,
            action,
            cmd_id,
            "",
            "",
            action,
            hoc_status,
            e,
            verbose,
        )
        time.sleep(0.5)


def process_file(file: str, verbose: bool):
    logger.info("Starting RootCA migration:")
    logger.info(f"input file {file} specified. file input takes the precedence. processing the file now")
    logger.info(f"default timeout for API calls: {os.environ.get('HCS_TIMEOUT', 30)} seconds")
    if not os.path.isfile(file):
        logger.error(f"invalid file path {file}")
        return
    if os.path.getsize(file) <= 0:
        logger.error(f"no content in the file {file}")
        return

    data = None
    try:
        f = open(file)
        data = json.load(f)
    except Exception as error:
        logger.error(f"{file} file can't be parsed due to {error}")
        return

    logger.info(f"file content = {data}")
    if not data:
        logger.error("invalid file content")
        return

    migrate_config_dict = data.get("migrate_config")
    if not migrate_config_dict:
        logger.error(f"migrate_config field is missing in the file {file}")
        return

    migrate_edges_dict = data.get("migrate_edges")
    if not migrate_edges_dict:
        logger.error(f"migrate_edges field is missing in the file {file}")
        return

    batch_size = migrate_config_dict.get("batch_size")
    failure_threshold = migrate_config_dict.get("failure_threshold")
    poweredon_vms_only = migrate_config_dict.get("poweredon_vms_only")
    skip_active_session_vms = migrate_config_dict.get("skip_active_session_vms")
    verbose = migrate_config_dict.get("verbose")

    if batch_size and int(batch_size) > 0:
        common_dict["BATCH_SIZE"] = int(batch_size)
    if failure_threshold and int(failure_threshold) > 0:
        common_dict["FAILURE_THRESHOLD"] = int(failure_threshold)

    logger.info("\n")
    logger.info("Rootca VMs Migration - File Input:")
    logger.info(f"batch_size: {common_dict['BATCH_SIZE']}")
    logger.info(f"failure_threshold: {common_dict['FAILURE_THRESHOLD']}")
    logger.info(f"poweredon_vms_only: {poweredon_vms_only}")
    logger.info(f"skip_active_session_vms: {skip_active_session_vms}")
    logger.info(f"verbose: {verbose}")
    logger.info(f"run_id: {common_dict['RUN_ID']}\n")

    counter = 0
    for target_org_id in migrate_edges_dict.keys():
        counter += 1
        logger.info(f"migrate_edges:{counter}: target_org_id = {target_org_id}, edges = {migrate_edges_dict.get('target_org_id')}")

        if not target_org_id:
            logger.warn(f"migrate_edges:{counter}: target_org_id can't be blank.")
            continue

        o = org_service.details.get(target_org_id)
        if not o:
            logger.warn(f"migrate_edges:{counter}: target_org_id {target_org_id} is invalid")
            continue

        edge_id_list = migrate_edges_dict.get(target_org_id)
        edge_ids = None
        if edge_id_list:
            edge_ids = ",".join(edge_id_list)
        if not edge_ids or len(edge_ids) <= 0:
            logger.warn(f"migrate_edges:{counter}: edges are not specified for org {target_org_id}. skipped migration for this org")
            continue
        migrate_edges(target_org_id, edge_ids, poweredon_vms_only, skip_active_session_vms, verbose)
    logger.info("Ended RootCA migration")


def get_template_and_edge_details(template: dict, org_id: str, verbose: bool):
    vmhub_url = data_util.deep_get_attr(template, "hdc.vmHub.url", raise_on_not_found=False)
    edge_deployment_id = data_util.deep_get_attr(template, "edgeDeploymentId", raise_on_not_found=False)
    location = data_util.deep_get_attr(template, "location", raise_on_not_found=False)
    if not vmhub_url:
        err = "vmhub url is missing on template {0}. exited migration.".format(template["id"])
        raise ValueError(err)
    if not edge_deployment_id:
        err = "edgeDeploymentId is missing on template {0}. exited migration.".format(template["id"])
        raise ValueError(err)

    edge = admin.edge.get(edge_deployment_id, org_id)
    if not edge:
        err = "edgeDeployment object is not found. edgeId {0} and org {1}".format(edge_deployment_id, org_id)
        raise ValueError(err)
    if edge["providerLabel"].lower() not in allowed_providers:
        logger.warn(f"Pool migration is not supported on {edge.get('providerLabel')} provider edge {edge['id']}, org: {org_id}")
        return
    edge_mqtt_url = data_util.deep_get_attr(edge, "fqdn", raise_on_not_found=False)
    regional_mqtt_url = data_util.deep_get_attr(edge, "privateEndpointDetails.dnsRecord", raise_on_not_found=False)
    if not regional_mqtt_url:
        logger.info("regional mqtt url is not populated on edge deployment. So, getting the url from vmhub")
        vmhub_mqtt_dict = vmhub.mqtt.get_mqtt_info(vmhub_url, verbose)
        regional_mqtt_url = vmhub_mqtt_dict["mqttServerHost"]
        logger.info("regional mqtt url from vmhub is %s", regional_mqtt_url)

    d = dict()
    d[VMHUB_URL] = vmhub_url
    d[EDGE_DEPLOYMENT_ID] = edge_deployment_id
    d[LOCATION] = location
    d[EDGE_MQTT_URL] = edge_mqtt_url
    d[REGIONAL_MQTT_URL] = regional_mqtt_url
    d[EDGE_FQDN_AUTO_GENERATED] = edge.get("fqdnAutoGenerated")
    d[RUN_ID] = common_dict["RUN_ID"]
    if verbose:
        logger.info("Key details from template & edge: %s", d)
    return d


def enable_power_policy_on_template(template: dict, verbose: bool):
    return power_policy_on_template(template, True, verbose)


def disable_power_policy_on_template(template: dict, verbose: bool):
    return power_policy_on_template(template, False, verbose)


def power_policy_on_template(template: dict, enable: bool, verbose: bool):
    # enable/disable powerPolicy on template
    action = "Enable" if enable else "Disable"
    template_id = template["id"]
    target_org_id = template["orgId"]
    if verbose:
        logger.info(f"{action} powerPolicy on template {template_id}")
    try:
        data_util.deep_get_attr(template, "powerPolicy", raise_on_not_found=True)
        enabled = data_util.deep_get_attr(template, "powerPolicy.enabled", raise_on_not_found=True)
        if enabled is not None and enabled is False:
            logger.info(f"powerPolicy already disabled on template {template_id}")
            return False
    except:
        logger.info(f"powerPolicy doesn't exist on template {template_id}")
        return False

    allowed_fields = ["name", "description", "powerPolicy", "sparePolicy", "applicationProperties", "flags"]
    field = "powerPolicy.enabled=true" if enable else "powerPolicy.enabled=false"
    patch = calculate_patch(template, allowed_fields, [field])
    for i in range(3):
        try:
            admin.template.update(template_id, target_org_id, patch)
            admin.template.wait_for_ready(template_id, target_org_id, 60)
            break
        except Exception as ex:
            logger.warn(f"powerPolicy update on template failed due to {str(ex)}. will auto retry after 90 seconds sleep")
            time.sleep(90)

    logger.info(f"{action}d powerPolicy on template {template_id}")
    return True


def log_vms_info(vms: dict, target_org_id: str, template_id: str, verbose: bool):
    for vm in vms:
        log_vm_info(target_org_id, template_id, vm["id"])


def agent_version_chk_on_vms(vms: dict, target_org_id: str, template_id: str, verbose: bool):
    if len(vms) <= 0:
        return
    agent_version_chk_failed_vms = []
    for vm in vms:
        if not is_valid_agent_version(vm.get("haiAgentVersion")):
            agent_version_chk_failed_vms.append(vm)
            vmm.hoc_event.send(
                vm,
                template_key_dict,
                Action.AGENT_VERSION.name,
                vm["id"],
                None,
                None,
                None,
                HocStatus.FAILURE.value,
                None,
                verbose,
            )
    logger.warn("Skipped migration on un-supported agent version on VMs: %d", len(agent_version_chk_failed_vms))
    for vm in agent_version_chk_failed_vms:
        logger.warn("vm %s - hai version check failed haiAgentVersion: %s", vm.get("id"), vm.get("haiAgentVersion"))
    for vm in agent_version_chk_failed_vms:
        vms.remove(vm)


def remove_active_session_vms(vms: dict, target_org_id: str, template_id: str, verbose: bool):
    if len(vms) <= 0:
        return
    skipped_vms = []
    skipped_vm_ids = []
    for vm in vms:
        if int(vm["vmAssignedSessions"]) > 0:
            skipped_vms.append(vm)
            skipped_vm_ids.append(vm["id"])
    # remove active session vms from processing further
    for vm in skipped_vms:
        vms.remove(vm)
    if verbose:
        logger.warn(f"Skipped migration on active session VMs: {skipped_vm_ids}")


def remove_non_powered_on_vms(vms: dict, target_org_id: str, template_id: str, verbose: bool):
    if len(vms) <= 0:
        return
    non_powered_on_vms = []
    non_powered_on_vm_ids = []
    for vm in vms:
        if vm["powerState"] in ["PoweredOff", "PoweringOff", "Unknown"]:
            non_powered_on_vms.append(vm)
            non_powered_on_vm_ids.append(vm["id"])
    # remove non_powered_on vms from processing further
    for vm in non_powered_on_vms:
        vms.remove(vm)
    if verbose:
        logger.warn(f"Skipped migration on non-poweredOn VMs: {non_powered_on_vm_ids}")


def power_on_vms(vms: dict, target_org_id: str, template_id: str, verbose: bool):
    if len(vms) <= 0:
        return
    poweron_vms = []
    poweron_failed_vms = []
    unmanaged_vm_ids = []
    for vm in vms:
        if vm["powerState"] in ["PoweredOff", "Unknown"]:
            if vm.get("managementType") is not None and vm.get("managementType") == "MANUAL":
                unmanaged_vm_ids.append(vm["id"])
                continue
            vmObj = VM(target_org_id, template_id, vm["id"])
            try:
                vmObj.power_on()
                poweron_vms.append(vm)
            except Exception as e:
                poweron_failed_vms.append(vm)
                vmm.hoc_event.send(
                    vm,
                    template_key_dict,
                    Action.POWER_ON.name,
                    vm["id"],
                    None,
                    None,
                    None,
                    HocStatus.FAILURE.value,
                    e,
                    verbose,
                )

    if verbose:
        logger.info("vms being powered on: %d", len(poweron_vms))
        for vm in poweron_vms:
            logger.info("vm %s - powerState: %s", vm.get("id"), vm.get("powerState"))

        logger.info("vms failed to power on: %d", len(poweron_failed_vms))
        for vm in poweron_failed_vms:
            logger.warn(" vm %s - powerOn operation failed, powerState: %s", vm.get("id"), vm.get("powerState"))
        logger.warn(f"skipped power-on operation on unmanaged VMs: count {len(unmanaged_vm_ids)}: {unmanaged_vm_ids}")

    # sleep for vms to poweredOn
    if len(poweron_vms) > 0:
        logger.info("sleep for %d minutes to powerOn all poweredOff vms", SLEEP_TIME_POWERON_VMS)
        time.sleep(60 * SLEEP_TIME_POWERON_VMS)

    # remove failed vms from processing further
    for vm in poweron_failed_vms:
        vms.remove(vm)


def perform_migration(template_key_dict: dict, vms: dict, target_org_id: str, template_id: str, batch_num: int, verbose: bool):
    logger.info(f"Perform get MQTT & cert refresh calls on batch {batch_num}")
    migrate_vms = []
    vms_initial_state = dict()
    for vm in vms:
        # check powerState before running migration
        vm_pwr_chk = inventory.get(template_id, vm["id"], target_org_id)
        log_vm_info(target_org_id, template_id, vm["id"])
        if (
            vm.get("agentCertIssuedByCALabel") is not None
            and vm.get("agentCertIssuedByCALabel") == "omnissa"
            and vm.get("regionalMqttEndpoint") is not None
            and template_key_dict[REGIONAL_MQTT_URL] in vm.get("regionalMqttEndpoint")
            and ".omnissa.com" in vm.get("regionalMqttEndpoint")
            and (
                (EDGE_FQDN_AUTO_GENERATED in template_key_dict and template_key_dict.get(EDGE_FQDN_AUTO_GENERATED) is False)
                or (
                    vm.get("edgeMqttEndpoint") is not None
                    and template_key_dict[EDGE_MQTT_URL] in vm.get("edgeMqttEndpoint")
                    and ".omnissa.com" in vm.get("edgeMqttEndpoint")
                )
            )
        ):
            already_migrated_vms.append(vm["id"])
            continue
        if vm_pwr_chk["powerState"] != "PoweredOn":
            prolonged_powering_on_vms[vm["id"]] = vm_pwr_chk
            continue
        elif vm_pwr_chk["lifecycleStatus"] != "PROVISIONED":
            invalid_lcs_vms[vm["id"]] = vm_pwr_chk["lifecycleStatus"]
            continue
        elif vm_pwr_chk["agentStatus"] != "AVAILABLE":
            un_avail_agent_status_vms[vm["id"]] = vm_pwr_chk["agentStatus"]
            continue
        migrate_vms.append(vm)

    for vm in migrate_vms:
        # if vm is poweredOn and picked-up for migration, discard from prolonged list
        if prolonged_powering_on_vms.get(vm["id"]) is not None:
            prolonged_powering_on_vms.pop(vm["id"])
            logger.info(f"vm {vm['id']}: has powered-on, and moved from prolonged_powering_on_vms list to migrate_vms list")

    if len(migrate_vms) <= 0:
        return
    vm_cmd_id_dict = dict()
    for vm in migrate_vms:
        cmd_id = str(uuid.uuid4())
        vm_cmd_id_dict[vm["id"]] = cmd_id
        try:
            vmhub.mqtt.get(
                target_org_id,
                template_key_dict[EDGE_DEPLOYMENT_ID],
                template_id,
                vm["id"],
                cmd_id,
                template_key_dict[VMHUB_URL],
                verbose,
            )
        except Exception as error:
            u_vm = inventory.get(template_id, vm["id"], target_org_id)
            vms_initial_state[vm["id"]] = u_vm
            logger.error(f"{target_org_id}/{template_id}: failed to send get-mqtt-command to agent on vm {vm['id']} due to {str(error)}")
            """
            vmm.hoc_event.send(
                u_vm,
                template_key_dict,
                Action.GET.name,
                cmd_id,
                None,
                None,
                None,
                HocStatus.FAILURE.value,
                str(error),
                verbose,
            )
            """
        if verbose:
            log_vm_info(target_org_id, template_id, vm["id"])

    logger.info("sleep for 15 seconds - made initial get-mqtt calls on batch")
    time.sleep(15 * SLEEP_TIME_MQTT_GET_UPDATE_VMS)

    for vm in migrate_vms:
        u_vm = inventory.get(template_id, vm["id"], target_org_id)
        vms_initial_state[vm["id"]] = u_vm
        """
        vmm.hoc_event.send(
            u_vm,
            template_key_dict,
            Action.GET.name,
            vm_cmd_id_dict[vm["id"]],
            None,
            None,
            None,
            HocStatus.SUCCESS.value,
            None,
            verbose,
        )
        """
    counter = 0
    for vm in migrate_vms:
        counter += 1
        if counter % 20 == 0:
            time.sleep(0.5)

        try:
            vmhub.mqtt.refresh_cert(
                target_org_id,
                template_key_dict[EDGE_DEPLOYMENT_ID],
                template_id,
                vm["id"],
                template_key_dict[REGIONAL_MQTT_URL],
                REGIONAL_MQTT_PORT,
                template_key_dict[VMHUB_URL],
                verbose,
            )
            """
            cmd_id = str(uuid.uuid4())
            vmhub.mqtt.get(
                target_org_id,
                template_key_dict[EDGE_DEPLOYMENT_ID],
                template_id,
                vm["id"],
                cmd_id,
                template_key_dict[VMHUB_URL],
                verbose,
            )
            time.sleep(15 * SLEEP_TIME_MQTT_GET_UPDATE_VMS)
            u_vm = inventory.get(template_id, vm["id"], target_org_id)
            vmm.hoc_event.send(
                u_vm,
                template_key_dict,
                Action.GET_POST_CERT_REF.name,
                cmd_id,
                None,
                None,
                None,
                HocStatus.SUCCESS.value,
                None,
                verbose,
            )
            """
        except Exception as error:
            u_vm = inventory.get(template_id, vm["id"], target_org_id)
            vmm.hoc_event.send(
                u_vm,
                template_key_dict,
                Action.GET_POST_CERT_REF.name,
                cmd_id,
                None,
                None,
                None,
                HocStatus.FAILURE.value,
                str(error),
                verbose,
            )
        if verbose:
            log_vm_info(target_org_id, template_id, vm["id"])
    logger.info("sleeping for 60 seconds - done refresh_cert calls on batch")
    time.sleep(60 * SLEEP_TIME_CERT_REFRESH_VMS)

    for vm in migrate_vms:
        # invoke API to update edge mqtt url
        cmd_id = str(uuid.uuid4())
        try:
            force_edge = False
            vmhub.mqtt.update(
                target_org_id,
                template_key_dict[EDGE_DEPLOYMENT_ID],
                template_id,
                vm["id"],
                cmd_id,
                template_key_dict[EDGE_MQTT_URL],
                template_key_dict[VMHUB_URL],
                force_edge,
                verbose,
            )
        except Exception as error:
            u_vm = inventory.get(template_id, vm["id"], target_org_id)
            vmm.hoc_event.send_before_after_info(
                vms_initial_state.get(vm["id"]),
                u_vm,
                template_key_dict,
                Action.GET_POST_UPDATE.name,
                cmd_id,
                str(force_edge),
                str(REGIONAL_MQTT_PORT),
                "EDGE",
                HocStatus.FAILURE.value,
                str(error),
                verbose,
            )
    logger.info("sleeping for 20 seconds - done update-mqtt-url calls on batch")
    time.sleep(20 * SLEEP_TIME_MQTT_GET_UPDATE_VMS)

    vm_cmd_id_dict2 = dict()
    for vm in migrate_vms:
        cmd_id = str(uuid.uuid4())
        try:
            vm_cmd_id_dict2[vm["id"]] = cmd_id
            vmhub.mqtt.get(
                target_org_id,
                template_key_dict[EDGE_DEPLOYMENT_ID],
                template_id,
                vm["id"],
                cmd_id,
                template_key_dict[VMHUB_URL],
                verbose,
            )
            log_vm_info(target_org_id, template_id, vm["id"])
        except Exception:
            logger.error(f"get-mqtt(post update-mqtt) call failed for vm {vm['id']}")
    logger.info("sleeping for 15 seconds - done update & get mqtt-url calls on batch")
    time.sleep(15 * SLEEP_TIME_MQTT_GET_UPDATE_VMS)

    for vm in migrate_vms:
        u_vm = inventory.get(template_id, vm["id"], target_org_id)
        vmm.hoc_event.send_before_after_info(
            vms_initial_state.get(vm["id"]),
            u_vm,
            template_key_dict,
            Action.GET_POST_UPDATE.name,
            vm_cmd_id_dict2[vm["id"]],
            str(force_edge),
            str(REGIONAL_MQTT_PORT),
            "EDGE",
            HocStatus.SUCCESS.value,
            None,
            verbose,
        )

    for vm in migrate_vms:
        # check if migration succeeded
        vm = inventory.get(template_id, vm["id"], target_org_id)
        if vm.get("regionalMqttEndpoint") is None or template_key_dict[REGIONAL_MQTT_URL] not in vm.get("regionalMqttEndpoint"):
            regional_mqtt_url_update_failed_vms.append(vm)
        elif vm.get("edgeMqttEndpoint") is None or template_key_dict[EDGE_MQTT_URL] not in vm.get("edgeMqttEndpoint"):
            edge_url_update_failed_vms.append(vm)
        total_failed_vms = len(regional_mqtt_url_update_failed_vms) + len(edge_url_update_failed_vms)
        if total_failed_vms >= common_dict["FAILURE_THRESHOLD"]:
            err = f"Exiting the script execution. Failure threshold(limit: {common_dict['FAILURE_THRESHOLD']}) reached: {total_failed_vms}"
            logger.error(err)
            for f_vm in regional_mqtt_url_update_failed_vms:
                logger.warn(
                    f"vm {f_vm.get('id')} - regional mqtt url is not updated. regionalMqttEndpoint on vm is {f_vm.get('regionalMqttEndpoint')}"
                )
            for f_vm in edge_url_update_failed_vms:
                logger.warn(f"vm {f_vm.get('id')} - edge mqtt url not updated. edgeMqttEndpoint on vm is {f_vm.get('edgeMqttEndpoint')}")
            raise ValueError(err)


def log_vm_info(target_org_id: str, template_id: str, vm_id: str):
    vm = inventory.get(template_id, vm_id, target_org_id)
    logger.info(
        "vm %s - powerState: %s, haiAgentVersion: %s, agentStatus: %s, lifecycleStatus: %s, activeSessions: %s, regionalMqttEndpoint: %s, edgeMqttEndpoint: %s, agentCertIssuedByCALabel: %s",
        vm["id"],
        vm.get("powerState"),
        vm.get("haiAgentVersion"),
        vm.get("agentStatus"),
        vm.get("lifecycleStatus"),
        vm.get("vmAssignedSessions"),
        vm.get("regionalMqttEndpoint"),
        vm.get("edgeMqttEndpoint"),
        vm.get("agentCertIssuedByCALabel"),
    )


def is_valid_agent_version(agent_version: str):
    if agent_version is None or not agent_version:
        return False
    av_arr = agent_version.split(".")
    msav_arr = MIN_SUPPORTED_AGENT_VERSION.split(".")
    index = 0
    while index < len(av_arr) and index < len(msav_arr):
        if int(av_arr[index]) == int(msav_arr[index]):
            index += 1
            continue
        elif int(av_arr[index]) > int(msav_arr[index]):
            return True
        else:
            return False

    if len(av_arr) >= len(msav_arr):
        return True
    else:
        return False


def log_vms_batch_details(vms_response: dict):
    batch_num = vms_response.get("number")
    total_batches = vms_response.get("totalPages")
    total_vms = vms_response.get("totalElements")
    vms_on_current_batch = vms_response.get("numberOfElements")
    logger.info(
        f"batch information: batch_num: {batch_num + 1}, total_batches: {total_batches}, batch_size: {common_dict['BATCH_SIZE']},  total_vms: {total_vms}, vms_on_current_batch: {vms_on_current_batch}"
    )


class Action(Enum):
    GET = 1
    GET_POST_CERT_REF = 2
    GET_POST_UPDATE = 3
    POWER_ON = 4
    AGENT_VERSION = 5
    SKIPPED = 1000
    SKIPPED_ALREADY_MIGRATED = 1001
    SKIPPED_POWER_ON = 1002
    SKIPPED_LIFECYCLE_NOT_PROVISIONED = 1003
    SKIPPED_UNAVAILABLE = 1004


class HocStatus(str, Enum):
    SUCCESS = "su"
    FAILURE = "fl"
