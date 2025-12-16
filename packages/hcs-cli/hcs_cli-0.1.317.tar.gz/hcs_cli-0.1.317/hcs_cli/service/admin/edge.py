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

from ..edge import _client, base_context
from ..edge import create as create
from ..edge import delete as delete
from ..edge import get as get
from ..edge import get_connection_string as get_connection_string
from ..edge import items as items
from ..edge import list as list
from ..edge import safe_delete as safe_delete
from ..edge import wait_for as wait_for
from ..edge import wait_for_deleted as wait_for_deleted

log = logging.getLogger(__name__)


def copy_private_endpoint_dns_records(id: str, org_id: str, verbose: bool):
    url = f"{base_context}/{id}/copy-private-endpoint-dns-records?org_id={org_id}"
    if verbose:
        log.info(f"Copying private endpoint dns records {url}")
    return _client.post(url)


def rootca_migrate_private_endpoint_fqdn(id: str, org_id: str, verbose: bool):
    url = f"{base_context}/{id}/migrate-private-endpoint-dns-records?org_id={org_id}"
    if verbose:
        log.info(f"migrating private_endpoint_fqdn {url}")
    return _client.post(url)


def rootca_migrate_edge_fqdn(id: str, org_id: str, verbose: bool):
    url = f"{base_context}/{id}/fqdn/migration?org_id={org_id}"
    if verbose:
        log.info(f"migrating edge fqdn {url}")
    return _client.post(url)


def rootca_sync_uag_twin_config(id: str, org_id: str, verbose: bool):
    url = f"{base_context}/{id}/sync-twin-configuration?org_id={org_id}"
    payload = dict()
    payload["modules"] = ["UAG_MODULE"]
    if verbose:
        log.info(f"running uag twin sync config - url: {url}, payload: {payload}")
    return _client.post(url, payload)
