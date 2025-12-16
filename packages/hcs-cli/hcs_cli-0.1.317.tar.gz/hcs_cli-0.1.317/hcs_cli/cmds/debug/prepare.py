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

import click
from hcs_core.ctxp import recent

from hcs_cli.support.debug_util import kubectl_patch


@click.command()
@click.argument("service", type=str, required=False)
def prepare(service: str, **kwargs):
    """Prepare service k8s pod for debugging"""

    service = recent.require("hcs_debug_k8s_service", service)

    # Define the patch operations
    patch_ops = [
        {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe", "value": None},
        {"op": "replace", "path": "/spec/template/spec/containers/0/readinessProbe", "value": None},
        {"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["sleep", "8640000"]},
    ]

    # Formulate the Kubernetes patch command
    patch_params = [
        "--type=json",
        "--patch",
        json.dumps(patch_ops),  # Convert patch_ops to JSON string
    ]

    new_pod_id = kubectl_patch(service, patch_params)

    return new_pod_id
