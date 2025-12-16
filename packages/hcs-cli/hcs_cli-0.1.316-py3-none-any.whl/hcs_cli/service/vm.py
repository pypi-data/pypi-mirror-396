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

from typing import Iterator

from hcs_core.sglib.client_util import hdc_service_client, wait_for_res_deleted, wait_for_res_status
from hcs_core.util.query_util import PageRequest, with_query

_client = hdc_service_client("admin")


class VM:
    def __init__(self, org_id: str, template_id: str, vm_id: str):
        self.org_id = org_id
        self.template_id = template_id
        self.vm_id = vm_id
        self._url = f"/v2/templates/{self.template_id}/vms/{self.vm_id}?org_id={org_id}"

    @staticmethod
    def list(template_id: str, fn_filter=None, **kwargs) -> list:
        def _get_page(query_string):
            url = f"/v2/templates/{template_id}/vms?" + query_string
            return _client.get(url)

        return PageRequest(_get_page, fn_filter, **kwargs).get()

    @staticmethod
    def items(template_id: str, fn_filter=None, **kwargs) -> Iterator:
        def _get_page(query_string):
            url = f"/v2/templates/{template_id}/vms?" + query_string
            return _client.get(url)

        return PageRequest(_get_page, fn_filter, **kwargs).items()

    def get(self, **kwargs):
        url = with_query(self._url, **kwargs)
        return _client.get(url)

    def delete(self, **kwargs):
        url = with_query(self._url, **kwargs)
        return _client.delete(url)

    def pairing_info(self, **kwargs):
        url = with_query(f"/v2/templates/{self.template_id}/vms/{self.vm_id}/pairing-info?org_id={self.org_id}", **kwargs)
        return _client.post(url)

    def put(self, payload: dict, **kwargs):
        url = with_query(self._url, **kwargs)
        return _client.put(url, payload)

    def wait_for_agent(self, state: str = "AVAILABLE", timeout: str = "10m"):
        return self.wait_for(
            field="agentStatus",
            expected_values=[state],
            unexpected_values=["ERROR"],
            transition_values=["UNAVAILABLE"],
            timeout=timeout,
            fail_fast=True,
        )

    def wait_for_power_state(self, status: str, timeout: str = "2m"):
        all_power_states = ["PoweredOn", "PoweredOff", "PoweringOn", "PoweringOff", "Unknown"]
        if status == "PoweredOn":
            unexpected_values = ["PoweringOff"]
        elif status == "PoweredOff":
            unexpected_values = ["PoweringOn"]
        elif status == "PoweringOn":
            unexpected_values = []
        elif status == "PoweringOff":
            unexpected_values = []
        else:
            raise Exception("Unexpected power status: " + status)

        transition_values = [state for state in all_power_states if state not in unexpected_values]

        return self.wait_for(
            field="powerState",
            expected_values=[status],
            unexpected_values=unexpected_values,
            transition_values=transition_values,
            timeout=timeout,
            fail_fast=True,
        )

    def wait_for(
        self,
        field: str,
        expected_values: list,
        timeout: str,
        unexpected_values: list = None,
        transition_values: list = None,
        fail_fast: bool = True,
    ):
        name = f"{self.template_id}/{self.vm_id}"

        def fn_get():
            return self.get()

        def fn_get_status(t):
            return t.get(field)

        if not expected_values:
            raise Exception("Invalid parameter. expected_values must not be empty.")

        if isinstance(expected_values, str):
            expected_values = [expected_values]

        _all_terminal_states = ["AVAILABLE", "ERROR", "DOMAIN_ERR"]
        if not unexpected_values:
            unexpected_values = list(set(_all_terminal_states) - set(expected_values))

        status_map = {"ready": expected_values, "error": unexpected_values, "transition": transition_values}
        return wait_for_res_status(
            resource_name=name, fn_get=fn_get, get_status=fn_get_status, status_map=status_map, timeout=timeout, polling_interval=10
        )

    def wait_for_deleted(self, timeout: str):
        name = f"{self.template_id}/{self.vm_id}"

        return wait_for_res_deleted(name, self.get, timeout, polling_interval=10)

    def _perform_vm_action(self, action: str):
        url = self._url + "&action=" + action
        return _client.post(url)

    def power_on(self):
        return self._perform_vm_action("powerOn")

    def power_off(self):
        return self._perform_vm_action("powerOff")

    def restart(self):
        return self._perform_vm_action("restart")

    def shutdown(self):
        return self._perform_vm_action("shutdown")

    def resize(self):
        return self._perform_vm_action("resize")

    def rebuild(self):
        return self._perform_vm_action("rebuild")

    def pair(self):
        return self._perform_vm_action("pair")
