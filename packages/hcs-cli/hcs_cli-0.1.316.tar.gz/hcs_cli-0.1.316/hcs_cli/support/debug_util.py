import os
import subprocess
import sys
import time


def run_command(command: list, exit_on_failure: bool = True, verbose: bool = True):
    if verbose:
        print("COMMAND: ", " ".join(command))
    try:
        result = subprocess.run(command, capture_output=True, check=True, text=True)
        if verbose:
            print("SUCCESS:", result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print("ERROR:  ", e.stderr)
        if exit_on_failure:
            sys.exit(1)


def restart_service(service_name: str, old_pod_id: str):
    service_full_name = get_service_full_name(service_name)
    run_command(["kubectl", "rollout", "restart", service_full_name])
    run_command(["kubectl", "rollout", "status", service_full_name])

    # wait for the old pod to be deleted
    if old_pod_id:
        res_type_name = service_full_name[: service_full_name.find("/")]

        if service_full_name.startswith("deployment"):
            res_type_name = "pod"
        elif service_full_name.startswith("statefulset"):
            res_type_name = "statefulset"

        old_pod_full_name = f"{res_type_name}/{old_pod_id}"
        print(f"Waiting for termination: {old_pod_full_name}...")
        while True:
            result = subprocess.run(["kubectl", "get", old_pod_full_name], capture_output=True, check=False, text=True)
            if result.returncode != 0:
                break
            time.sleep(3)

    return get_pod_id(service_name, verbose=False)


def kubectl_patch(service_name: str, patch_params: list):

    service_full_name = get_service_full_name(service_name)
    # Formulate the Kubernetes patch command
    patch_command = ["kubectl", "patch", service_full_name] + patch_params

    old_pod_id = get_pod_id(service_name, verbose=False)

    # Execute the patch command and capture stdout/stderr
    run_command(patch_command)

    return restart_service(service_name, old_pod_id)


def get_service_full_name(service: str):
    if service in ["clouddriver", "connection-service", "vmhub"]:
        return f"statefulset/{service}-statefulset"
    else:
        return f"deployment/{service}-deployment"


def get_mvn_build_cmd():
    for filename in os.listdir():
        if filename == "settings.xml":
            return "mvn package -DskipTests -s settings.xml"
    return "mvn package -DskipTests"


def get_pod_id(service, verbose: bool = False):
    pod_name_command = ["kubectl", "get", "po", "-l", f"app={service}", "-o", "jsonpath='{.items[0].metadata.name}'"]
    pod_id = run_command(pod_name_command, verbose=verbose).stdout
    if pod_id.startswith("'"):
        pod_id = pod_id[1:-1]
    return pod_id
