import click
from hcs_core.ctxp import profile
from hcs_core.ctxp.util import error_details

from hcs_cli.cmds.dev.fs.helper.k8s_util import validate_kubeconfig
from hcs_cli.cmds.dev.util import log

fail = log.fail


def validate_fs_profile():
    url = profile.current().hcs.url
    if url.find(".fs.devframe.cp.horizon.omnissa.com") == -1:
        fail("This command is only available on feature stack development environments. Current URL: " + url)


def validate_fs_kubeconfig():
    fs_name = profile.name()
    try:
        if not validate_kubeconfig(fs_name, raise_on_error=False):
            pass
    except Exception as e:
        print(error_details(e))
        fail(
            "Feature stack kubectl config is not set.\n"
            "Recovery options:\n"
            "  Download and copy feature stack kubeconfig to ~/.kube/config, or ~/.kube/_fs_config"
        )
