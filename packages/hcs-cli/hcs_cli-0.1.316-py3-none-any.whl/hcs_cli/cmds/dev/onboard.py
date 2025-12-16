from time import sleep, time

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import profile
from hcs_core.ctxp.util import error_details
from InquirerPy import inquirer
from InquirerPy.base import Choice

import hcs_cli.cmds.dev.util.github_helper as github_helper
from hcs_cli.cmds.dev.fs.init import _retrieve_config_from_nightly_repo
from hcs_cli.cmds.dev.util.log import fail
from hcs_cli.support.exec_util import run_cli


@click.group()
def onboard():
    """Setup express onboarding deployment."""
    pass


@onboard.command(name="start")
@click.option("--mode", type=click.Choice(["exp-single-session", "exp-multi-session"]), help="Onboarding mode")
@cli.org_id
@click.option("--fs", is_flag=True, help="Update config to fit for feature stack (e.g. avoid private link)")
def start_onboard(mode: str, org: str, fs: bool):
    """Start express onboarding process."""

    org_id = cli.get_org_id(org)

    if not mode:
        choices = [
            Choice(value="exp-single-session", enabled=True, name="Express onboarding - single session"),
            Choice(value="exp-multi-session", enabled=True, name="Express onboarding - multi-session"),
        ]
        mode = inquirer.select(
            message="Choose mode:",
            choices=choices,
        ).execute()

    click.echo(f"Deploying: {mode}")

    if mode == "exp-single-session":
        config_file = (
            "src/test/resources/com/vmware/integration/sg/payloads/orchestrator/express_onboarding_single_session_deployment_payload.txt"
        )
    elif mode == "exp-multi-session":
        config_file = (
            "src/test/resources/com/vmware/integration/sg/payloads/orchestrator/express_onboarding_multi_session_deployment_payload.txt"
        )
    else:
        return f"Unknown mode: {mode}", 1

    _check_is_prod_profile()

    url = "https://github.com/euc-eng/horizonv2-sg.nightly-tests.git"
    with github_helper.repo(url) as repo:
        payload = repo.get(config_file, format="json")

    if fs:
        payload["edge"]["enablePrivateEndpoint"] = False

    ret = run_cli(
        f"hcs api --post /deployment-orchestrator/v1/deployments?org_id={org_id}", inherit_output=False, input=payload, output_json=True
    )
    _show_deployment_status(ret)
    _wait_for_deployment_complete(org_id)

    click.echo("Onboard complete.")


@onboard.command()
@cli.org_id
def show(org: str):
    """Show express onboarding deployment status in a view."""
    org_id = cli.get_org_id(org)
    deployment = run_cli(f"hcs api /deployment-orchestrator/v1/deployments?org_id={org_id}", output_json=True)
    if not deployment:
        click.echo("No express onboarding deployment found.")
        return

    _show_deployment_status(deployment)


@onboard.command()
@cli.org_id
def get(org: str):
    """Get express onboarding deployment details."""
    org_id = cli.get_org_id(org)
    return run_cli(f"hcs api /deployment-orchestrator/v1/deployments?org_id={org_id}", output_json=True)


@onboard.command()
@click.option("--all/--express-only", default=False, is_flag=True, help="Delete all resources or only express onboarding deployment")
@cli.org_id
def delete(all: bool, org: str):
    """Delete express onboarding deployment and optionally all resources."""
    org_id = cli.get_org_id(org)
    if all:
        profile_data = profile.current()
        url = profile_data.hcs.url
        org = run_cli("hcs org get", output_json=True)

        click.secho("⚠️ This will delete all resources.", fg="bright_red")
        click.echo("     Profile name: " + profile.name())
        click.echo("     HCS URL: " + url)
        click.echo("     Org: " + org["orgName"])
        input = click.prompt("Enter org name to continue, or Ctrl+C to abort", default="", show_default=False)
        if input.lower() != org["orgName"].lower():
            return "Org name does not match. Aborting.", 1

    deployment_id = _delete_express_onboarding_deployment(org_id)

    if all:
        _delete_all("pool", org_id)
        _delete_all("template", org_id)
        _delete_all("edge", org_id)
        _delete_all("provider", org_id)
        _delete_all("site", org_id)
        _delete_all_sso_configs(org_id)
        _delete_all("ad", org_id)

    _wait_for_deployment_deletion(deployment_id, org_id)

    click.echo("Reset complete.")


def _delete_express_onboarding_deployment(org_id: str):
    deployment = run_cli(f"hcs api /deployment-orchestrator/v1/deployments?org_id={org_id}", output_json=True)
    if not deployment:
        click.echo("No express onboarding deployment found.")
        return

    deployment_id = deployment.get("id")
    click.echo("Deleting express onboarding deployment resources...")
    try:
        run_cli(
            f"hcs api --delete /deployment-orchestrator/v1/resources?org_id={org_id}",
            inherit_output=False,
            raise_on_error=True,
            log_error=False,
        )
    except Exception as e:
        click.secho(error_details(e), fg="bright_black")
    click.echo("Deleting express onboarding deployment: " + deployment_id)
    try:
        run_cli(
            f"hcs api --delete /deployment-orchestrator/v1/deployments?org_id={org_id}",
            inherit_output=False,
            raise_on_error=True,
            log_error=False,
        )
    except Exception as e:
        click.secho(error_details(e), fg="bright_black")
    _show_deployment_status(deployment)
    return deployment_id


def _wait_for_deployment_complete(org_id):
    timeout = 60 * 20
    start = time()
    while True:
        sleep(60)
        deployment = run_cli(
            f"hcs api /deployment-orchestrator/v1/deployments?org_id={org_id}", output_json=True, show_command=False, inherit_output=False
        )
        _show_deployment_status(deployment)
        elapsed = time() - start
        if elapsed > timeout:
            click.secho("Timeout waiting for express onboarding deployment to be deleted.", fg="bright_red")
        # "NOT_YET_SUBMITTED"
        # 1"SUBMITTED"
        # 2"IN_PROGRESS"
        # 3"SUCCESS"
        # 4"FAILURE"
        # 5"DELETED"
        # 6"DELETING"
        status = deployment.get("deploymentStatus")
        if status == "SUCCESS":
            click.echo("✅ Success")
            return
        if status in ["FAILURE", "DELETED"]:
            click.echo("❌ Express onboarding deployment completed with status: " + status)
            return


def _wait_for_deployment_deletion(deployment_id, org_id):
    if not deployment_id:
        return

    timeout = 60 * 20
    start = time()
    while True:
        sleep(60)
        try:
            run_cli(
                f"hcs api --delete /deployment-orchestrator/v1/deployments?org_id={org_id}",
                inherit_output=False,
                raise_on_error=True,
                log_error=False,
                show_command=False,
            )
        except Exception as e:
            click.secho(error_details(e), fg="bright_black")
            sleep(5)
        deployment = run_cli(f"hcs api /deployment-orchestrator/v1/deployments?org_id={org_id}", output_json=True, show_command=False)
        if not deployment:
            click.echo("Express onboarding deployment deleted.")
            break
        elapsed = time() - start
        if elapsed > timeout:
            click.secho("Timeout waiting for express onboarding deployment to be deleted.", fg="bright_red")
        _show_deployment_status(deployment)


def _show_deployment_status(deployment):
    """Display deployment status with live updating UI that clears previous output."""
    import os
    from datetime import datetime

    # Clear the terminal
    os.system("clear" if os.name == "posix" else "cls")

    # Header
    click.secho("🚀 Express Onboarding Deployment Status", fg="bright_blue", bold=True)
    click.secho("=" * 50, fg="bright_blue")

    # Deployment info
    deployment_id = deployment.get("id", "N/A")
    deployment_status = deployment.get("deploymentStatus", "UNKNOWN")
    location = deployment.get("location", "N/A")
    created_at = deployment.get("createdAt", "N/A")
    expire_at = deployment.get("expireAt", "N/A")

    # Format timestamps
    if created_at != "N/A":
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            created_at = created_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            pass

    if expire_at != "N/A":
        try:
            expire_dt = datetime.fromisoformat(expire_at.replace("Z", "+00:00"))
            expire_at = expire_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            pass

    click.echo(f"Deployment ID: {deployment_id}")
    click.echo(f"Overall Status: {_get_status_emoji(deployment_status)} {deployment_status}")
    click.echo(f"Location: {location}")
    click.echo(f"Created: {created_at}")
    click.echo(f"Expires: {expire_at}")
    click.echo()

    # Resources status
    resources = deployment.get("resources", {})
    if resources:
        click.secho("📋 Resource Status:", fg="bright_yellow", bold=True)
        click.secho("-" * 80, fg="bright_yellow")

        # Define resource display order for better UX
        resource_order = [
            "PROVIDER_INSTANCE",
            "PROVIDER_PREFERENCES",
            "SITE",
            "ACTIVE_DIRECTORY",
            "EDGE",
            "POOL_GROUP",
            "POOL",
            "IMAGE",
            "UAG",
            "ENTITLEMENT",
        ]

        # Show resources in order, then any remaining ones
        displayed = set()
        for resource_type in resource_order:
            if resource_type in resources:
                _display_resource_status(resource_type, resources[resource_type])
                displayed.add(resource_type)

        # Show any remaining resources not in the predefined order
        for resource_type, resource_data in resources.items():
            if resource_type not in displayed:
                _display_resource_status(resource_type, resource_data)

    # Options
    options = deployment.get("options", {})
    if options:
        click.echo()
        click.secho("⚙️  Deployment Options:", fg="bright_cyan")
        for key, value in options.items():
            click.echo(f"  {key}: {value}")

    click.echo()
    click.secho(f"Last updated: {datetime.now().strftime('%H:%M:%S')}", fg="bright_black")


def _display_resource_status(resource_type, resource_data):
    """Display individual resource status with proper formatting."""
    status = resource_data.get("resourceStatus", "UNKNOWN")
    resource_id = resource_data.get("id", "N/A")
    error_details = resource_data.get("errorDetails", [])

    # Format resource name for better readability
    display_name = resource_type.replace("_", " ").title()

    # Status with emoji and color
    status_emoji = _get_status_emoji(status)
    if status == "SUCCESS":
        status_color = "bright_green"
    elif status == "IN_PROGRESS":
        status_color = "bright_yellow"
    elif status in ["FAILED", "ERROR"]:
        status_color = "bright_red"
    elif status == "NOT_YET_SUBMITTED":
        status_color = "bright_black"
    elif status in ["DELETED", "REMOVED"]:
        status_color = "bright_magenta"
    elif status in ["DESTROYING", "TERMINATING", "CLEANUP"]:
        status_color = "bright_cyan"
    else:
        status_color = "white"

    # Display resource line
    click.echo(f"  {status_emoji} ", nl=False)
    click.secho(f"{display_name:<20}", fg="bright_white", nl=False)
    click.secho(f" {status:<20}", fg=status_color, nl=False)

    if resource_id != "N/A":
        click.secho(f" (ID: {resource_id})", fg="bright_black", nl=False)

    click.echo()

    # Show error details if any
    if error_details:
        for error in error_details:
            click.secho(f"    ❌ {error}", fg="bright_red")


def _get_status_emoji(status):
    """Return appropriate emoji for status."""
    status_emojis = {
        "SUCCESS": "✅",
        "IN_PROGRESS": "⏳",
        "FAILED": "❌",
        "ERROR": "❌",
        "NOT_YET_SUBMITTED": "⏸️",
        "SUBMITTED": "📤",
        "PENDING": "⏳",
        "COMPLETED": "✅",
        "CANCELLED": "🛑",
        "TIMEOUT": "⏰",
        "DELETED": "🗑️",
        "REMOVED": "🗑️",
        "DESTROYING": "💥",
        "TERMINATING": "💥",
        "CLEANUP": "🧹",
    }
    return status_emojis.get(status, "⚪")


def _delete_all_sso_configs(org_id: str):
    sso_configs = run_cli(f"hcs api /admin/v1/sso-configurations?org_id={org_id} --all-pages --ids", output_json=True)
    for id in sso_configs:
        run_cli(f"hcs api --delete /admin/v1/sso-configurations/{id}?org_id={org_id}", inherit_output=False)


def _delete_all(entity_type: str, org_id: str):
    click.echo(f"Deleting all {entity_type}s...")
    items = run_cli(f"hcs {entity_type} list --ids --org {org_id}", output_json=True)
    if not items:
        return

    for id in items:
        try:
            run_cli(f"hcs {entity_type} delete {id} -y --org {org_id}", inherit_output=False)
        except Exception as e:
            click.secho(f"Error deleting {entity_type} {id}: {e}. Retry in 10 seconds...", fg="bright_red")
            sleep(10)
            run_cli(f"hcs {entity_type} delete {id} -y --org {org_id}", inherit_output=True)
    start = time()
    item_count = -1
    while True:
        items = run_cli(f"hcs {entity_type} list --ids --org {org_id}", output_json=True)
        if len(items) == 0:
            break
        if len(items) != item_count:
            item_count = len(items)
            start = time()
        elif time() - start > 600:
            fail(f"Timeout waiting for {entity_type} to be deleted. Remaining: {items}")
        click.secho(f"Waiting for {entity_type} to be deleted... {len(items)} remaining", fg="bright_black")
        sleep(60)


def _check_is_prod_profile():
    profile_data = profile.current()
    url = profile_data.hcs.url
    if url.startswith("https://cloud") and url.endswith(".horizon.omnissa.com"):
        return

    click.echo("⚠️ You are not using the production profile.")
    click.echo("     Profile name: " + profile.name())
    click.echo("     HCS URL: " + url)
    click.echo("Onboarding is only tested in production profile.")
    click.prompt("Press Enter to continue or Ctrl+C to abort", default="", show_default=False)
