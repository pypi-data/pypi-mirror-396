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

from hcs_core.sglib.client_util import hdc_service_client, wait_for_res_deleted, wait_for_res_status
from hcs_core.util.query_util import with_query

_client = hdc_service_client("lcm")


def delete(template_id: str, vm_id: str, org_id: str, force: bool = True):
    return _client.delete(f"/v1/capacity/{template_id}/vms/{vm_id}?org_id={org_id}&force={force}")


def get(template_id: str, vm_id: str, org_id: str):
    return _client.get(f"/v1/capacity/{template_id}/vms/{vm_id}?org_id={org_id}")


def put(template_id: str, vm_id: str, org_id: str, payload):
    return _client.put(f"/v1/capacity/{template_id}/vms/{vm_id}?org_id={org_id}", payload)


def get_pairing_info(template_id: str, vm_id: str, **kwargs):
    url = with_query(f"/v1/capacity/{template_id}/vms/{vm_id}/pairing-info", **kwargs)
    return _client.post(url)


def power_on(template_id: str, vm_id: str, org_id: str):
    return _client.post(f"/v1/capacity/{template_id}/vms/{vm_id}/powerOn?org_id={org_id}")


def power_off(template_id: str, vm_id: str, org_id: str):
    return _client.post(f"/v1/capacity/{template_id}/vms/{vm_id}/powerOff?org_id={org_id}")


def restart(template_id: str, vm_id: str, org_id: str):
    return _client.post(f"/v1/capacity/{template_id}/vms/{vm_id}/restart?org_id={org_id}")


def shutdown(template_id: str, vm_id: str, org_id: str):
    return _client.post(f"/v1/capacity/{template_id}/vms/{vm_id}/shutdown?org_id={org_id}")


def pair(template_id: str, vm_id: str, org_id: str):
    return _client.post(f"/v1/capacity/{template_id}/vms/{vm_id}/pair?org_id={org_id}")


def wait_for(
    template_id: str,
    vm_id: str,
    org_id: str,
    field: str,
    expected_values: list,
    timeout: str,
    unexpected_values: list = None,
    transition_values: list = None,
    fail_fast: bool = True,
):
    name = f"{template_id}/{vm_id}"

    # akka lcm vm does not have powerState field.
    # Should remove after HV2-189554 reach to prod.
    vm_info = get(template_id=template_id, vm_id=vm_id, org_id=org_id)
    if "powerState" not in vm_info:

        def fn_get():
            from hcs_cli.service import inventory

            return inventory.vm.get(template_id, vm_id, org_id)

    else:

        def fn_get():
            return get(template_id, vm_id, org_id)

    def fn_get_status(t):
        return t.get(field)

    if not expected_values:
        raise Exception("Invalid parameter. expected_values must not be empty.")

    if isinstance(expected_values, str):
        expected_values = [expected_values]

    _all_terminal_states = ["AVAILABLE", "ERROR", "DOMAIN_ERR"] if fail_fast else []
    if not unexpected_values:
        unexpected_values = list(set(_all_terminal_states) - set(expected_values))

    status_map = {"ready": expected_values, "error": unexpected_values, "transition": transition_values}
    return wait_for_res_status(resource_name=name, fn_get=fn_get, get_status=fn_get_status, status_map=status_map, timeout=timeout)


def wait_for_deleted(template_id: str, vm_id: str, org_id: str, timeout: str):

    name = f"{template_id}/{vm_id}"

    def fn_get():
        return get(template_id, vm_id, org_id)

    return wait_for_res_deleted(name, fn_get, timeout)
