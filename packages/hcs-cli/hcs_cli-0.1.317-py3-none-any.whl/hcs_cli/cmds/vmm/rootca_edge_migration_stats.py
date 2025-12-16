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
import time
from datetime import datetime

import click
import hcs_core.ctxp.data_util as data_util
import hcs_core.sglib.cli_options as cli
import httpx

from hcs_cli.service import admin, ims, inventory, org_service, pki, vmm

MIN_SUPPORTED_AGENT_VERSION = "24.2.0"
global common_dict
common_dict = dict()

allowed_providers = {"azure", "aws"}
supported_template_types = {"DEDICATED", "MULTI_SESSION", "FLOATING"}

# Create a logger
logger = logging.getLogger("edge_stats")


@click.command(name="edge_stats", hidden="false")
@cli.org_id
@click.argument("edge_ids", type=str, required=False)
@click.option("--run-id", type=str, required=False)
@click.option("--verbose", "--v", type=bool, is_flag=True, required=False)
def stats(org: str, edge_ids: str, run_id: str, verbose: bool):
    """edge migration stats"""
    target_org_id = org
    if not target_org_id:
        return "--org is required", 1

    if target_org_id.upper() == "ALL" and edge_ids:
        return "edge_ids can't be specified when --org all is specified", 1

    logger.info("Started gather edge migration stats:")
    logger.info("\n")
    logger.info(f"default timeout for API calls: {os.environ.get('HCS_TIMEOUT', 30)} seconds")

    if run_id:
        common_dict["RUN_ID"] = run_id
    else:
        common_dict["RUN_ID"] = str(datetime.now().strftime("%m%d%Y%H%M%S"))

    logger.info("Command Inputs:")
    logger.info(f"Org = {target_org_id}")
    logger.info(f"EdgeIds = {edge_ids}")
    logger.info(f"verbose = {verbose}")
    logger.info(f"RUN_ID = {common_dict['RUN_ID']}")

    if target_org_id.upper() != "ALL":
        try:
            org = org_service.details.get(target_org_id)
            if not org:
                logger.error(f"Invalid org id {target_org_id}")
                return
            get_all_edges_stats(org, edge_ids, verbose)
        except httpx.HTTPStatusError as ex:
            logger.error(f"Http Status Code: {ex.response.status_code}")
            logger.error(f"Url: {ex.request.url}")
            logger.error(f"Response Content: {ex.response.text}")
            return
        except Exception as ex:
            logger.error(ex)
            return
    else:
        get_all_org_all_edge_stats(verbose)


def get_all_org_all_edge_stats(verbose: bool):
    org_count = 0
    for org in org_service.details.items():
        org_count += 1
        get_all_edges_stats(org, None, verbose)
    logger.info(f"Total orgs processed: {org_count}")


def get_all_edges_stats(org: dict, edge_ids: str, verbose: bool):
    target_org_id = org["orgId"]
    edge_id = None
    edge_name = None
    try:
        if edge_ids:
            edges = admin.edge.items(org_id=target_org_id, search="id $in " + edge_ids)
        else:
            edges = admin.edge.items(org_id=target_org_id)
        for edge in edges:
            edge_id = edge["id"]
            edge_name = edge["name"]
            if edge["providerLabel"].lower() not in allowed_providers:
                logger.warn(
                    f"Skipped edge stats calculation; rootca migration is not supported on {edge.get('providerLabel')} provider edge {edge_id}, org: {target_org_id}"
                )
                continue
            logger.info(f"collecting edge stats of org: {target_org_id} and edge_id: {edge_id}")
            edge_stats = get_edge_stats(edge, verbose)
            get_all_template_images_and_vms_stats(org, edge, edge_stats, verbose)
    except httpx.HTTPStatusError as ex:
        # logger.error(f"Http status code: {ex.response.status_code}")
        # logger.error(f"Url: {ex.request.url}")
        # logger.error(f"Response content: {ex.response.text}")
        if "ORG_LOCATION_NOT_FOUND" in ex.response.text:
            template_stats = dict()
            template_stats["org_id"] = org.get("orgId")
            template_stats["org_name"] = org.get("orgName")
            template_stats["edge_id"] = edge_id
            template_stats["edge_name"] = edge_name
            template_stats["error"] = "org/edge not configured. ORG_LOCATION_NOT_FOUND"
            logger.warn(template_stats)
            send_template_stats_event(template_stats, False, verbose)
    except Exception as ex:
        logger.error(f"target_org_id: {target_org_id}, edge_id: {edge_id} - {str(ex)}")
        template_stats = dict()
        template_stats["org_id"] = org.get("orgId")
        template_stats["org_name"] = org.get("orgName")
        template_stats["edge_id"] = edge_id
        template_stats["edge_name"] = edge_name
        template_stats["error"] = "org/edge not configured. " + str(ex)
        send_template_stats_event(template_stats, False, verbose)


def get_all_template_images_and_vms_stats(org: dict, edge: dict, edge_stats: dict, verbose: bool):
    all_template_stats = list()
    target_org_id = org["orgId"]
    edge_id = edge["id"]
    # provider_instance_id = edge["providerInstanceId"]
    logger.info(f"processing stats for org: {target_org_id}, edge: {edge_id}\n\n")
    template_count = 0
    for template in admin.template.items(org_id=target_org_id, search="edgeDeploymentId $eq " + edge_id):
        if template.get("templateType") not in supported_template_types:
            logger.warn(f"Not supported template type {template.get('templateType')}, so template {template.get('id')} is skipped")
            continue
        template_count += 1
        template_id = template.get("id")
        logger.info(f"{target_org_id}/{edge_id}: processing template {template.get('id')}")
        template_stats = dict()
        template_stats["org_id"] = org.get("orgId")
        template_stats["org_name"] = org.get("orgName")
        template_stats["edge_id"] = edge.get("id")
        template_stats["edge_fqdn_auto_generated"] = edge.get("fqdnAutoGenerated")
        template_stats["edge_name"] = edge.get("name")
        template_stats["template_id"] = template.get("id")
        template_stats["template_name"] = template.get("name")
        template_stats["template_type"] = template.get("templateType")
        all_template_stats.append(template_stats)
        image_reference = template.get("imageReference")
        if not image_reference:
            template_stats["error"] = "imageReference element is missing on template"
            logger.warn(f"{target_org_id}/{edge_id}/{template_id}: {template_stats['error']}")
            get_template_vms_stats(target_org_id, edge_id, template, template_stats, verbose)
            continue
        template_stats["image_reference"] = template.get("imageReference")
        stream_id = image_reference.get("streamId")
        version_id = image_reference.get("versionId")
        marker_id = image_reference.get("markerId")

        if not version_id:
            image = ims.images.get(stream_id, target_org_id)
            if not image:
                template_stats["error"] = "image document is missing"
                logger.warn(f"{target_org_id}/{edge_id}/{template_id}: {template_stats['error']}")
                get_template_vms_stats(target_org_id, edge_id, template, template_stats, verbose)
                continue
            markers = image.get("markers")
            if not markers:
                template_stats["error"] = "markers element list is missing on image"
                logger.warn(f"{target_org_id}/{edge_id}/{template_id}: {template_stats['error']}")
                get_template_vms_stats(target_org_id, edge_id, template, template_stats, verbose)
                continue
            for marker in markers:
                if marker.get("id") == marker_id:
                    version_id = marker.get("versionId")
                    break
                else:
                    continue

        template_stats["stream_id"] = stream_id
        template_stats["marker_id"] = marker_id
        template_stats["version_id"] = version_id
        logger.info(
            f"Image info: {target_org_id}/{edge_id}/{template_id}: stream_id: {template_stats['stream_id']}, marker_id: {template_stats['marker_id']}, version_id: {template_stats['version_id']}"
        )

        version = ims.version(stream_id, target_org_id).get(version_id)
        if not version:
            template_stats["error"] = "version document is missing"
            logger.warn(f"{target_org_id}/{edge_id}/{template_id}: {template_stats['error']}")
            get_template_vms_stats(target_org_id, edge_id, template, template_stats, verbose)
            continue
        options = version.get("options")
        if not options:
            template_stats["error"] = "options element list is missing on image"
            logger.warn(f"{target_org_id}/{edge_id}/{template_id}: {template_stats['error']}")
            get_template_vms_stats(target_org_id, edge_id, template, template_stats, verbose)
            continue
        agents = options.get("agents")
        is_using_custom_vm_image = False
        hai_agent_version = None
        is_valid_agent = False
        if agents:
            for agent in agents:
                if agent.get("name") == "HAI-Agent":
                    hai_agent_version = agent.get("agentVersion")
                    if is_valid_agent_version(agent.get("agentVersion")):
                        is_valid_agent = True
                        logger.info(f"{target_org_id}/{edge_id}/{template_id}: hai agent version {agent.get('agentVersion')} is VALID")
                    break
        else:
            is_using_custom_vm_image = True
            logger.warn(
                f"{target_org_id}/{edge_id}/{template_id}: template uses manually installed agent on the image. So check agent version on the template VMs"
            )

        template_stats["is_using_custom_vm_image"] = is_using_custom_vm_image
        template_stats["vm_image_agent_version"] = hai_agent_version
        template_stats["is_vm_image_on_valid_agent_version"] = is_valid_agent
        get_template_vms_stats(target_org_id, edge_id, template, template_stats, verbose)
    logger.info(f"{target_org_id}/{edge_id}: total templates in this edge: {template_count}")

    total_capacity = 0
    total_unsupportedvms = 0
    total_migrated_vms_count = 0
    total_non_migrated_vms_count = 0

    for template_stats in all_template_stats:
        logger.info(f"{template_stats}")
        if template_stats.get("total_vms"):
            total_capacity = total_capacity + int(template_stats.get("total_vms"))

        if template_stats.get("invalid_agent_version_vm_count"):
            total_unsupportedvms = total_unsupportedvms + int(template_stats.get("invalid_agent_version_vm_count"))

        if template_stats.get("migrated_vms_count"):
            total_migrated_vms_count = total_migrated_vms_count + int(template_stats.get("migrated_vms_count"))

        if template_stats.get("non_migrated_vms_count"):
            total_non_migrated_vms_count = total_non_migrated_vms_count + int(template_stats.get("non_migrated_vms_count"))
        send_template_stats_event(template_stats, True, verbose)

    # filter image versions across the pools of an edge
    unique_image_ids = set()
    unique_image_stats = list()
    for template_stats in all_template_stats:
        if not template_stats.get("stream_id"):
            continue
        # if not template_stats.get("version_id") and not template_stats.get("marker_id"):
        #    continue
        unique_image_id = (
            template_stats.get("stream_id") + " - " + str(template_stats.get("marker_id")) + " - " + str(template_stats.get("version_id"))
        )
        if unique_image_id not in unique_image_ids:
            unique_image_ids.add(unique_image_id)
            unique_image_stats.append(template_stats)

    logger.info(f"Unique images: {target_org_id}/{edge_id}: {unique_image_ids}")
    if len(unique_image_ids) > 0:
        logger.info(f"{target_org_id}/{edge_id}/{template_id}: unique image ids: {unique_image_ids}\n")
        logger.info("Sending all images' stats events:")
        for template_stats in unique_image_stats:
            send_image_stats_event(template_stats, verbose)

    edge_migration_eligible = True
    are_all_templates_vms_migrated = True
    for template_stats in all_template_stats:
        if (
            "is_using_custom_vm_image" in template_stats.keys()
            and template_stats.get("is_using_custom_vm_image") is False
            and "is_vm_image_on_valid_agent_version" in template_stats.keys()
            and template_stats.get("is_vm_image_on_valid_agent_version") is False
        ) or ("all_vms_on_valid_agent_version" in template_stats.keys() and template_stats.get("all_vms_on_valid_agent_version") is False):
            edge_migration_eligible = False

        if "are_all_vms_migrated" in template_stats.keys() and template_stats.get("are_all_vms_migrated") is False:
            are_all_templates_vms_migrated = False

    logger.info(
        f"Edge Migration Eligibility: org_id: {org.get('orgId')}, edge_id: {edge.get('id')}, edge_migration_eligible: {edge_migration_eligible}"
    )
    send_edge_stats_event(
        org.get("orgId"),
        edge.get("id"),
        template_count,
        total_capacity,
        total_unsupportedvms,
        total_migrated_vms_count,
        total_non_migrated_vms_count,
        edge_migration_eligible,
        are_all_templates_vms_migrated,
        edge_stats,
        verbose,
    )


def get_edge_stats(edge: dict, verbose: bool):
    edge_stats = dict()
    edge_stats["edge_status"] = edge.get("status")
    edge_stats["provider_label"] = edge.get("providerLabel")
    edge_stats["regional_mqtt_url"] = data_util.deep_get_attr(edge, "privateEndpointDetails.dnsRecord", raise_on_not_found=False)
    edge_stats["edge_mqtt_url"] = data_util.deep_get_attr(edge, "fqdn", raise_on_not_found=False)
    edge_stats["is_fqdn_auto_generated"] = edge.get("fqdnAutoGenerated")
    # get edge ca_label set on PKI service
    edge_ca_label_on_pki = None
    edge_calabel = pki.certificate.get_edge_calabel(edge["id"], edge["orgId"], verbose)
    if edge_calabel:
        edge_ca_label_on_pki = edge_calabel.get("caLabel")
    edge_stats["edge_ca_label_on_pki"] = edge_ca_label_on_pki

    regional_mqtt_url = data_util.deep_get_attr(edge, "privateEndpointDetails.dnsRecord", raise_on_not_found=False)
    edge_fqdn_auto_generated = edge.get("fqdnAutoGenerated")
    edge_mqtt_url = data_util.deep_get_attr(edge, "fqdn", raise_on_not_found=False)
    edge_migrated = False
    if (
        (edge_fqdn_auto_generated is False or (edge_fqdn_auto_generated is True and edge_mqtt_url and ".omnissa." in edge_mqtt_url))
        and edge_ca_label_on_pki
        and edge_ca_label_on_pki == "omnissa"
        and ((not regional_mqtt_url) or (regional_mqtt_url and ".omnissa." in regional_mqtt_url))
    ):
        edge_migrated = True
    edge_stats["edge_migrated"] = edge_migrated
    return edge_stats


def get_template_vms_stats(target_org_id: str, edge_id: str, template: dict, template_stats: dict, verbose: bool):
    invalid_agent_version_vms = list()
    migrated_vms = list()
    non_migrated_vms = list()
    page_num = 0
    BATCH_SIZE = 100
    vm_count = 0
    while True:
        raw_list = inventory.vm.raw_list(template["id"], org_id=target_org_id, vm_ids=None, size=BATCH_SIZE, page=page_num)
        page_num += 1
        total_pages = raw_list.get("totalPages")
        vms = raw_list.get("content")
        for vm in vms:
            vm_count += 1
            if not is_valid_agent_version(vm.get("haiAgentVersion")):
                invalid_agent_version_vms.append(vm["id"])

            if (
                vm.get("agentCertIssuedByCALabel") is not None
                and vm.get("agentCertIssuedByCALabel") == "omnissa"
                and vm.get("regionalMqttEndpoint") is not None
                and ".omnissa." in vm.get("regionalMqttEndpoint")
                and (
                    ("edge_fqdn_auto_generated" in template_stats and template_stats["edge_fqdn_auto_generated"] is False)
                    or (vm.get("edgeMqttEndpoint") is not None and ".omnissa." in vm.get("edgeMqttEndpoint"))
                )
            ):
                migrated_vms.append(vm["id"])
            else:
                non_migrated_vms.append(vm["id"])
        # check migration done on all batches in the template
        if page_num >= total_pages:
            break

    # derive agent version stats of all VMs
    all_vms_on_valid_agent_version = False
    if len(invalid_agent_version_vms) == 0:
        all_vms_on_valid_agent_version = True
    template_stats["all_vms_on_valid_agent_version"] = all_vms_on_valid_agent_version
    template_stats["invalid_agent_version_vm_count"] = len(invalid_agent_version_vms)
    template_stats["invalid_agent_version_vms"] = invalid_agent_version_vms

    # derive migrated/non-migrated VMs stats
    are_all_vms_migrated = False
    if len(non_migrated_vms) == 0:
        are_all_vms_migrated = True
    template_stats["are_all_vms_migrated"] = are_all_vms_migrated
    template_stats["migrated_vms_count"] = len(migrated_vms)
    template_stats["migrated_vms"] = migrated_vms
    template_stats["non_migrated_vms_count"] = len(non_migrated_vms)
    template_stats["non_migrated_vms"] = non_migrated_vms
    template_stats["total_vms"] = vm_count


# SUPPORTING FUNCTIONS #########################################################


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


def send_edge_stats_event(
    org_id: str,
    edge_id: str,
    total_pools: int,
    total_capacity: int,
    total_unsupportedvms: int,
    total_migrated_vms_count: int,
    total_non_migrated_vms_count: int,
    edge_migration_eligible: bool,
    are_all_templates_vms_migrated: bool,
    edge_stats: dict,
    verbose: bool,
):
    event = {
        hoc_fields["id"]: org_id + ":" + edge_id,
        hoc_fields["type"]: "rca:edge:st",
        hoc_fields["version"]: "1",
        hoc_fields["source"]: "vmm",
    }
    data = {
        hoc_fields["utcTime"]: int(round(time.time() * 1000)),
        hoc_fields["run_id"]: common_dict["RUN_ID"],
        hoc_fields["orgId"]: org_id,
        hoc_fields["edgeId"]: edge_id,
        hoc_fields["status"]: "su",
        hoc_fields["edge_migration_eligible"]: edge_migration_eligible,
        hoc_fields["are_all_templates_vms_migrated"]: are_all_templates_vms_migrated,
        hoc_fields["edge_status"]: edge_stats.get("edge_status"),
        hoc_fields["provider_label"]: edge_stats.get("provider_label"),
        hoc_fields["regional_mqtt_url"]: edge_stats.get("regional_mqtt_url"),
        hoc_fields["edge_mqtt_url"]: edge_stats.get("edge_mqtt_url"),
        hoc_fields["is_fqdn_auto_generated"]: edge_stats.get("is_fqdn_auto_generated"),
        hoc_fields["total_pools"]: total_pools,
        hoc_fields["total_capacity"]: total_capacity,
        hoc_fields["total_unsupportedvms"]: total_unsupportedvms,
        hoc_fields["total_migratedvms"]: total_migrated_vms_count,
        hoc_fields["total_nonmigratedvms"]: total_non_migrated_vms_count,
        hoc_fields["pct_error_vms"]: (int((total_unsupportedvms / total_capacity) * 100) if total_capacity > 0 else 0),
        hoc_fields["edge_migrated"]: edge_stats["edge_migrated"],
    }
    if edge_stats.get("edge_ca_label_on_pki"):
        data[hoc_fields["edge_ca_label_on_pki"]] = edge_stats.get("edge_ca_label_on_pki")
    event["d"] = data
    vmm.hoc_event.send_generic(event, verbose)


def send_image_stats_event(template_stats: dict, verbose: bool):
    stream_id = template_stats.get("stream_id")
    version_id = template_stats.get("version_id")
    event = {
        hoc_fields["id"]: stream_id + ":" + version_id,
        hoc_fields["type"]: "rca:edge:imgst",
        hoc_fields["version"]: "1",
        hoc_fields["source"]: "vmm",
    }

    img_agent_version = ""
    if template_stats.get("vm_image_agent_version"):
        img_agent_version = template_stats.get("vm_image_agent_version")
    data = {
        hoc_fields["utcTime"]: int(round(time.time() * 1000)),
        hoc_fields["run_id"]: common_dict["RUN_ID"],
        hoc_fields["orgId"]: template_stats.get("org_id"),
        hoc_fields["edgeId"]: template_stats.get("edge_id"),
        hoc_fields["stream_id"]: template_stats.get("stream_id"),
        hoc_fields["version_id"]: template_stats.get("version_id"),
        hoc_fields["is_using_custom_vm_image"]: template_stats.get("is_using_custom_vm_image"),
        hoc_fields["vm_image_agent_version"]: img_agent_version,
        hoc_fields["is_vm_image_on_valid_agent_version"]: template_stats.get("is_vm_image_on_valid_agent_version"),
    }

    if template_stats.get("marker_id"):
        data[hoc_fields["marker_id"]] = template_stats.get("marker_id")

    event["d"] = data
    vmm.hoc_event.send_generic(event, verbose)


def send_template_stats_event(template_stats: dict, success: bool, verbose: bool):
    av_inv_vm_ids_str = None
    invalid_agent_version_vms = template_stats.get("invalid_agent_version_vms")
    if invalid_agent_version_vms and len(invalid_agent_version_vms) > 0:
        av_inv_vm_ids_str = ",".join(invalid_agent_version_vms)

    # check this since on incomplete setup of orgs/edges, template(s) don't exist.
    unique_event_id = template_stats.get("template_id")
    if not unique_event_id:
        unique_event_id = str(int(round(time.time() * 1000)))
    event = {
        hoc_fields["id"]: unique_event_id,
        hoc_fields["type"]: "rca:edge:poolst",
        hoc_fields["version"]: "1",
        hoc_fields["source"]: "vmm",
    }
    trim_migrated_vms = template_stats.get("migrated_vms")
    if trim_migrated_vms and len(trim_migrated_vms) > 50:
        trim_migrated_vms = list()
    trim_non_migrated_vms = template_stats.get("non_migrated_vms")
    if trim_non_migrated_vms and len(trim_non_migrated_vms) > 50:
        trim_non_migrated_vms = list()
    data = {
        hoc_fields["utcTime"]: int(round(time.time() * 1000)),
        hoc_fields["run_id"]: common_dict["RUN_ID"],
        hoc_fields["orgId"]: template_stats.get("org_id"),
        hoc_fields["edgeId"]: template_stats.get("edge_id"),
        hoc_fields["templateId"]: template_stats.get("template_id"),
        hoc_fields["templateName"]: template_stats.get("template_name"),
        hoc_fields["templateType"]: template_stats.get("template_type"),
        hoc_fields["error"]: template_stats.get("error"),
        hoc_fields["all_vms_on_valid_agent_version"]: template_stats.get("all_vms_on_valid_agent_version"),
        hoc_fields["invalid_agent_version_vm_count"]: template_stats.get("invalid_agent_version_vm_count"),
        hoc_fields["stream_id"]: template_stats.get("stream_id"),
        hoc_fields["marker_id"]: template_stats.get("marker_id"),
        hoc_fields["version_id"]: template_stats.get("version_id"),
        hoc_fields["is_using_custom_vm_image"]: template_stats.get("is_using_custom_vm_image"),
        hoc_fields["vm_image_agent_version"]: template_stats.get("vm_image_agent_version"),
        hoc_fields["is_vm_image_on_valid_agent_version"]: template_stats.get("is_vm_image_on_valid_agent_version"),
        hoc_fields["are_all_vms_migrated"]: template_stats.get("are_all_vms_migrated"),
        hoc_fields["migrated_vms"]: trim_migrated_vms,
        hoc_fields["migrated_vms_count"]: template_stats.get("migrated_vms_count"),
        hoc_fields["non_migrated_vms"]: trim_non_migrated_vms,
        hoc_fields["non_migrated_vms_count"]: template_stats.get("non_migrated_vms_count"),
        hoc_fields["total_vms"]: template_stats.get("total_vms"),
    }
    if success:
        data[hoc_fields["status"]] = "su"
    else:
        data[hoc_fields["status"]] = "fl"
    if av_inv_vm_ids_str:
        data[hoc_fields["av_inv_vm_ids"]] = av_inv_vm_ids_str
    event["d"] = data
    vmm.hoc_event.send_generic(event, verbose)


hoc_fields = dict()
# common HOC fields
hoc_fields["id"] = "i"
hoc_fields["type"] = "t"
hoc_fields["version"] = "v"
hoc_fields["source"] = "src"
hoc_fields["data"] = "d"

hoc_fields["utcTime"] = "utcTime"
hoc_fields["orgId"] = "oid"

# template stats HOC fields
hoc_fields["edgeId"] = "eid"
hoc_fields["templateId"] = "tid"
hoc_fields["templateName"] = "tname"
hoc_fields["templateType"] = "ttype"
hoc_fields["status"] = "s"
hoc_fields["all_vms_on_valid_agent_version"] = "vmsavvalid"
hoc_fields["invalid_agent_version_vm_count"] = "vmsavinvcnt"
hoc_fields["av_inv_vm_ids"] = "vmsavinv"
hoc_fields["are_all_vms_migrated"] = "areallvmsmig"
hoc_fields["migrated_vms"] = "migvms"
hoc_fields["migrated_vms_count"] = "migvmscount"
hoc_fields["non_migrated_vms"] = "nonmigvms"
hoc_fields["non_migrated_vms_count"] = "nonmigvmscount"
hoc_fields["total_vms"] = "ttlvms"

# image stats HOC fields
hoc_fields["imageId"] = "iid"
hoc_fields["imageName"] = "iname"
hoc_fields["imageStatus"] = "is"
hoc_fields["is_image_published"] = "ipub"
hoc_fields["is_agent_manually_installed"] = "ami"
hoc_fields["has_valid_agent_version"] = "vav"

hoc_fields["is_using_custom_vm_image"] = "custvmimg"
hoc_fields["vm_image_agent_version"] = "vmimgav"
hoc_fields["is_vm_image_on_valid_agent_version"] = "vmimgavvalid"

hoc_fields["stream_id"] = "stmid"
hoc_fields["marker_id"] = "mkrid"
hoc_fields["version_id"] = "verid"
hoc_fields["error"] = "err"
hoc_fields["run_id"] = "runid"

# edge related stats
hoc_fields["edge_migration_eligible"] = "edgemigelgbl"
hoc_fields["are_all_templates_vms_migrated"] = "arealltmptsvmsmig"
hoc_fields["edge_status"] = "es"
hoc_fields["provider_label"] = "epl"
hoc_fields["regional_mqtt_url"] = "ergnlmqtturl"
hoc_fields["edge_mqtt_url"] = "emqtturl"
hoc_fields["edge_ca_label_on_pki"] = "ecalblpki"
hoc_fields["is_fqdn_auto_generated"] = "fqdnautogen"
hoc_fields["total_pools"] = "ttlpools"
hoc_fields["total_capacity"] = "ttlcap"
hoc_fields["total_unsupportedvms"] = "total_unsupportedvms"
hoc_fields["total_migratedvms"] = "total_migratedvms"
hoc_fields["total_nonmigratedvms"] = "total_nonmigratedvms"
hoc_fields["pct_error_vms"] = "pct_error_vms"
hoc_fields["edge_migrated"] = "edgemig"
