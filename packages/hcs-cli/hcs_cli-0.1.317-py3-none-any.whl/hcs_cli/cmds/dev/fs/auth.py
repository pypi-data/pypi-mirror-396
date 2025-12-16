import click
from hcs_core.ctxp import profile

from hcs_cli.cmds.dev.fs.helper.credential_helper import get_client_credential_from_k8s_and_update_profile
from hcs_cli.cmds.dev.util import log

fail = log.fail


@click.command()
@click.option("--clear", "-c", is_flag=True, default=False, help="Reset the current profile auth.")
def auth(clear, **kwargs):
    """Update the current profile with feature stack service credentials from k8s."""

    profile_data = profile.current()
    if clear:
        updated = False
        if "override" in profile_data:
            del profile_data["override"]
            updated = True
        if "auth" in profile_data:
            del profile_data["auth"]
            updated = True
        if updated:
            profile.save()
    else:
        print("URL:", profile_data.hcs.url)
        get_client_credential_from_k8s_and_update_profile()
    return profile_data
