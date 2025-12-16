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
import hcs_core.sglib.cli_options as cli
import httpx

from hcs_cli.service import admin, edgehub, org_service, vmm

global common_dict
common_dict = dict()
allowed_providers = {"azure", "aws", "view"}

# allowed_edge_statuses = {"READY"}
# Create a logger
logger = logging.getLogger("edge_rotate_certs")


@click.command(name="edge_rotate_certs", hidden="false")
@cli.org_id
@click.argument("edge_ids", type=str, required=False)
@click.option("--run-id", type=str, required=False)
@click.option(
    "--ca-label",
    type=click.Choice(["legacy", "omnissa"], case_sensitive=True),
    default="legacy",
    show_default="legacy",
    required=True,
)
@click.option("--force", type=bool, is_flag=True, required=False)
@click.option("--verbose", "--v", type=bool, is_flag=True, required=False)
@click.option(
    "--provider",
    type=click.Choice(allowed_providers, case_sensitive=True),
    default=["azure"],
    show_default=["azure"],
    multiple=True,
    required=False,
)
@click.option(
    "--exclude_orgs",
    "--e",
    type=str,
    required=False,
    default="826f7674-9ebb-487c-ad43-365d6aca4427,91a4008d-14fc-4815-9f75-b693dc8deda8,70523c57-899e-4d57-a181-eb8e2d988aba",
)
def stats(org: str, edge_ids: str, run_id: str, ca_label: str, force: bool, verbose: bool, provider: list, exclude_orgs: str):
    """edge rotate certs"""
    target_org_id = org
    exclude_org_ids = [org_id.strip() for org_id in exclude_orgs.split(",")]

    if not target_org_id:
        return "--org is required", 1

    if target_org_id.upper() == "ALL" and edge_ids:
        return "edge_ids can't be specified when --org all is specified", 1

    logger.info(
        f"Starting Rotating Certs with ca_label: {ca_label} with force: {force} on Org: {target_org_id}, Edges: {edge_ids} for matching Providers: {provider}"
    )
    logger.info(f"Org Ids that will be excluded {exclude_org_ids}")
    logger.info("\n")
    logger.info(f"default timeout for API calls: {os.environ.get('HCS_TIMEOUT', 30)} seconds")

    common_dict["CA_LABEL"] = ca_label
    if run_id:
        common_dict["RUN_ID"] = run_id
    else:
        common_dict["RUN_ID"] = str(datetime.now().strftime("%m%d%Y%H%M%S"))
    logger.info(f"RUN_ID = {common_dict['RUN_ID']}")

    if target_org_id.upper() != "ALL":
        if target_org_id in exclude_org_ids:
            return f"Target org {target_org_id} is in exclude_orgs {exclude_org_ids}", 1
        try:
            org = org_service.details.get(target_org_id)
            if not org:
                logger.error(f"Invalid org id {target_org_id}")
                return
            rotate_certs_on_all_edges(org, edge_ids, force, provider, verbose)
        except httpx.HTTPStatusError as ex:
            logger.error(f"Http Status Code: {ex.response.status_code}")
            logger.error(f"Url: {ex.request.url}")
            logger.error(f"Response Content: {ex.response.text}")
            return
        except Exception as ex:
            logger.error(ex)
            return
    else:
        get_all_org_all_edge_stats(force, provider, exclude_org_ids, verbose)


def get_all_org_all_edge_stats(force: bool, desiredProviderTypes: list, exclude_org_ids: list, verbose: bool):
    logger.info(f"Rotating certs on all orgs except orgs specified in exclusion list {exclude_org_ids}")
    for org in org_service.details.items():
        target_org_id = (org["orgId"]).strip()
        if target_org_id in exclude_org_ids:
            logger.warn(f"Ignoring cert rotation on org {org} because it is in exclusion list {exclude_org_ids}")
            continue
        else:
            rotate_certs_on_all_edges(org, None, force, desiredProviderTypes, verbose)


def rotate_certs_on_all_edges(org: dict, edge_ids: str, force: bool, desiredProviderTypes: list, verbose: bool):
    target_org_id = org["orgId"]
    logger.info(f"Rotate certs on edges {edge_ids} of target org {target_org_id}")
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
            edge_providerLabel = edge["providerLabel"]
            logger.info(f"Found edge {edge_id}, name: {edge_name}, providerLabel: {edge_providerLabel}")
            if edge["providerLabel"].lower() not in allowed_providers:
                logger.warn(f"Cert rotation is not supported on {edge.get('providerLabel')} provider edge {edge_id}, org: {target_org_id}")
                continue
            if edge["providerLabel"].lower() not in desiredProviderTypes:
                logger.warn(
                    f"Ignore cert rotation on provider: {edge.get('providerLabel')}, edge: {edge_id}, org: {target_org_id} because it doesn't match desiredProviderType={desiredProviderTypes}"
                )
                continue
            """
            if edge["status"] not in allowed_edge_statuses:
                logger.warn(
                    f"Cert rotation is not supported on status {edge['status']} of edge {edge_id}, org: {target_org_id}"
                )
                continue
            """
            rotate_certs_on_edge(org, edge, force, verbose)
    except httpx.HTTPStatusError as ex:
        # logger.error(f"Http status code: {ex.response.status_code}")
        # logger.error(f"Url: {ex.request.url}")
        # logger.error(f"Response content: {ex.response.text}")
        if "ORG_LOCATION_NOT_FOUND" in ex.response.text:
            rotate_edge_certs = dict()
            rotate_edge_certs["org_id"] = org.get("orgId")
            rotate_edge_certs["org_name"] = org.get("orgName")
            rotate_edge_certs["edge_id"] = edge_id
            rotate_edge_certs["edge_name"] = edge_name
            rotate_edge_certs["info"] = "org/edge not configured. ORG_LOCATION_NOT_FOUND"
            logger.warn(rotate_edge_certs)
    except Exception as ex:
        logger.error(f"target_org_id: {target_org_id}, edge_id: {edge_id} - {ex}")
        rotate_edge_certs = dict()
        rotate_edge_certs["org_id"] = org.get("orgId")
        rotate_edge_certs["org_name"] = org.get("orgName")
        rotate_edge_certs["edge_id"] = edge_id
        rotate_edge_certs["edge_name"] = edge_name
        rotate_edge_certs["info"] = "org/edge not configured. " + str(ex)


def rotate_certs_on_edge(org: dict, edge: dict, force: bool, verbose: bool):
    rotate_edge_certs = dict()
    rotate_edge_certs["ca_label"] = common_dict["CA_LABEL"]
    rotate_edge_certs["run_id"] = common_dict["RUN_ID"]
    rotate_edge_certs["org_id"] = org.get("orgId")
    rotate_edge_certs["org_name"] = org.get("orgName")
    rotate_edge_certs["edge_id"] = edge.get("id")
    rotate_edge_certs["edge_name"] = edge.get("name")
    rotate_edge_certs["edge_status"] = edge.get("status")
    rotate_edge_certs["edge_providerlabel"] = edge.get("providerLabel")

    # get device id from edge
    if not edge.get("edgeGatewayLocation") or not edge.get("edgeGatewayLocation").get("deviceId"):
        msg = "edgeGatewayLocation/deviceId is missing on edge"
        logger.error(f"{msg} on org: {org.get('orgId')}, {edge.get('id')}")
        rotate_edge_certs["status"] = "fl"
        rotate_edge_certs["info"] = msg
        send_edge_rotate_certs_event(rotate_edge_certs, verbose)
        return
    device_id = edge.get("edgeGatewayLocation").get("deviceId")
    rotate_edge_certs["device_id"] = device_id
    # get edge-hub url from edge
    if not edge.get("hdc") or not edge.get("hdc").get("edgeHubUrl"):
        msg = "hdc/edgeHubUrl is missing on edge"
        logger.error(f"{msg} on org: {org.get('orgId')}, {edge.get('id')}")
        rotate_edge_certs["status"] = "fl"
        rotate_edge_certs["info"] = msg
        send_edge_rotate_certs_event(rotate_edge_certs, verbose)
        return
    edgehub_url = edge.get("hdc").get("edgeHubUrl")
    rotate_edge_certs["edgehub_url"] = edgehub_url
    # update edge config
    try:
        device = edgehub.edgecontroller.get(device_id, edgehub_url, verbose)
        if not device or not device.get("edgeTwinDeviceId"):
            msg = "device/edgeTwinDeviceId is missing on edgecontroller"
            logger.error(f"{msg} on org: {org.get('orgId')}, {edge.get('id')}")
            rotate_edge_certs["status"] = "fl"
            rotate_edge_certs["info"] = msg
            send_edge_rotate_certs_event(rotate_edge_certs, verbose)
            return
        edge_twin_id = device.get("edgeTwinDeviceId")

        if not force and is_cert_rotated(edge_twin_id, edgehub_url, "omnissa", verbose):
            rotate_edge_certs["status"] = "su"
            rotate_edge_certs["info"] = "SKIPPED; caLabel is already on omnissa"
            logger.info(rotate_edge_certs)
            send_edge_rotate_certs_event(rotate_edge_certs, verbose)
            return

        edgehub.edgecontroller.update_edge_config(device_id, common_dict["CA_LABEL"], edgehub_url, verbose)
        time.sleep(7)
        if not is_cert_rotated(edge_twin_id, edgehub_url, common_dict["CA_LABEL"], verbose):
            raise Exception("cert rotation didn't complete")
        rotate_edge_certs["status"] = "su"
        logger.info(rotate_edge_certs)
        send_edge_rotate_certs_event(rotate_edge_certs, verbose)
    except Exception as ex:
        rotate_edge_certs["status"] = "fl"
        rotate_edge_certs["info"] = str(ex)
        logger.error(f"error while checking if already cert_rotated on edge: {rotate_edge_certs}")
        send_edge_rotate_certs_event(rotate_edge_certs, verbose)


def is_cert_rotated(edge_twin_id: str, edgehub_url: str, target_ca_label: str, verbose: bool):
    edgetwin_dict = edgehub.edgetwin.get(edge_twin_id, edgehub_url, verbose)
    if (
        edgetwin_dict
        and edgetwin_dict.get("twinDesired")
        and edgetwin_dict.get("twinDesired").get("serviceConfig")
        and edgetwin_dict.get("twinDesired").get("serviceConfig").get("envProps")
    ):
        ca_label = edgetwin_dict.get("twinDesired").get("serviceConfig").get("envProps").get("caLabel")
        return ca_label and ca_label == target_ca_label
    return False


def send_edge_rotate_certs_event(edge_rotate_certs: dict, verbose: bool):
    edge_id = edge_rotate_certs.get("edge_id")
    event = {
        hoc_fields["id"]: edge_id,
        hoc_fields["type"]: "rca:edge:rtcert",
        hoc_fields["version"]: "1",
        hoc_fields["source"]: "vmm",
    }
    data = {
        hoc_fields["utcTime"]: int(round(time.time() * 1000)),
        hoc_fields["run_id"]: edge_rotate_certs["run_id"],
        hoc_fields["org_id"]: edge_rotate_certs.get("org_id"),
        hoc_fields["edge_id"]: edge_id,
        hoc_fields["edge_name"]: edge_rotate_certs.get("edge_name"),
        hoc_fields["device_id"]: edge_rotate_certs.get("device_id"),
        hoc_fields["edgehub_url"]: edge_rotate_certs.get("edgehub_url"),
        hoc_fields["ca_label"]: edge_rotate_certs.get("ca_label"),
        hoc_fields["status"]: edge_rotate_certs.get("status"),
        hoc_fields["edge_status"]: edge_rotate_certs.get("edge_status"),
        hoc_fields["provider_label"]: edge_rotate_certs.get("edge_providerlabel"),
    }
    if edge_rotate_certs.get("info"):
        data[hoc_fields["info"]] = edge_rotate_certs.get("info")
    event["d"] = data
    vmm.hoc_event.send_generic(event, verbose)


hoc_fields = dict()
hoc_fields["id"] = "i"
hoc_fields["type"] = "t"
hoc_fields["version"] = "v"
hoc_fields["source"] = "src"
hoc_fields["data"] = "d"

hoc_fields["utcTime"] = "utcTime"
hoc_fields["org_id"] = "oid"
hoc_fields["edge_id"] = "eid"
hoc_fields["edge_name"] = "ename"

hoc_fields["device_id"] = "did"
hoc_fields["edgehub_url"] = "ehurl"
hoc_fields["ca_label"] = "calbl"
hoc_fields["status"] = "s"
hoc_fields["info"] = "info"
hoc_fields["run_id"] = "runid"
hoc_fields["edge_status"] = "edgest"
hoc_fields["provider_label"] = "prlbl"
