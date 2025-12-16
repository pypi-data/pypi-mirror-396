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

from hcs_core.sglib.client_util import hdc_service_client

hoc_fields = dict()
hoc_fields["id"] = "i"
hoc_fields["type"] = "t"
hoc_fields["version"] = "v"
hoc_fields["source"] = "src"
hoc_fields["data"] = "d"
hoc_fields["utcTime"] = "utcTime"
hoc_fields["traceId"] = "trid"
hoc_fields["runId"] = "runid"
hoc_fields["action"] = "act"
hoc_fields["status"] = "s"
hoc_fields["orgId"] = "oid"
hoc_fields["edgeId"] = "eid"
hoc_fields["templateId"] = "tid"
hoc_fields["vmId"] = "vid"
hoc_fields["haiAgentVersion"] = "agtver"
hoc_fields["powerState"] = "agtps"
hoc_fields["agentStatus"] = "agtst"
hoc_fields["lifecycleStatus"] = "agtlcs"
hoc_fields["forceEdge"] = "forceedge"
hoc_fields["edgeMqttUrl"] = "emqtt"
hoc_fields["regionalMqttHost"] = "rmqtt"
hoc_fields["regionalMqttPort"] = "rmqttp"
hoc_fields["updateType"] = "cmdut"
hoc_fields["commandId"] = "cmdid"
hoc_fields["vmhubUrl"] = "vmhub"

hoc_fields["regionalMqttEndpointOnVm"] = "rmqttonvm"
hoc_fields["edgeMqttEndpointOnVm"] = "emqttonvm"
hoc_fields["agentCertIssuedByCALabel"] = "calblonvm"

hoc_fields["vmMigrated"] = "vmmig"
hoc_fields["moreInfo"] = "minfo"
hoc_fields["error"] = "err"


# Create a logger
logger = logging.getLogger("vmm.hoc_event")

_client = hdc_service_client("vm-manager")


def send(
    vm: dict,
    template_key_dict: dict,
    action: str,
    cmd_id: str,
    force_edge: str,
    regional_mqtt_port: str,
    update_type: str,
    status: str,
    error: str,
    verbose: bool,
):
    agent_mqtt_hoc_event = {
        hoc_fields["id"]: cmd_id,
        hoc_fields["type"]: "mqt:get:st",
        hoc_fields["version"]: "1",
        hoc_fields["source"]: "vmm",
    }

    data = {
        hoc_fields["utcTime"]: str(int(round(time.time() * 1000))),
        hoc_fields["orgId"]: vm.get("orgId"),
        hoc_fields["edgeId"]: template_key_dict.get("edge_deployment_id"),
        hoc_fields["templateId"]: vm.get("templateId"),
        hoc_fields["vmId"]: vm.get("id"),
        hoc_fields["haiAgentVersion"]: vm.get("haiAgentVersion"),
        hoc_fields["powerState"]: vm.get("powerState"),
        hoc_fields["agentStatus"]: vm.get("agentStatus"),
        hoc_fields["lifecycleStatus"]: vm.get("lifecycleStatus"),
        hoc_fields["edgeMqttUrl"]: template_key_dict.get("edge_mqtt_url"),
        hoc_fields["regionalMqttHost"]: template_key_dict.get("regional_mqtt_url"),
        hoc_fields["vmhubUrl"]: template_key_dict.get("vmhub_url"),
        hoc_fields["runId"]: template_key_dict.get("run_id"),
        hoc_fields["action"]: action,
        hoc_fields["status"]: status,
    }

    if vm.get("edgeMqttEndpoint"):
        data[hoc_fields["edgeMqttEndpointOnVm"]] = vm.get("edgeMqttEndpoint")
    if vm.get("regionalMqttEndpoint"):
        data[hoc_fields["regionalMqttEndpointOnVm"]] = vm.get("regionalMqttEndpoint")
    if vm.get("agentCertIssuedByCALabel"):
        data[hoc_fields["agentCertIssuedByCALabel"]] = vm.get("agentCertIssuedByCALabel")

    if regional_mqtt_port:
        data[hoc_fields["regionalMqttPort"]] = regional_mqtt_port
    if force_edge:
        data[hoc_fields["forceEdge"]] = force_edge
    if update_type:
        data[hoc_fields["updateType"]] = update_type
    if error:
        data[hoc_fields["error"]] = error

    agent_mqtt_hoc_event["d"] = data
    # create array of events
    event_array = []
    event_array.append(agent_mqtt_hoc_event)
    # create hoc events request
    events_request = {}
    events_request["events"] = event_array

    if verbose:
        logger.info(f"hoc events: {events_request}")
    try:
        ret = _client.post("/v1/agent/mqtt/hoc-events", events_request)
        if verbose:
            logger.info("Response POST /v1/agent/mqtt/hoc-events - {ret}")
        return ret
    except Exception as error:
        logger.error(f"failed to send hoc event due to {error}")


def send_before_after_info(
    vm_before: dict,
    vm: dict,
    template_key_dict: dict,
    action: str,
    cmd_id: str,
    force_edge: str,
    regional_mqtt_port: str,
    update_type: str,
    status: str,
    error: str,
    verbose: bool,
):
    event = {
        hoc_fields["id"]: str(int(round(time.time() * 1000))),
        hoc_fields["type"]: "rca:edge:vmmigst",
        hoc_fields["version"]: "1",
        hoc_fields["source"]: "vmm",
    }

    data = {
        hoc_fields["utcTime"]: int(round(time.time() * 1000)),
        hoc_fields["orgId"]: vm.get("orgId"),
        hoc_fields["edgeId"]: template_key_dict.get("edge_deployment_id"),
        hoc_fields["templateId"]: vm.get("templateId"),
        hoc_fields["vmId"]: vm.get("id"),
        hoc_fields["haiAgentVersion"]: vm.get("haiAgentVersion"),
        hoc_fields["powerState"]: (vm_before.get("powerState") or "") + " -> " + vm.get("powerState"),
        hoc_fields["agentStatus"]: (vm_before.get("agentStatus") or "") + " -> " + vm.get("agentStatus"),
        hoc_fields["agentCertIssuedByCALabel"]: (vm_before.get("agentCertIssuedByCALabel") or "")
        + " -> "
        + (vm.get("agentCertIssuedByCALabel") or ""),
        hoc_fields["lifecycleStatus"]: vm_before.get("lifecycleStatus") + " -> " + vm.get("lifecycleStatus"),
        hoc_fields["runId"]: template_key_dict.get("run_id"),
        hoc_fields["action"]: action,
        hoc_fields["status"]: status,
    }

    more_info = dict()
    more_info["edgeFQDNOnEdge"] = template_key_dict.get("edge_mqtt_url")
    more_info["regionalFQDNOnEdge"] = template_key_dict.get("regional_mqtt_url")

    if vm_before.get("edgeMqttEndpoint"):
        more_info["pre_mig_edgeMqttUrlOnVm"] = vm_before.get("edgeMqttEndpoint")
    if vm_before.get("regionalMqttEndpoint"):
        more_info["pre_mig_regionalMqttUrlOnVm"] = vm_before.get("regionalMqttEndpoint")
    if vm_before.get("agentCertIssuedByCALabel"):
        more_info["pre_mig_agentCertIssuedByCALabelOnVm"] = vm_before.get("agentCertIssuedByCALabel")

    if vm.get("edgeMqttEndpoint"):
        more_info["post_mig_edgeMqttUrlOnVm"] = vm.get("edgeMqttEndpoint")
    if vm.get("regionalMqttEndpoint"):
        more_info["post_mig_regionalMqttUrlOnVm"] = vm.get("regionalMqttEndpoint")
    if vm.get("agentCertIssuedByCALabel"):
        more_info["post_mig_agentCertIssuedByCALabelOnVm"] = vm.get("agentCertIssuedByCALabel")

    data[hoc_fields["moreInfo"]] = ", ".join(f"{key}: {value}" for key, value in more_info.items())

    migrated = "NONE"
    if (
        vm.get("edgeMqttEndpoint")
        and "omnissa." in vm.get("edgeMqttEndpoint")
        and vm.get("regionalMqttEndpoint")
        and "omnissa." in vm.get("regionalMqttEndpoint")
    ):
        migrated = "EDGE_REGIONAL"
    elif vm.get("edgeMqttEndpoint") and "omnissa." in vm.get("edgeMqttEndpoint"):
        migrated = "EDGE"
    elif vm.get("regionalMqttEndpoint") and "omnissa." in vm.get("regionalMqttEndpoint"):
        migrated = "REGIONAL"
    data[hoc_fields["vmMigrated"]] = migrated

    if regional_mqtt_port:
        data[hoc_fields["regionalMqttPort"]] = regional_mqtt_port
    if force_edge:
        data[hoc_fields["forceEdge"]] = force_edge
    if update_type:
        data[hoc_fields["updateType"]] = update_type
    if error:
        data[hoc_fields["error"]] = error

    event["d"] = data
    send_generic(event, verbose)


def send_generic(event: str, verbose: bool):
    if verbose:
        logger.info(f"hoc event: {event}")
    try:
        ret = _client.post("/v1/agent/mqtt/generic/hoc-events", event)
        return ret
    except Exception as error:
        logger.error(f"failed to send generic hoc event due to {error}")
