import json
import os

from hcs_cli.cmds.dev.util import log
from hcs_cli.support.exec_util import exec

fail = log.fail

_fs_kubeconfig = os.path.expanduser("~/.kube/_fs_config")
_kubectl_command_with_config_file = "kubectl --kubeconfig " + _fs_kubeconfig
_kubectl_command_default = "kubectl"
_kubectl_command = _kubectl_command_default


def kubectl(command: str, ignore_error: bool = False, get_json: bool = False, input: str = None, show_command: bool = True):
    if get_json:
        command.find("-ojson") == -1 and command.find("--output=json") == -1
        command += " -ojson"
    ret = exec(
        _kubectl_command + " " + command,
        log_error=not ignore_error,
        raise_on_error=not ignore_error,
        input=input,
        show_command=show_command,
        env=os.environ.copy(),
    )
    if ignore_error and ret.returncode != 0:
        return None
    if get_json:
        try:
            return json.loads(ret.stdout)
        except json.JSONDecodeError as e:
            fail(f"Failed to parse JSON output from kubectl command: {e}\nOutput: {ret.stdout}")
    return ret


def validate_kubeconfig(fs_name: str, try_default_config: bool = True, raise_on_error: bool = True):

    if os.path.exists(_fs_kubeconfig):
        log.info("Using feature stack kubeconfig: " + _fs_kubeconfig)
        global _kubectl_command
        _kubectl_command = _kubectl_command_with_config_file
    else:
        log.info("Using default kubeconfig (because " + _fs_kubeconfig + " does not exist)")

    good = False
    ret = kubectl("config view --minify --output jsonpath={..namespace}")
    output = ret.stdout.strip()
    if output == fs_name:
        log.good("kubectl config context: " + fs_name)
        good = True
    else:
        log.trivial("Incorrect namespace: " + output)
        if try_default_config:
            _kubectl_command = _kubectl_command_default
            ret = kubectl("config view --minify --output jsonpath={..namespace}")
            output = ret.stdout.strip()
            if output == fs_name:
                log.good("kubectl config context: " + fs_name)
                good = True
            else:
                log.trivial("Incorrect namespace: " + output)
    if not good:
        if raise_on_error:
            fail(
                "kubectl config namespace is not set to feature stack name."
                f"  Expected: {fs_name}\n"
                f"  Current: {output}\n\n"
                f"Recovery options:\n"
                f"  Copy feature stack config to ~/.kube/_fs_config (or ~/.kube/config).\n"
            )
        else:
            return False

    ret = kubectl("get po", ignore_error=True)
    if ret.returncode != 0:
        if raise_on_error:
            fail("Fail connecting to k8s. Check config.")
        else:
            return False

    log.good("k8s connection")
    return True
