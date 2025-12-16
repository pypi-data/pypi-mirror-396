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

from hcs_core.sglib.client_util import default_crud, hdc_service_client
from httpx import HTTPStatusError

_client = hdc_service_client("images")
_crud_vsphere = default_crud(_client, "/v1/vsphere/gold-patterns", "gold-patterns")
_crud_nutanix = default_crud(_client, "/v1/nutanix/gold-patterns", "gold-patterns")
_crud_akka = default_crud(_client, "/v1/akka/gold-patterns", "gold-patterns")


def _raise_if_unsupported_provider_error(ex):
    if not isinstance(ex, HTTPStatusError):
        raise ex
    if not ex.response:
        raise ex
    content = ex.response.text
    if not content or content.find("UNSUPPORTED_PROVIDER") < 0:
        raise ex


def get(id: str, org_id: str, **kwargs):
    ret = _crud_vsphere.get(id, org_id, **kwargs)
    if not ret:
        ret = _crud_akka.get(id, org_id, **kwargs)
    try:
        if not ret:
            ret = _crud_nutanix.get(id, org_id, **kwargs)
    except Exception as e:
        _raise_if_unsupported_provider_error(e)
        # else pass

    if not ret:
        return

    return _formalize_gold_pattern_model(ret)


def list(org_id: str, **kwargs):
    ret1 = _crud_vsphere.list(org_id, **kwargs)
    ret2 = _crud_akka.list(org_id, **kwargs)
    try:
        ret3 = _crud_nutanix.list(org_id, **kwargs)
    except HTTPStatusError as e:
        _raise_if_unsupported_provider_error(e)
        # else pass
        ret3 = []

    ret = []
    for r in ret1:
        ret.append(_formalize_gold_pattern_model(r))
    for r in ret2:
        ret.append(_formalize_gold_pattern_model(r))
    for r in ret3:
        ret.append(_formalize_gold_pattern_model(r))
    return ret


def create(payload: dict, **kwargs):
    if _is_nutanix(payload):
        ret = _crud_nutanix.create(payload, **kwargs)
    elif _is_akka(payload):
        ret = _crud_akka.create(payload, **kwargs)
    else:
        ret = _crud_vsphere.create(payload, **kwargs)
    return _formalize_gold_pattern_model(ret)


def delete(**kwargs):
    _crud_vsphere.delete(**kwargs)
    _crud_akka.delete(**kwargs)
    try:
        _crud_nutanix.delete(**kwargs)
    except Exception as e:
        _raise_if_unsupported_provider_error(e)
        # else pass


def _formalize_gold_pattern_model(data):
    if data:
        return data["goldPattern"]
    return data


def _is_akka(payload):
    method = payload["goldPattern"]["goldPatternDetails"]["method"]
    return method.lower().find("akka") >= 0


def _is_nutanix(payload):
    method = payload["goldPattern"]["goldPatternDetails"]["method"]
    return method.lower().find("nutanix") >= 0
