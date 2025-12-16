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

import json
import time

import click
from hcs_core.ctxp import CtxpException
from hcs_core.sglib.client_util import default_crud, hdc_service_client
from hcs_core.util.query_util import PageRequest, with_query

_client = hdc_service_client("lcm")
_crud = default_crud(_client, "/v1/templates", "template")

get = _crud.get


def list_all(name: str = None, **kwargs):
    def _get_page(query_string):
        url = "/v1/templates?" + query_string
        return _client.get(url)

    ret = PageRequest(_get_page, **kwargs).get()
    if name:
        # filter_fn = lambda t : t.name.find(name) >= 0
        def filter_fn(t):
            return t.name.find(name) >= 0

        ret = list(filter(filter_fn, ret))
    return ret


def delete(id: str, org_id: str, force: bool):
    resp = _client.delete(f"/v1/templates/{id}?org_id={org_id}&force={force}")
    return _convert_resp(resp)


def create(template: dict):
    url = "/v1/templates"
    url += "/" + template["providerType"].lower()
    return _client.post(url=url, json=template)


def update(template: dict):
    url = "/v1/templates"
    # workaround for AKKA
    if template["providerType"] == "AKKA":
        pass
    else:
        url += "/" + template["providerType"].lower()
    return _client.post(url=url, json=template)


def wait(
    id: str,
    org_id: str,
    timeout_seconds: int,
    expected_status: list = ["READY"],
    exclude_status: list = ["ERROR"],
    interval_seconds: int = 10,
):
    start = int(time.time())
    ever_printed = False
    while True:
        t = get(id, org_id)
        if not t:
            msg = f"Error waiting for template {id}. Not found."
            raise CtxpException(msg)

        status = t.status

        if status in expected_status:
            if ever_printed:
                click.secho(
                    f"Waiting for template {id}. Expected={expected_status}, current={status}, counter={t.counter}. Complete.",
                    fg="bright_black",
                    err=True,
                )
            return t

        if status in exclude_status:
            msg = f"Error waiting for template {id}. Current status is {status}, which is not expected."
            raise CtxpException(msg)

        now = int(time.time())
        elapsed = now - start

        if elapsed > timeout_seconds:
            msg = f"Timeout waiting for template {id}. Current: {status}, expect: {expected_status}"
            raise CtxpException(msg)

        delay = min(interval_seconds, timeout_seconds - elapsed)
        time.sleep(delay)

        click.secho(
            f"Waiting for template {id}. Expected={expected_status}, current={status}, counter={t.counter} ...", fg="bright_black", err=True
        )
        ever_printed = True


def _convert_resp(resp):
    if resp:
        resp.read()
        try:
            json.loads(resp.text)
        except:
            return resp.text


wait_for_deleted = _crud.wait_for_deleted


def retry(id: str, org_id: str):
    url = f"/v1/templates/{id}/retry?org_id={org_id}"
    return _client.post(url)


def cancel(id: str, org_id: str):
    url = f"/v1/templates/{id}/cancel?org_id={org_id}"
    return _client.post(url)


def ensure_capacity(id: str, org_id: str, target_capacity: int, protection_time: str):
    url = f"/v1/capacity/{id}?org_id={org_id}"
    payload = {"targetCapacity": target_capacity, "protectionTime": protection_time}

    return _client.post(url, payload)


def health(id: str, org_id: str, **kwargs):
    url = f"/v1/templates/{id}/health?org_id={org_id}"
    url = with_query(url, **kwargs)
    return _client.get(url)
