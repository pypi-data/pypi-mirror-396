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

import inspect
import json
import os
import re
import shutil
import subprocess
import time
from collections import OrderedDict, defaultdict
from pathlib import Path

import click
import hcs_core.sglib.cli_options as cli
from dotenv import load_dotenv
from hcs_core.ctxp import context, profile
from hcs_core.ctxp.util import error_details
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.separator import Separator
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

import hcs_cli.cmds.dev.util.github_helper as github_helper
import hcs_cli.support.profile as profile_support
from hcs_cli.cmds.dev.fs.helper import credential_helper, jenkins_util, k8s_util, license_info, step_util
from hcs_cli.cmds.dev.fs.helper.k8s_util import kubectl
from hcs_cli.cmds.dev.fs.helper.step_util import step as step
from hcs_cli.cmds.dev.util import log
from hcs_cli.cmds.dev.util.log import fail as fail
from hcs_cli.cmds.dev.util.log import warn as warn
from hcs_cli.service import auth, org_service
from hcs_cli.service.admin.uag import list as list_uags
from hcs_cli.support.exec_util import exec, run_cli
from hcs_cli.support.template_util import with_template_file

_delete_temp_files = False


@click.command()
@cli.org_id
@click.option("--interactive/--auto", "-i/-a", is_flag=True, default=True, help="Interactive mode.")
@click.option("--step", "-s", type=str, required=False, help="Steps to run. Default is all steps.")
@click.option(
    "--jenkins",
    "-j",
    type=str,
    required=False,
    help="The service name that triggered the feature stack pipeline, e.g. 'lcm'. This option is used to download kubeconfig.",
)
@click.option("--delete-temp-files", is_flag=True, default=False, help="Delete temporary files after use.")
@click.argument("fs_name", type=str, required=False)
def init(interactive: bool, step: str, jenkins: str, fs_name: str, delete_temp_files: bool, **kwargs):
    """Initialize feature stack with common settings and infrastructure."""

    if not fs_name:
        fs_name = profile.name()

    if fs_name == "default":
        # default is not valid. Should be FS short id.
        fail("Usage: hcs dev fs init <YOUR_FEATURE_STACK_ID>")

    global _delete_temp_files
    _delete_temp_files = delete_temp_files

    if interactive and not step:
        disabled_steps = _collect_setup_config()
        step_util.disable(disabled_steps)

    if step:
        _run_single_step(step)
    else:
        _prepare_profile(fs_name)
        _prepare_k8s_config(jenkins)
        _get_client_credential_from_k8s_and_update_profile()
        _validate_fs_auth()
        _common_init()
        _create_idp()
        _create_infra_akka()
        _create_infra_lcm_zerocloud()
        _create_infra_azure(fs_name)
        _create_infra_azsim()
    log.good("Done")


@step
def _common_init():
    _reg_datacenter()
    _create_org_details()
    _create_org_location_mapping()
    _create_license_info()
    _patch_mqtt_alias()
    _update_mqtt()
    _show_mqtt_info()
    _test_mqtt()
    _restart_services()
    _wait_for_services_restart()
    _touch_fs_to_avoid_recycle()


@step
def _prepare_profile(fs_name: str):
    api_token = os.getenv("HCS_API_TOKEN")
    hcs_client_id = os.getenv("HCS_CLIENT_ID")
    hcs_client_secret = os.getenv("HCS_CLIENT_SECRET")
    env_org_id = os.getenv("ORG_ID")
    if not profile.exists(fs_name):
        log.info("Feature profile does not exist. Creating profile: " + fs_name)
        profile_data = profile_support.create_for_feature_stack(fs_name)
        if not hcs_client_id or not hcs_client_secret:
            if not api_token:
                fail("Both HCS_CLIENT_ID and HCS_API_TOKEN are missing. Specify at least one type of credentials.")
        profile_data["csp"]["orgId"] = env_org_id
        profile_data["csp"]["apiToken"] = api_token
        profile_data["csp"]["clientId"] = hcs_client_id
        profile_data["csp"]["clientSecret"] = hcs_client_secret
        profile.create(fs_name, profile_data, overwrite=False, auto_use=True)
    else:
        if profile.name() != fs_name:
            log.warn("Switching to profile: " + fs_name)
            profile.use(fs_name)
        profile_data = profile.current()
        _validate_fs_url(profile_data.hcs.url)
        updated = False
        if env_org_id and profile_data.csp.orgId != env_org_id:
            log.warn(
                f"Current profile orgId ({profile_data.csp.orgId}) does not match provided orgId. Updating profile to use the specified orgId {env_org_id}."
            )
            profile_data.csp.orgId = env_org_id
            updated = True
        if api_token and profile_data.csp.apiToken != api_token:
            log.warn(
                f"Current profile apiToken ({profile_data.csp.apiToken}) does not match provided apiToken. Updating profile to use the specified apiToken."
            )
            profile_data.csp.apiToken = api_token
            updated = True
        if (
            hcs_client_id
            and profile_data.csp.clientId != hcs_client_id
            or hcs_client_secret
            and profile_data.csp.clientSecret != hcs_client_secret
        ):
            log.warn(
                f"Current profile clientId ({profile_data.csp.clientId}) or clientSecret does not match provided values. Updating profile to use the specified clientId and clientSecret."
            )
            profile_data.csp.clientId = hcs_client_id
            profile_data.csp.clientSecret = hcs_client_secret
            updated = True

        if updated:
            profile.save()

    # validate the API token matches org-id
    import hcs_core.sglib.auth as auth

    token = auth.login(force_refresh=True)
    token_org_id = auth.get_org_id_from_token(token)
    profile_data = profile.current(reload=True)
    profile_org_id = profile_data.csp.orgId
    if env_org_id:
        if env_org_id != token_org_id:
            warn("The provided ORG_ID does not match the API token org.")
    else:
        env_org_id = token_org_id
        os.environ["ORG_ID"] = token_org_id

    if profile_org_id:
        if profile_org_id != token_org_id:
            log.warn(
                f"Profile orgId ({profile_org_id}) does not match API token org ({token_org_id}). Updating profile to use the API token org."
            )
            profile_data.csp.orgId = token_org_id
            profile.save()
        else:
            pass
    else:
        profile_data.csp.orgId = token_org_id
        profile.save()


def _collect_setup_config():
    # Step 1: Collect environment config
    has_local_env = os.path.isfile(".env")
    choices = []
    if has_local_env:
        choices.append(Choice(value="_local_env", enabled=True, name="Load local .env file"))

    choices += [
        Choice(value="_nightly_test_env", enabled=True, name="Auto configure from nightly test"),
        Choice(value="_user_specified_env", enabled=True, name="User provided env file"),
    ]

    env_choice = inquirer.select(
        message="Choose how to load your .env file:",
        choices=choices,
        instruction="(Use SPACE to toggle, ENTER to confirm)",
    ).execute()

    # Step 2: Collect deployment config
    deployment_choices = [
        Choice(value="_common_init", enabled=True, name="Common Init (Org, Datacenter, License, MQTT, ...)"),
        Separator("-------- Pools/Templates --------"),
        Choice(value="_create_infra_akka", enabled=False, name="Akka (Provider, Edge, UAG, Dedicated/Floating/Multi-session)"),
        Choice(value="_create_infra_azure", enabled=False, name="Azure (Provider, Edge, UAG, Dedicated/Floating/Multi-session)"),
        Choice(value="_create_infra_azsim", enabled=False, name="Azure-simulator (Provider, Edge, UAG, Dedicated/Floating/Multi-session)"),
        Choice(value="_create_infra_lcm_zerocloud", enabled=False, name="LCM Zerocloud Templates"),
    ]

    selected = inquirer.checkbox(
        message="Select deployment features:",
        choices=deployment_choices,
        instruction="(Use SPACE to toggle, ENTER to confirm)",
        transformer=lambda result: ", ".join(result),
    ).execute()

    env_path = ".env"
    if env_choice == "_nightly_test_env":
        env_path = _retrieve_config_from_nightly_repo()
    elif env_choice == "_user_specified_env":
        completer = PathCompleter(expanduser=True)
        env_path_input = prompt("Enter the full path to your .env file: ", completer=completer, default="~/")
        env_path = Path(env_path_input).expanduser().resolve()

    env_path = os.path.expanduser(str(env_path))
    if is_valid_env_file(env_path):
        load_dotenv(env_path, override=True)
        log.good(f"Loaded environment file from {os.path.abspath(env_path)}")
    else:
        fail(f"Could not find .env file at {env_path}. Please ensure it follows the template format.")
    disabled_steps = [c.value for c in deployment_choices if isinstance(c, Choice) and c.value not in selected]

    return disabled_steps


def _retrieve_config_from_nightly_repo():
    OUTPUT_ENV_FILE = ".env"

    github_helper.check_ssh_access()
    with github_helper.repo("git@github.com:euc-eng/horizonv2-sg.nightly-tests.git") as repo:
        config_data = repo.get("src/test/resources/com/vmware/integration/sg/payloads/onboard/configuration.txt", format="json")
        config_props = repo.get("src/test/resources/config.properties")

    _write_env_file(config_data, config_props, OUTPUT_ENV_FILE)
    _organize_env_file(OUTPUT_ENV_FILE)

    log.good(f".env file created at: {Path(OUTPUT_ENV_FILE).resolve()}")
    return Path(OUTPUT_ENV_FILE)


@step
def _create_infra_azure(fs_name):
    # use the following command to inspect the resolved file
    #   hcs plan resolve
    # or examine the finally resolved input after deployment:
    #   hcs plan input
    azure_plan_path = _resolve_bundled_file_path("provided_files/azure.plan.yml")
    ret = run_cli("hcs plan apply -f " + azure_plan_path, raise_on_error=False)
    if ret.returncode != 0:
        log.warn("Failed to apply Azure plan. Please check the output for details.")
        return

    # To get the output, use the following command:
    #   hcs plan output -d
    # or programatically
    details = run_cli("hcs plan output --details", output_json=True)

    # store in context
    context.set("infra", details)

    # It can be retrieved from other modules when needed:
    # infra = context.get("infra")
    # print(json.dumps(infra['mySite'], indent=4))
    # print(json.dumps(infra['myProvider'], indent=4))
    _map_fqdn_to_lb(fs_name)
    log.good("Azure infrastructure set up.")


@step
def _create_infra_azsim():
    azusim_plan_path = _resolve_bundled_file_path("provided_files/azsim.plan.yml")
    ret = run_cli("hcs plan apply -f " + azusim_plan_path, raise_on_error=False)
    if ret.returncode == 0:
        log.good("Azure simulator infrastructure set up.")
    else:
        log.warn("Failed to apply Azure simulator plan. Please check the output for details.")


@step
def _create_infra_akka():
    infra_plan_path = _resolve_bundled_file_path("provided_files/akka.plan.yml")
    ret = run_cli("hcs plan apply -f " + infra_plan_path, raise_on_error=False)
    if ret.returncode == 0:
        log.good("Akka infrastructure set up.")
    else:
        log.warn("Failed to apply Akka plan. Please check the output for details.")


@step
def _create_infra_lcm_zerocloud():
    run_cli("hcs lcm template create -p zero-floating", output_json=True)
    run_cli("hcs lcm template create -p zero-dedicated", output_json=True)
    run_cli("hcs lcm template create -p zero-multisession", output_json=True)
    log.good("LCM Zerocloud template.")


@step
def _create_license_info():
    license_info.createLicenseFeatures()
    log.good("License set up.")


def is_valid_env_file(path):
    if not os.path.isfile(path):
        return False
    if not os.path.basename(path).startswith(".env"):
        return False
    try:
        with open(path, "r") as f:
            for line in f:
                if line.strip() == "" or line.strip().startswith("#"):
                    continue
                if "=" not in line:
                    return False
        return True
    except Exception:
        return False


def extract_network_info(env_file_path=".env"):
    virtual_network = None
    subnets = {}

    with open(env_file_path, "r") as env_file:
        for line in env_file:
            line = line.strip()
            if line.startswith("virtualNetwork="):
                virtual_network = line.split("=", 1)[1]
            elif any(line.startswith(f"{name}=") for name in ["dmzSubnet", "managementSubnet", "desktopSubnet"]):
                key, value = line.split("=", 1)
                subnets[key] = value

    # Parse the virtual network resource ID
    parts = virtual_network.split("/")
    subscription_id = parts[2]
    resource_group = parts[4]
    vnet_name = parts[-1]

    return subscription_id, resource_group, vnet_name, subnets


def _write_subnet_cidrs_to_config_file(subscription_id, vnet, resource_group, subnets):
    try:
        subprocess.run(["az", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except:
        fail("Set up Azure CLI before proceeding.")
    print(f"Setting Azure subscription to {subscription_id}")
    try:
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)
    except:
        fail(f"You don't have access to subscription {subscription_id}, please contact your admin for help.")
    log.good("Azure subscription successfully set.")
    print("Attempting to retrieve CIDR values for subnets.")
    for key, value in subnets.items():
        try:
            cidr_output = subprocess.check_output(
                [
                    "az",
                    "network",
                    "vnet",
                    "subnet",
                    "show",
                    "--name",
                    value,
                    "--vnet-name",
                    vnet,
                    "--resource-group",
                    resource_group,
                    "--query",
                    "addressPrefix",
                    "--output",
                    "tsv",
                ],
                text=True,
            ).strip()

            # Append to .env file
            with open(".env", "a") as env_file:
                env_file.write(f"{key}_CIDR={cidr_output}\n")
        except:
            fail("Error retrieving one or more CIDRs.")

    log.good("CIDR values retrieved!")
    with open(".env", "a") as env_file:
        config_block = f"""
        desktopResourceGroup={resource_group}
        infraResourceGroup={resource_group}
        desktopVnet={vnet}
        infraVnet={vnet}
        """
        env_file.write(config_block)


def _prepare_repo(clone_dir):
    if Path(clone_dir).exists():
        log.warn(f"Deleting existing directory: {clone_dir}")
        shutil.rmtree(clone_dir)
    print("📥 Cloning repo with sparse-checkout...")
    cmd = "git clone --filter=blob:none --no-checkout --depth=1 git@github.com:euc-eng/horizonv2-sg.nightly-tests.git"
    exec(cmd, log_error=True, raise_on_error=False, inherit_output=False).stdout


def _sparse_checkout(clone_dir):
    files_to_checkout = [
        "src/test/resources/com/vmware/integration/sg/payloads/onboard/configuration.txt",
        "src/test/resources/config.properties",
    ]
    for file in files_to_checkout:
        cmd = f"git checkout master -- {file}"
        exec(cmd, log_error=True, raise_on_error=False, inherit_output=False, cwd=clone_dir).stdout


def _read_json_config(clone_dir):
    path = Path(clone_dir) / "src/test/resources/com/vmware/integration/sg/payloads/onboard/configuration.txt"
    print(f"📄 Reading: {path}")
    with open(path, "r") as f:
        return json.load(f)


def _read_properties(clone_dir):
    path = Path(clone_dir) / "src/test/resources/config.properties"
    print(f"📄 Reading: {path}")
    props = {}
    with open(path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                props[key.strip()] = value.strip()
    return props


def _write_env_file(data, props, env_file):
    ignore_keys = {
        "aksUserIdentity",
        "adServerEndpoint",
        "signingCaName",
        "caHostName",
        "siteName",
        "domainUser",
        "domainPassword",
        "virtualNetwork",
    }
    ad_username = data.get("domainUser")
    ad_password = data.get("domainPassword")

    with open(env_file, "w") as f:
        for key, value in data.items():
            if key not in ignore_keys:
                f.write(f"{to_env_key(key)}={value}\n")
        config_block = f"""HCS_CLIENT_ID={props['csp.service.app.client_id']}
        HCS_CLIENT_SECRET={props['csp.service.app.client_secret']}
        IDP_TENANT_DOMAIN=test-sanity-domain
        UAG_FQDN=myuag.fqdn
        DESKTOP_SUBNET_CIDR=10.76.0.0/16
        DMZ_SUBNET_CIDR=10.77.0.0/24
        MANAGEMENT_SUBNET_CIDR=10.77.3.0/24
        TENANT_SUBNET=desktop-76
        TENANT_SUBNET_CIDR=10.76.0.0/16
        DESKTOP_RESOURCE_GROUP=horizonv2-sg-dev
        INFRA_RESOURCE_GROUP=horizonv2-sg-dev
        DESKTOP_VNET=horizonv2-sg-dev-vnet
        INFRA_VNET=horizonv2-sg-dev-vnet
        PRIMARY_BIND_USER_NAME={ad_username}
        PRIMARY_BIND_PASSWORD={ad_password}
        AUXILIARY_BIND_USER_NAME={ad_username}-2
        AUXILIARY_BIND_PASSWORD={ad_password}-2
        PRIMARY_JOIN_USER_NAME={ad_username}-3
        PRIMARY_JOIN_PASSWORD={ad_password}-3
        AUXILIARY_JOIN_USER_NAME={ad_username}-4
        AUXILIARY_JOIN_PASSWORD={ad_password}-4
        ENTITLEMENT_USER_1={ad_username}
        ENTITLEMENT_USER_2={ad_username}-2
        IMAGE_USER_NAME={ad_username}
        IMAGE_PASSWORD={ad_password}
        VM_USER_NAME={ad_username}
        VM_PASSWORD={ad_password}
        DEPLOYMENT_ID=az-1
        """
        f.write(config_block)


def to_env_key(key):
    ACRONYMS = {"BIOS", "CIDR"}
    key_snake = re.sub(r"(?<!^)(?=[A-Z])", "_", key).upper()
    # Fix known acronyms (e.g., NET_B_I_O_S → NET_BIOS)
    for acronym in ACRONYMS:
        key_snake = re.sub(r"_".join(acronym), acronym, key_snake)
    return key_snake


def _organize_env_file(env_file):
    group_rules = OrderedDict(
        [
            ("Credentials (Optional):", ["HCS_CLIENT_ID", "HCS_CLIENT_SECRET"]),
            ("Identity Provider (IDP) Configuration", ["IDP_USER_NAME", "IDP_PASSWORD", "IDP_TENANT_DOMAIN"]),
            (
                "AD Configuration",
                [
                    "DNS_DOMAIN_NAME",
                    "NET_BIOS_NAME",
                    "PRIMARY_JOIN_USER_NAME",
                    "PRIMARY_JOIN_PASSWORD",
                    "AUXILIARY_JOIN_USER_NAME",
                    "AUXILIARY_JOIN_PASSWORD",
                    "PRIMARY_BIND_USER_NAME",
                    "PRIMARY_BIND_PASSWORD",
                    "AUXILIARY_BIND_USER_NAME",
                    "AUXILIARY_BIND_PASSWORD",
                ],
            ),
            (
                "Primary Provider Configuration",
                ["PROVIDER_LABEL", "SUBSCRIPTION_ID", "DIRECTORY_ID", "APPLICATION_ID", "APPLICATION_KEY", "REGION"],
            ),
            ("Resource and Network Configuration", ["DESKTOP_RESOURCE_GROUP", "INFRA_RESOURCE_GROUP", "DESKTOP_VNET", "INFRA_VNET"]),
            (
                "Subnet",
                [
                    "DMZ_SUBNET",
                    "DMZ_SUBNET_CIDR",
                    "DESKTOP_SUBNET",
                    "DESKTOP_SUBNET_CIDR",
                    "MANAGEMENT_SUBNET",
                    "MANAGEMENT_SUBNET_CIDR",
                    "TENANT_SUBNET",
                    "TENANT_SUBNET_CIDR",
                ],
            ),
            ("Resource Credentials", ["IMAGE_USER_NAME", "IMAGE_PASSWORD", "VM_USER_NAME", "VM_PASSWORD"]),
            ("UAG", ["UAG_FQDN"]),
            ("Entitlement", ["ENTITLEMENT_USER_1", "ENTITLEMENT_USER_2"]),
            ("Deployment ID", ["DEPLOYMENT_ID"]),
        ]
    )

    with open(env_file, "r") as f:
        lines = f.readlines()

    env_dict = {line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip() for line in lines if "=" in line and not line.startswith("#")}

    grouped_env = defaultdict(list)
    ungrouped = []

    for key, value in env_dict.items():
        found = False
        for group, keys in group_rules.items():
            if key in keys:
                grouped_env[group].append(f"{key}={value}")
                found = True
                break
        if not found:
            ungrouped.append(f"{key}={value}")

    organized_lines = []
    for group, items in grouped_env.items():
        organized_lines.append(f"# {group}")
        organized_lines.extend(items)
        organized_lines.append("")

    if ungrouped:
        organized_lines.append("# Other Variables")
        organized_lines.extend(ungrouped)

    with open(env_file, "w") as f:
        f.write("\n".join(organized_lines))


def _cleanup_repo(clone_dir):
    print(f"🧹 Cleaning up cloned repo: {clone_dir}")
    shutil.rmtree(clone_dir)
    log.good("🗑️ Repo deleted.")


@step
def _touch_fs_to_avoid_recycle():
    namespace = profile.name()
    ns_json = kubectl(f"get namespace {namespace} -ojson", get_json=True)
    metadata = ns_json.get("metadata", {})
    # Update annotations
    annotations = metadata.setdefault("annotations", {})
    # Update labels
    labels = metadata.setdefault("labels", {})
    updated_at = time.strftime("%Y-%m-%d")
    annotations["updatedAt"] = updated_at
    labels["updatedAt"] = updated_at
    file_patch_fs_updated_at = "patch-fs-updated-at.json"
    with open(file_patch_fs_updated_at, "w") as f:
        json.dump(ns_json, f, indent=4)
    kubectl(f"apply -f {file_patch_fs_updated_at}")
    if _delete_temp_files and os.path.exists(file_patch_fs_updated_at):
        os.remove(file_patch_fs_updated_at)
    log.good(f"Namespace {namespace} 'updatedAt' set to {updated_at}, so it will not be recycled soon.")


def _run_single_step(name):
    name = name.lower().replace("-", "_")
    import hcs_cli.cmds.dev.fs.init as my_self

    steps = [
        obj
        for fn_name, obj in inspect.getmembers(my_self)
        if inspect.isfunction(obj) and fn_name.startswith("_") and fn_name not in ["_run_single_step", "init"]
    ]
    candidates = [f for f in steps if name in f.__name__.lower()]
    if not candidates:
        fail(f"No step found matching '{name}'.")
    elif len(candidates) > 1:
        fail(f"Multiple steps found matching '{name}': {[f.__name__ for f in candidates]}")
    else:
        candidates[0]()


@step
def _prepare_k8s_config(jenkins: str = None):
    fs_name = profile.name()
    try:
        if not k8s_util.validate_kubeconfig(fs_name, raise_on_error=False):
            feature_stack_service = jenkins if jenkins else os.getenv("FEATURE_STACK_SERVICE")
            if feature_stack_service:
                print("kubectl config validation failed.")
                print(f"Retrieving feature stack kubeconfig from Jenkins pipeline: {feature_stack_service}")
                jenkins_util.download_kubeconfig(feature_stack_service)
                k8s_util.validate_kubeconfig(fs_name, raise_on_error=True)
    except Exception as e:
        print(error_details(e))
        fail(
            "Feature stack kubectl config is not set.\n"
            "Recovery options:\n"
            "  1. Download and copy feature stack kubeconfig to ~/.kube/_fs_config\n"
            "  2. Or specify service name that triggered FS, using 'hcs dev fs <fs-name> --jenkins <service-name>', to download kubeconfig from Jenkins feature stack pipeline.\n"
        )


def _resolve_bundled_file_path(relative_path: str):
    current_file_path = os.path.abspath(__file__)
    base_path = os.path.dirname(current_file_path)
    return os.path.join(base_path, relative_path)


@step
def _patch_mqtt_alias():
    with_template_file(
        "provided_files/patch-mqtt-hostname.yml",
        substitutions={r"{{FS_NAME}}": profile.name()},
        fn=lambda temp_file_path: kubectl(f"apply -f {temp_file_path}"),
        base_path=__file__,
        delete_after=_delete_temp_files,
    )
    log.good("MQTT hostname patched.")


@step
def _show_mqtt_info():
    ret = kubectl("exec -t mqtt-server-0 -- vmq-admin session show", ignore_error=True)
    if not ret:
        log.warn("MQTT session info not available.")
        return
    print(ret.stdout)
    if ret.stderr:
        print("Error retrieving MQTT session info:", ret.stderr)


@step
def _update_mqtt():
    namespace = profile.name()
    with_template_file(
        "provided_files/mqtt-server-external.yaml",
        substitutions={r"(namespace:\s*)\S+": rf"\1{namespace}"},
        fn=lambda temp_file_path: kubectl(f"apply -f {temp_file_path}"),
        base_path=__file__,
        delete_after=_delete_temp_files,
    )

    ip_address = _retrieve_mqtt_server_ip_address("mqtt-server-external")

    with_template_file(
        "provided_files/mqtt-secret.yaml",
        substitutions={
            r"(namespace:\s*)\S+": rf"\1{namespace}",
            r'(mqtt\.server-host:\s*)".*?"': rf'\1"{ip_address}"',
        },
        fn=lambda temp_file_path: kubectl(f"apply -f {temp_file_path}"),
        base_path=__file__,
        delete_after=_delete_temp_files,
    )

    log.good("MQTT external IP updated in k8s secret.")

    profile_data = profile.current()
    profile_data.hcs.regions[0].mqtt = ip_address
    profile.save()
    log.good("MQTT external IP updated in profile.")


@step
def _test_mqtt():
    import hcs_cli.cmds.dev.util.mqtt_helper as mqtt_helper

    try:
        cert_config = mqtt_helper.prepare_cert(os.getenv("ORG_ID"))
        mqtt_helper.test_mqtt(profile.current().hcs.regions[0].mqtt, 8883, cert_config)
    except Exception as e:
        log.warn("Failed testing MQTT:" + error_details(e))


def _retrieve_mqtt_server_ip_address(service_name, timeout=300, interval=5):
    start = time.time()
    while time.time() - start < timeout:
        result = kubectl("get service mqtt-server-external")
        output = result.stdout.strip().splitlines()

        if len(output) >= 2:
            header = output[0].split()
            values = output[1].split()

            ip_index = header.index("EXTERNAL-IP")
            external_ip = values[ip_index]

            if external_ip.lower() != "<pending>" and external_ip.lower() != "<none>":
                log.good(f"External IP found: {external_ip}")
                return external_ip

        print("[…] Waiting for External IP to be assigned...")
        time.sleep(interval)

    fail(f"Timed out waiting for External IP of service '{service_name}'")


@step
def _validate_fs_auth():
    try:
        org_service.datacenter.list()
        log.good("Auth to feature stack")
    except Exception as e:
        fail(
            "Failed to connect to feature stack. Check your profile settings.\n"
            f"  Profile name={profile.name()}\n"
            f"  Profile url={profile.current().hcs.url}\n\n"
            f"Recovery options:\n"
            f"  1. Check if the feature stack is running and accessible.\n"
            f"  2. Verify your API token and org ID in the profile.\n",
            e,
        )


def _validate_fs_url(url):
    # https://nanw.fs.devframe.cp.horizon.omnissa.com
    if url.endswith("/"):
        url = url[:-1]
    if not url.endswith(".fs.devframe.cp.horizon.omnissa.com"):
        fail(
            f"The current profile URL is not a feature stack.\n"
            f"  Profile name={profile.name()}\n"
            f"  Profile url={url}\n\n"
            f"Recovery options:\n"
            f"  1. Create a profile for feature stack: 'hcs profile init --feature-stack <fs-name>'\n"
            f"  2. Or switch to a feature stack profile 'hcs profile use'\n"
        )

    start = url.find("//")
    if start == -1:
        fail("Invalid feature stack URL format: missing '//'. url=" + url)
    start += 2
    end = url.find(".", start)
    if end == -1:
        fail("Invalid feature stack URL format: missing '.' after '//' in url=" + url)
    fs_name = url[start:end]

    log.good("Feature stack: " + fs_name)
    return fs_name


@step
def _get_client_credential_from_k8s_and_update_profile():
    credential_helper.get_client_credential_from_k8s_and_update_profile()
    log.good("Profile updated with client credentials for internal services.")


@step
def _reg_datacenter():
    feature_stack_url = profile.current().hcs.url
    payload1 = {
        "geoLocation": {"coordinates": [-122.143936, 37.468319], "type": "Point"},
        "name": "feature-stack-dc",
        "locations": ["EU", "JP", "GB", "IE", "US"],
        "regions": [
            "westus2",
            "westus",
            "centralus",
            "eastus2",
            "eastus",
            "westus3",
            "northeurope",
            "francecentral",
            "francesouth",
            "germanynorth",
            "germanywestcentral",
            "norwaywest",
            "norwayeast",
            "swedencentral",
            "swedensouth",
            "switzerlandnorth",
            "switzerlandwest",
            "uaecentral",
            "uaenorth",
            "uksouth",
            "ukwest",
            "westeurope",
            "japaneast",
            "australiaeast",
            "centralindia",
            "eastasia",
            "italynorth",
            "israelcentral",
            "usgovvirginia",
            "usgovarizona",
            "usgovtexas",
            "chinanorth",
            "chinanorth2",
            "brazilsouth",
            "us-central1",
            "ap-south-1",
            "us-west-1",
            "us-west-2",
            "us-east-1",
        ],
        "providerRegions": {
            "aws": ["ap-south-1", "us-west-1", "us-west-2", "us-east-1"],
            "gcp": ["us-central1"],
            "azure": [
                "westus2",
                "westus",
                "centralus",
                "eastus2",
                "eastus",
                "westus3",
                "northeurope",
                "francecentral",
                "francesouth",
                "germanynorth",
                "germanywestcentral",
                "norwaywest",
                "norwayeast",
                "swedencentral",
                "swedensouth",
                "switzerlandnorth",
                "switzerlandwest",
                "uaecentral",
                "uaenorth",
                "uksouth",
                "ukwest",
                "westeurope",
                "japaneast",
                "australiaeast",
                "centralindia",
                "eastasia",
                "italynorth",
                "israelcentral",
                "usgovvirginia",
                "usgovarizona",
                "usgovtexas",
                "chinanorth",
                "chinanorth2",
                "brazilsouth",
            ],
        },
        "url": feature_stack_url,
        "edgeHubUrl": "https://horizonv2-em.devframe.cp.horizon.omnissa.com",
        "edgeHubRegionCode": "us",
        "dnsUris": [
            "/subscriptions/bfd75b0b-ffce-4cf4-b46b-ecf18410c410/resourceGroups/horizonv2-sg-dev/providers/Microsoft.Network/dnszones/featurestack.devframe.cp.horizon.omnissa.com"
        ],
        "vmHubs": [
            {
                "name": "default",
                "url": feature_stack_url,
                "uagAasFqdn": "https://int.reverseconnect.uag.azcp.horizon.vmware.com",
                "azureRegions": [
                    "westus2",
                    "westus",
                    "centralus",
                    "eastus2",
                    "eastus",
                    "westus3",
                    "northeurope",
                    "francecentral",
                    "francesouth",
                    "germanynorth",
                    "germanywestcentral",
                    "norwaywest",
                    "norwayeast",
                    "swedencentral",
                    "swedensouth",
                    "switzerlandnorth",
                    "switzerlandwest",
                    "uaecentral",
                    "uaenorth",
                    "uksouth",
                    "ukwest",
                    "westeurope",
                    "japaneast",
                    "australiaeast",
                    "centralindia",
                    "eastasia",
                    "italynorth",
                    "israelcentral",
                    "usgovvirginia",
                    "usgovarizona",
                    "usgovtexas",
                    "chinanorth",
                    "chinanorth2",
                    "brazilsouth",
                ],
                "awsRegions": ["ap-south-1", "us-west-1", "us-east-1", "us-west-2"],
                "gcpRegions": ["us-central1"],
                "vmHubGeoPoint": {"type": "Point", "coordinates": [-119.852, 47.233]},
                "privateLinkServiceIds": [
                    "/subscriptions/f8b96ec7-cf11-4ae2-ab75-9e7755a00594/resourceGroups/dev1_westus2/providers/Microsoft.Network/privateLinkServices/dev1b-westus2-cp103a-privatelink"
                ],
            }
        ],
    }
    try:
        # ret = org_service.datacenter.create(payload1)

        from hcs_core.sglib.hcs_client import hcs_client

        profile_data = profile.current()
        url = profile_data.hcs.url
        custom_auth = profile_data.csp
        custom_client = hcs_client(url=url, custom_auth=custom_auth)
        ret = custom_client.post("/org-service/v1/datacenters", payload1)
        print(ret)
        log.good("Datacenter registered.")
    except Exception as e:
        if "already exists" in error_details(e):
            log.info("Datacenter already exists. Skipping creation.")
        else:
            raise


@step
def _create_org_details():
    namespace = profile.name()
    payload2 = {
        "customerName": f"{namespace}-dev",
        "customerType": "INTERNAL",
        "orgId": os.getenv("ORG_ID"),
        "wsOneOrgId": "pseudo-ws1-org-id",
    }
    try:
        ret = org_service.details.create(payload2)
        print(ret)
        log.good("Org details created.")
    except Exception as e:
        if "already exist" in error_details(e):
            log.info("Org details already exist. Skipping creation.")
        else:
            raise


@step
def _create_org_location_mapping():
    payload3 = {"location": "US", "orgId": os.getenv("ORG_ID")}
    ret = org_service.orglocationmapping.create(payload3)
    print(ret)
    log.good("Org location mapping created.")


@step
def _create_idp():
    org_id = os.getenv("ORG_ID")
    try:
        existing_map = auth.admin.get_org_idp_map(org_id=org_id)
    except Exception as e:
        fail(f"Failed to fetch existing IDP map: {error_details(e)}")
    # Check if IDP mapping already exists
    if existing_map and existing_map.get("idpType") == "AZURE" and existing_map.get("idpTenantDomain") == os.getenv("IDP_TENANT_DOMAIN"):
        log.info("IDP already exists. Skipping creation.")
    else:
        try:
            payload = {
                "userName": os.getenv("IDP_USER_NAME"),
                "password": os.getenv("IDP_PASSWORD"),
                "idpType": "AZURE",
                "domains": [os.getenv("IDP_USER_NAME").split("@")[1]],
                "force": True,
                "redirectUri": f"{profile.current().hcs.url}/auth/v1/callback",
                "orgId": org_id,
                "idpTenantDomain": os.getenv("IDP_TENANT_DOMAIN"),
            }
            ret = auth.admin.create_org_idp_map_internal(payload)
            print(ret)
            log.good("IDP set up.")
        except Exception as e:
            print(e)
            fail("IDP credentials require 2FA which is currently not supported. Please manually set up your IDP in Astro.")


@step
def _restart_services():
    kubectl("rollout restart deployment portal-deployment", ignore_error=True)
    kubectl("rollout restart statefulset vmhub-statefulset", ignore_error=True)
    kubectl("rollout restart statefulset connection-service-statefulset", ignore_error=True)
    kubectl("rollout restart statefulset clouddriver-statefulset", ignore_error=True)

    # TODO: not sure why restart of this deployment failed
    # kubectl("rollout restart deployment infra-vsphere-twin-deployment")

    log.good("Services restarted.")


@step
def _wait_for_services_restart():
    log.info("Waiting for services to restart...")
    # TODO: wait for actual services to be ready
    time.sleep(60)


def _map_fqdn_to_lb(fs_name):
    orgId = os.getenv("ORG_ID")
    deployment_id = os.getenv("DEPLOYMENT_ID")
    for uag in list_uags(orgId):
        if uag.get("name") == deployment_id and uag.get("orgId") == orgId:
            print("The next step requires adding FQDN mapping. Run the following command in another window:")
            print(f'echo "{uag["loadBalancer"]["ipAddress"]} {os.getenv("UAG_FQDN")}" | sudo tee -a /etc/hosts')
            log.info(
                f"After that, you can view your desktops at https://{fs_name}.fs.devframe.cp.horizon.omnissa.com/appblast/endpoint/appblast"
            )
            break
