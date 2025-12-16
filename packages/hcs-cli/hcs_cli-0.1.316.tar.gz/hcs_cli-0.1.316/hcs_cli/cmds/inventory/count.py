import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import recent

from hcs_cli.service import inventory


@click.command()
@cli.org_id
@click.argument("template_id", type=str, required=False)
def count(template_id: str, org: str):
    """Count template VMs"""
    template_id = recent.require("template", template_id)
    return inventory.count(template_id, cli.get_org_id(org))
