"""
Copyright 2025 Omnissa Inc.
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

import click
import hcs_core.ctxp.data_util as data_util
import hcs_core.sglib.cli_options as cli
import httpx
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from hcs_core.ctxp import recent

from hcs_cli.service import admin, diagnostics

log = logging.getLogger(__name__)


@click.command("edge-getpods", hidden=True)
@click.argument("id", type=str, required=True)
@cli.org_id
@cli.verbose
def edge_getpods(id: str, org: str, verbose: bool):
    """Get edge connection string"""
    org_id = cli.get_org_id(org)
    id = recent.require("edge", id)
    ret = diagnostics.edge.diagnose_get_pods(id, org_id=org_id, verbose=verbose)
    if ret:
        return ret
    return "", 1


@click.command("edge-url-reachability", hidden=True)
@click.argument("id", type=str, required=True)
@click.option("--namespace", "-n", type=str, required=True, default="edge-namespace")
@click.option("--podname", "-p", type=str, required=True, default="mqtt-server-0")
@click.option("--url", "-u", type=str, required=True)
@cli.org_id
@cli.verbose
def edge_url_reachability(id: str, org: str, namespace: str, podname: str, url: str, verbose: bool):
    """Get edge connection string"""
    org_id = cli.get_org_id(org)
    id = recent.require("edge", id)
    ret = diagnostics.edge.diagnose_url_accessibility(
        id, org_id=org_id, namespace=namespace, podname=podname, url2check=url, verbose=verbose
    )
    if ret:
        return ret
    return "", 1


@click.command("copy-privatelink-dns-records", hidden=True)
@click.argument("id", type=str, required=True)
@cli.org_id
@cli.verbose
def edge_copy_privatelink_dns_records(id: str, org: str, verbose: bool):
    """Copy privatelink edge dns records"""
    org_id = cli.get_org_id(org)
    id = recent.require("edge", id)
    ret = admin.edge.copy_private_endpoint_dns_records(id, org_id=org_id, verbose=verbose)
    if ret:
        return ret
    return "", 1


@click.command("check-omnissa-privatelink-reachability", hidden=True)
@click.argument("id", type=str, required=True)
@cli.org_id
@cli.verbose
def check_omnissa_privatelink_dns_records(id: str, org: str, verbose: bool):
    """Check omnissa privatelink edge dns records"""
    org_id = cli.get_org_id(org)
    id = recent.require("edge", id)

    log.info(f"Check Omnissa regional mqtt url reachability for org: {org_id}, edge: {id}")
    podname = "mqtt-server-0"

    # 1. Get privatelink url
    myEdge = admin.edge.get(id=id, org_id=org_id)
    regional_mqtt_url = data_util.deep_get_attr(myEdge, "privateEndpointDetails.dnsRecord", raise_on_not_found=False)
    omnissa_regional_mqtt_url = "https://" + regional_mqtt_url.replace("vmware", "omnissa")
    log.info(f"regional mqtt: {regional_mqtt_url}, url to verify: {omnissa_regional_mqtt_url}")

    # 2. Copy the privatelink endpoint dns records
    ret = admin.edge.copy_private_endpoint_dns_records(id, org_id=org_id, verbose=verbose)
    if not ret:
        return "Failed to copy dns records in omnissa privatelink domain", 1

    # 3. Get pods and namespaces
    ret = diagnostics.edge.diagnose_get_pods(id, org_id=org_id, verbose=verbose)
    if not ret:
        return f"Failed to get pods in edge {id}", 1
    lines = ret.get("diagnosticData").split("\n")
    namespace = "edge-namespace"
    for line in lines:
        if "sg-uag-module" in line or "mqtt-server-0" in line or "infra-azure-module" in line or "token-generator" in line:
            lineTokens = line.split()
            log.info(lineTokens)
            namespace = lineTokens[0].strip()
            podname = lineTokens[1].strip()
            status = lineTokens[3].strip()
            log.info(f"Found pod {podname} in {status} status")
            if status == "Running":
                break
            else:
                continue
    if status != "Running":
        return "Failed to find running telemetry-server or mqtt-server pods"

    # 4. Finally verify url reachability
    log.info("Verify url:")
    log.info(f" edgeId: {id}")
    log.info(f" org_id: {org_id}")
    log.info(f" namespace: {namespace}")
    log.info(f" pod: {podname}")
    log.info(f" url: {omnissa_regional_mqtt_url}")

    try:
        exitcode60Found = False
        ret = diagnostics.edge.diagnose_url_accessibility(
            id,
            org_id=org_id,
            namespace=namespace,
            podname=podname,
            url2check=omnissa_regional_mqtt_url,
            verbose=verbose,
        )
        if ret:
            log.info(ret)
            if ret.get("diagnosticData").find("command terminated with exit code 60") > 0:
                exitcode60Found = True

    except httpx.HTTPStatusError as e:
        log.error(str(e))
        log.error(e.__cause__)
        log.error(e.response.content)

        if str(e.response.content).find("command terminated with exit code 60") > 0:
            exitcode60Found = True

    if exitcode60Found:
        log.info(f"url {omnissa_regional_mqtt_url} is reachable on edge: {id}.")
        return 0

    log.info(f"url {omnissa_regional_mqtt_url} is not reachable on edge: {id}.")
    return "", 1


@click.command("get-uag-certificate", hidden=True)
@click.argument("edge_id", type=str, required=True)
@cli.org_id
@cli.verbose
def edge_get_uag_mgmt_certificates(edge_id: str, org: str, verbose: bool):
    """Copy privatelink edge dns records"""
    org_id = cli.get_org_id(org)
    edge_id = recent.require("edge", edge_id)

    uags_dict = admin.uag.get_by_edge_deployment_id(edge_id, org_id)
    if uags_dict and uags_dict["content"] and uags_dict["content"][0]["id"]:
        uag_id = uags_dict["content"][0]["id"]
        gateways = uags_dict["content"][0]["gateways"]
        log.info(f"Get cert on all uag vms; org_id: {org_id}, edge_id: {edge_id}, uag_id: {uag_id}")

        for uag_gateway in gateways:
            log.info(f"Get cert on all uag vms; org_id: {org_id}, edge_id: {edge_id}, uag_id: {uag_id}, uag_gateway: {uag_gateway}")
            res = admin.uag.get_certs_on_uag_vm(id=uag_id, org_id=org_id, gateway_id=uag_gateway["id"], verbose=True)
            if verbose:
                log.info(f"Get cert response = {res}")

            if res and res.get("diagnosticData") and res.get("diagnosticData").startswith("Enable succeeded"):
                diagnosticData = res.get("diagnosticData")
                start_index = diagnosticData.find("-----BEGIN CERTIFICATE-----")
                if start_index == -1:
                    log.info("uag_id: No cert found (begin)")
                end_index = diagnosticData.find("-----END CERTIFICATE-----", start_index)

                if end_index == -1:
                    log.error("uag_id: No cert found (end)")

                cert = diagnosticData[start_index:end_index] + "-----END CERTIFICATE-----"
                if verbose:
                    log.info(f"cert on org_id: {org_id}, edge_id: {edge_id}, uag_id: {uag_id}, uag_gateway: {uag_gateway}:\n{cert}")
                cert_obj = x509.load_pem_x509_certificate(cert.encode("utf-8"), default_backend())
                if cert_obj:
                    log.info(f"  Subject: {cert_obj.subject}")
                    log.info(f"  Issuer: {cert_obj.issuer}")
                    log.info(f"  Serial Number: {cert_obj.serial_number}")
                    log.info(f"  Not valid before: {cert_obj.not_valid_before}")
                    log.info(f"  Not valid after: {cert_obj.not_valid_after}")
        return 0
    else:
        return "", 1
