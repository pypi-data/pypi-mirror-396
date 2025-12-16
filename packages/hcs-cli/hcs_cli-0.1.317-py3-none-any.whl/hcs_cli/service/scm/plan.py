"""
Copyright 2023-2024 VMware Inc.
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

from hcs_core.sglib.client_util import default_crud, hdc_service_client, with_query

_client = hdc_service_client("scm")
_crud = default_crud(_client, "/v1/plan", "plan")

get = _crud.get
delete = _crud.delete


def list(org_id: str, **kwargs):
    url = with_query("/v1/plan", orgId=org_id, **kwargs)
    return _client.get(url)


def create(org_id: str, name: str, payload):
    url = f"/v1/plan/{name}?orgId={org_id}"
    return _client.put(url, payload)


def update(org_id: str, name: str, payload):
    url = f"/v1/plan/{name}?orgId={org_id}"
    return _client.post(url, json=payload)


def update_slot(org_id: str, name: str, slot: str, payload):
    url = f"/v1/plan/{name}/calendar/{slot}?orgId={org_id}"
    return _client.put(url, json=payload)


def delete_slot(org_id: str, name: str, slot: str):
    url = f"/v1/plan/{name}/calendar/{slot}?orgId={org_id}"
    return _client.delete(url)


def tasks(org_id: str, id: str, day: str, slot: str, limit: int, states: str):
    url = f"/v1/plan/{id}/tasks?orgId={org_id}&limit={limit}"
    if day:
        url += "&day=" + day
    if slot:
        url += "&slot=" + slot
    if states:
        url += "&states=" + states
    return _client.get(url)


def get_task(org_id: str, id: str, task_key: str):
    return _client.get(f"/v1/plan/{id}/tasks/{task_key}?orgId={org_id}")


def run(org_id: str, id: str, slot: str = None, payload=None, **kwargs):
    url = f"/v1/plan/{id}/run?orgId={org_id}"
    if slot:
        url += "&slot=" + slot
    return _client.post(url, json=payload)
