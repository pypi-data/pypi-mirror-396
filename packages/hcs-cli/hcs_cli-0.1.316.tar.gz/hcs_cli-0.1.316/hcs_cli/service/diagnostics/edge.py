"""
Copyright 2025 VMware Inc.
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

from hcs_core.sglib.client_util import hdc_service_client

log = logging.getLogger(__name__)

_client = hdc_service_client("admin")
base_context = "/v2/edge-deployments"


def diagnose_get_pods(id: str, org_id: str, verbose: bool):
    url = f"{base_context}/{id}/diagnose?org_id={org_id}"
    payload = dict()
    payload["diagnosticType"] = "GET_PODS"
    if verbose:
        log.info(f"get pods - payload: url: {url}, {payload}")
    return _client.post(url, payload, timeout=120)


def diagnose_url_accessibility(id: str, org_id: str, namespace: str, podname: str, url2check: str, verbose: bool):
    url = f"{base_context}/{id}/diagnose?org_id={org_id}"
    payload = dict()
    payload["diagnosticType"] = "URL_ACCESSIBILITY"
    payload["containerName"] = "app"
    payload["podName"] = podname
    payload["url"] = url2check
    payload["namespace"] = namespace

    if verbose:
        log.info(f"get url - url: {url}, {payload}")
    return _client.post(url, payload, timeout=120)
