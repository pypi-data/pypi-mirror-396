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

from hcs_core.sglib import hcs_client

# Create a logger
logger = logging.getLogger("edgecontroller")


def _client(url: str):
    if not url.endswith("/"):
        url += "/"
    url += "edgecontroller"
    return hcs_client(url)


def get(device_id: str, edgehub_url: str, verbose: bool):
    ret = _client(edgehub_url).get("/v1/devices/" + device_id)
    return ret


def update_edge_config(device_id: str, ca_label: str, edgehub_url: str, verbose: bool):
    payload = {"envProps": {"caLabel": ca_label}, "mqttCertKeyTs": int(round(time.time() * 1000))}
    patch_url = "v1/devices/" + device_id + "/edgeconfig"
    if verbose:
        logger.info(f"patch url: {patch_url} and payload: {payload}")
    ret = _client(edgehub_url).patch(patch_url, payload)
    return ret
