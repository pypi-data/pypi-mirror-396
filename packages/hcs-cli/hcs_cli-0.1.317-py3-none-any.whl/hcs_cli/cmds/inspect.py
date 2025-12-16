import click
from hcs_core.sglib import cli_options as cli

from hcs_cli.support import inspect_util


@click.command(hidden=True)
@cli.org_id
@click.option("--template", "-t", type=str, required=False)
@click.option("--provider", "-p", type=str, required=False)
def inspect(org: str, template: str, provider: str, **kwargs):
    """Inspect the template."""
    org_id = cli.get_org_id(org)

    if template:
        # inspect template
        return inspect_util.inspect_template(org_id, template)

    if provider:
        # inspect provider
        return inspect_util.inspect_provider(org_id, provider)
    return "Must specify a resource to inspect.", 1
