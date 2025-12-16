from typing import Callable

from hcs_cli.service import VM, template


def templates(org_id: str, fn_filter: Callable = None) -> list:
    """Return the list of templates."""
    ret = template.list(org_id, fn_filter=fn_filter)
    return ret


def vms(org_id: str, template_id: str) -> list:
    """Return the list of VMs in the template."""
    ret = VM.list(org_id, template_id)
    return ret
