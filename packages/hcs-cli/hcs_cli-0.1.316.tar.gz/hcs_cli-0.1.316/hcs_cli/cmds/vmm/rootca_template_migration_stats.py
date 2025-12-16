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
from datetime import datetime

import click
import hcs_core.ctxp.data_util as data_util

from hcs_cli.service import admin, inventory, vmhub

# Create a logger
logger = logging.getLogger("rootca_template_migration_stats")

BATCH_SIZE = 50

VMHUB_URL = "vmhub_url"
EDGE_DEPLOYMENT_ID = "edge_deployment_id"
EDGE_MQTT_URL = "edge_mqtt_url"
REGIONAL_MQTT_URL = "regional_mqtt_url"
REGIONAL_MQTT_PORT = "443"
LOCATION = "location"
RUN_ID = "run_id"


@click.command(name="template_stats", hidden="false")
@click.argument("target_org_id", type=str, required=True)
@click.argument("template_id", type=str, required=True)
@click.option("--verbose", "--v", type=bool, is_flag=True, required=False)
def template_migration_stats(target_org_id: str, template_id: str, verbose: bool):
    """cert refresh on all vms in org/template"""
    logger.info("Template Stats of org: %s, template: %s\n", target_org_id, template_id)

    # declare all global variables
    global template_key_dict
    template_key_dict = {}
    global vms_powerstate
    vms_powerstate = dict()

    global vms_powered_on
    vms_powered_on = []
    global vms_powered_off
    vms_powered_off = []
    global vms_powering_on
    vms_powering_on = []
    global vms_powering_off
    vms_powering_off = []
    global vms_unknown
    vms_unknown = []

    global vms_agentversion
    vms_agentversion = dict()
    global vms_lcs
    vms_lcs = dict()
    global vms_agentstatus
    vms_agentstatus = dict()
    global vms_migrated
    vms_migrated = []
    global vms_notmigrated
    vms_notmigrated = []

    # get key details from template
    template = None
    try:
        template = admin.template.get(template_id, target_org_id)
        template_key_dict = get_template_and_edge_details(template, target_org_id, verbose)
        logger.info("Template Key Details:")
        for key in template_key_dict.keys():
            logger.info(f"{key} : {template_key_dict[key]}")
    except Exception as error:
        logger.error(error)
        return

    page_num = 0
    while True:
        try:
            raw_list = inventory.vm.raw_list(template_id, org_id=target_org_id, vm_ids=None, size=BATCH_SIZE, page=page_num)
            page_num += 1
            total_pages = raw_list.get("totalPages")
            vms = raw_list.get("content")
            get_migration_stats(vms, target_org_id, template_id, page_num, verbose)
        except Exception as error:
            logger.error(error)
        # check migration done on all batches in the template
        if page_num >= total_pages:
            break
    print_stats(verbose)
    return


def get_migration_stats(vms: dict, target_org_id: str, template_id: str, batch_num: int, verbose: bool):
    for vm in vms:
        # check powerState before running migration
        vm_id = vm["id"]
        ps = vm["powerState"]

        if ps == "PoweredOn":
            vms_powered_on.append(vm_id)
        elif ps == "PoweringOn":
            vms_powering_on.append(vm_id)
        elif ps == "PoweredOff":
            vms_powered_off.append(vm_id)
        elif ps == "PoweringOff":
            vms_powering_off.append(vm_id)
        else:
            vms_unknown.append(vm_id)

        list = vms_powerstate.get(ps)
        if not list:
            vm_ids = []
            vms_powerstate[ps] = vm_ids
        vms_powerstate.get(ps).append(vm_id)

        av = vm["haiAgentVersion"]
        list = vms_agentversion.get(av)
        if not list:
            vm_ids = []
            vms_agentversion[av] = vm_ids
        vms_agentversion.get(av).append(vm_id)

        lcs = vm["lifecycleStatus"]
        list = vms_lcs.get(lcs)
        if not list:
            vm_ids = []
            vms_lcs[lcs] = vm_ids
        vms_lcs.get(lcs).append(vm_id)

        vas = vm["agentStatus"]
        list = vms_agentstatus.get(vas)
        if not list:
            vm_ids = []
            vms_agentstatus[vas] = vm_ids
        vms_agentstatus.get(vas).append(vm_id)

        if (
            vm.get("regionalMqttEndpoint") is not None
            and template_key_dict[REGIONAL_MQTT_URL] in vm.get("regionalMqttEndpoint")
            and "omnissa" in vm.get("regionalMqttEndpoint")
            and vm.get("edgeMqttEndpoint") is not None
            and template_key_dict[EDGE_MQTT_URL] in vm.get("edgeMqttEndpoint")
            and "omnissa" in vm.get("edgeMqttEndpoint")
        ):
            vms_migrated.append(vm_id)
        else:
            vms_notmigrated.append(vm_id)


def print_stats(verbose: bool):
    logger.info("\n")
    logger.info("Template VM counts on power state:")
    logger.info(f"PoweredOn VMs: {len(vms_powered_on)}")
    logger.info(f"PoweredOff VMs: {len(vms_powered_off)}")
    logger.info(f"PoweringOn VMs: {len(vms_powering_on)}")
    logger.info(f"PoweringOff VMs: {len(vms_powering_off)}")
    logger.info(f"Unknown VMs: {len(vms_unknown)}")
    if verbose:
        logger.info("\n")
        logger.info(f"PoweredOn VMs: {vms_powered_on}")
        logger.info(f"PoweredOff VMs: {vms_powered_off}")
        logger.info(f"PoweringOn VMs: {vms_powering_on}")
        logger.info(f"PoweringOff VMs: {vms_powering_off}")
        logger.info(f"Unknown VMs: {vms_unknown}")

    logger.info("\n")
    logger.info("Template VM counts on agent version:")
    for key in vms_agentversion.keys():
        logger.info(f"{key} : {len(vms_agentversion[key])}")
    if verbose:
        logger.info("\n")
        for key in vms_agentversion.keys():
            logger.info(f"{key} : {vms_agentversion[key]}")

    logger.info("\n")
    logger.info("Template VM counts on lifecycle status:")
    for key in vms_lcs.keys():
        logger.info(f"{key} : {len(vms_lcs[key])}")
    if verbose:
        logger.info("\n")
        for key in vms_lcs.keys():
            logger.info(f"{key} : {vms_lcs[key]}")

    logger.info("\n")
    logger.info("Template VM counts on agent status:")
    for key in vms_agentstatus.keys():
        logger.info(f"{key} : {len(vms_agentstatus[key])}")
    if verbose:
        logger.info("\n")
        for key in vms_agentstatus.keys():
            logger.info(f"{key} : {vms_agentstatus[key]}")

    logger.info("\n")
    logger.info("Template VM counts on migration status:")
    logger.info(f"migrated VMs: {len(vms_migrated)}")
    logger.info(f"not migrated VMs: {len(vms_notmigrated)}")
    if verbose:
        logger.info("\n")
        logger.info(f"migrated VMs: {vms_migrated}")
        logger.info(f"not migrated VMs: {vms_notmigrated}")


def get_template_and_edge_details(template: dict, org_id: str, verbose: bool):
    if not template:
        err = "Template object not found. exited migration."
        raise ValueError(err)
    if template.get("templateType") == "FLOATING":
        err = "Template {0} is {1} type. migration is not supported.".format(template["id"], template.get("templateType"))
        raise ValueError(err)

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
    if edge.get("providerLabel").lower() != "azure":
        err = f"Skipped pool stats calculation; rootca migration is not supported on {edge.get('providerLabel')} provider edge {edge['id']}, org: {org_id}"
        raise ValueError(err)
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
    d[RUN_ID] = str(datetime.now().strftime("%m%d%Y%H%M%S"))
    return d
