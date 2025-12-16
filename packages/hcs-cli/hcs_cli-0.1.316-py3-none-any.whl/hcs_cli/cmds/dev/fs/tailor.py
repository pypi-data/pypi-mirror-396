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

import subprocess

import click
import questionary

from hcs_cli.cmds.dev.fs.helper.k8s_util import kubectl
from hcs_cli.cmds.dev.fs.helper.util import validate_fs_kubeconfig, validate_fs_profile
from hcs_cli.cmds.dev.util.log import fail, warn

_service_dependency = {
    "inventory": [],
    "clouddriver": ["pki"],
    "lcm": ["inventory", "credentials", "clouddriver", "vmhub"],
    "vmhub": ["pki"],
    "admin": ["lcm", "inventory", "credentials"],
    "portal": ["admin"],
}

_core_infra = ["kafka-standalone", "mongodb-standalone", "redis-standalone", "mqtt-server"]

_ring0 = ["credentials", "auth", "org-service", "pki"]

_scenario_dependency_map = {
    "lcm-core": [
        "lcm",
        "inv-status-sync",
        "smart-capacity-management",
        "scheduler-control-service",
    ],
    "ring0": [
        "admin",
        "lcm",
        "inv-status-sync",
        "smart-capacity-management",
        "scheduler-control-service",
        "inventory",
        "org-service",
        "credentials",
        "auth",
        "pki",
        "clouddriver",
        "vmhub",
        "connection-service",
        "license-features",
        "portal",
        "deployer",
        "images",
        "ad-twin",
        "graphql",
        "aims",
    ],
}


@click.command()
@click.argument("for-scenario", required=False)
def tailor(for_scenario: str, **kwargs):
    """Tailor the feature stack for development of the component, by deleting unrelated deployments."""

    validate_fs_profile()
    validate_fs_kubeconfig()
    existing_deployments, existing_statefulsets = _get_deployments_and_statefulsets()

    if not for_scenario:
        names = list(_scenario_dependency_map.keys())
        for_scenario = questionary.select("Select dev scenario:", names, default=names[0], show_selected=True).ask()
        if not for_scenario:
            return "", 1
    else:
        if for_scenario not in _scenario_dependency_map:
            click.echo(f"Scenario '{for_scenario}' not found. Available scenarios:")
            for comp in _scenario_dependency_map:
                click.echo(f"  - {comp}")
            return "", 1

    dependencies = _scenario_dependency_map[for_scenario]

    visited_dependencies = set(_core_infra + _ring0)
    todo_dependencies = list(dependencies)
    while todo_dependencies:
        service = todo_dependencies.pop()
        if service in visited_dependencies:
            continue
        print(f"+ {service}")
        visited_dependencies.add(service)
        new_dependencies = _service_dependency.get(service, [])
        for dep in new_dependencies:
            if dep in visited_dependencies:
                continue
            print(f"+ {service} -> {dep}")
            todo_dependencies.append(dep)

    # fix final_dependencies service names to match deployment/statefulset names
    all_names = set(existing_deployments + existing_statefulsets)
    final_dependencies = set()
    missing_dependencies = set()
    for d in visited_dependencies:
        if d in all_names:
            final_dependencies.add(d)
            continue
        if d + "-deployment" in all_names:
            final_dependencies.add(d + "-deployment")
            continue
        if d + "-statefulset" in all_names:
            final_dependencies.add(d + "-statefulset")
            continue
        if d + "-standalone" in all_names:
            final_dependencies.add(d + "-standalone")
            continue
        missing_dependencies.add(d)

    targets_to_remove = sorted(all_names - final_dependencies)
    final_dependencies = sorted(final_dependencies)

    for t in final_dependencies:
        click.echo(click.style(" KEEP    " + t, fg="white"))
    for t in missing_dependencies:
        click.echo(click.style(" MISSING " + t, fg="bright_yellow"))
    for t in targets_to_remove:
        click.echo(click.style(" REMOVE  " + t, fg="bright_black"))
        # try:
        #     # Use kubectl to delete the deployment or statefulset
        #     subprocess.run(["kubectl", "delete", "deployment", t], check=True)
        # except subprocess.CalledProcessError as e:
        #     print_error(f"Failed to delete {t}: {e}")

    # kubectl scale deployment <deployment-name> --replicas=0

    click.confirm("Remove unnecessary pods?", abort=True)

    for t in targets_to_remove:
        print(f"Removing {t}...")
        # Use kubectl to delete the deployment or statefulset
        if t.endswith("-deployment") or t in existing_deployments:
            kubectl(f"scale deployment {t} --replicas=0")
        elif t.endswith("-statefulset") or t in existing_statefulsets:
            kubectl(f"scale statefulset {t} --replicas=0")
        else:
            raise ValueError(f"Unknown target type for {t}")

    error_pods = _list_error_pods()
    if error_pods:
        print("Remove error pods:")
        for pod, reason in error_pods.items():
            print(f"  - {pod:<60} {reason}")
        for pod in error_pods:
            kubectl(f"delete pod {pod}")
    else:
        print("No error pods found.")
    return


def _get_deployments_and_statefulsets():
    # Get the names of all deployments in the current namespace
    output = kubectl("get deployments -o jsonpath='{.items[*].metadata.name}'").stdout
    deployments = output.strip().replace("'", "").split()
    output = kubectl("get statefulsets -o jsonpath='{.items[*].metadata.name}'").stdout
    statefulsets = output.strip().replace("'", "").split()
    return deployments, statefulsets


def _list_error_pods():
    pods_json = kubectl("get pods -o json", show_command=False, get_json=True)
    error_pods = {}
    for item in pods_json.get("items", []):
        pod_name = item["metadata"]["name"]
        phase = item["status"].get("phase", "")
        if phase == "Failed" or phase == "Unknown":
            error_pods[pod_name] = f"Pod phase: {phase}"
            continue
        for container_status in item["status"].get("containerStatuses", []):
            waiting_state = container_status.get("state", {}).get("waiting", {})
            terminated_state = container_status.get("state", {}).get("terminated", {})
            if waiting_state:
                reason = waiting_state.get("reason", "Waiting")
                error_pods[pod_name] = f"Container waiting: {reason}"
                break
            if terminated_state:
                reason = terminated_state.get("reason", "Terminated")
                error_pods[pod_name] = f"Container terminated: {reason}"
                break
    return error_pods
