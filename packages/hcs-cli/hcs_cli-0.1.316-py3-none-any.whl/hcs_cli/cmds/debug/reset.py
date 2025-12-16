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
@click.option("--image", "-i", type=str, required=False, help="Specify the image to use. Optional.")
def reset(service: str, **kwargs):
    """Reset service k8s container"""

    service = recent.require("hcs_debug_k8s_service", service)

    # Define the patch operations
    patch_ops = [
        {
            "op": "add",
            "path": "/spec/template/spec/containers/0/livenessProbe",
            "value": {
                "failureThreshold": 3,
                "httpGet": {"path": "/actuator/health", "port": 8080, "scheme": "HTTP"},
                "initialDelaySeconds": 20,
                "periodSeconds": 60,
                "successThreshold": 1,
                "timeoutSeconds": 20,
            },
        },
        {
            "op": "add",
            "path": "/spec/template/spec/containers/0/readinessProbe",
            "value": {
                "failureThreshold": 3,
                "httpGet": {"path": "/actuator/health", "port": 8080, "scheme": "HTTP"},
                "initialDelaySeconds": 20,
                "periodSeconds": 10,
                "successThreshold": 1,
                "timeoutSeconds": 20,
            },
        },
        {"op": "replace", "path": "/spec/template/spec/containers/0/command", "value": None},
    ]

    image = kwargs.get("image")
    if image:
        patch_ops.append(
            {
                "op": "replace",
                "path": "/spec/template/spec/containers/0/image",
                "value": f"hcsdevframework.azurecr.io/devframe-prod/horizonv2-sg/{service}:{image}",
            }
        )

    # Formulate the Kubernetes patch command
    patch_params = [
        "--type=json",
        "--patch",
        json.dumps(patch_ops),  # Convert patch_ops to JSON string
    ]

    kubectl_patch(service, patch_params)
