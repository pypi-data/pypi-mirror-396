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

from ..uag import _client, base_context
from ..uag import create as create
from ..uag import delete as delete
from ..uag import get as get
from ..uag import get_by_edge_deployment_id as get_by_edge_deployment_id
from ..uag import get_by_provider_id as get_by_provider_id
from ..uag import list as list
from ..uag import safe_delete as safe_delete
from ..uag import wait_for_deleted as wait_for_deleted
from ..uag import wait_for_ready as wait_for_ready

log = logging.getLogger(__name__)


def refresh_certs_on_uag_vms(id: str, org_id: str, diagnostic_type: str, verbose: bool):
    payload = {"diagnosticType": diagnostic_type, "applyToAllGatewayVMs": True}
    url = f"{base_context}/{id}/diagnose?org_id={org_id}"
    if verbose:
        log.info(f"cert refresh on all uag vms; url: {url}, payload: {payload}")
    return _client.post(url, payload, timeout=120.0)


def get_certs_on_uag_vm(id: str, org_id: str, gateway_id: str, verbose: bool):
    payload = {"diagnosticType": "GET_PKI_CERTIFICATE", "gatewayId": gateway_id}
    url = f"{base_context}/{id}/diagnose?org_id={org_id}"
    if verbose:
        log.info(f"Get cert refresh on uag vm; url: {url}, payload: {payload}")
    return _client.post(url, payload, timeout=120.0)
