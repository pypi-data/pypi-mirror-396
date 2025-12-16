import click
from hcs_core.sglib import cli_options as cli


@click.command()
@cli.org_id
@click.option(
    "--from",
    "from_param",
    type=str,
    required=False,
    default="-12h",
    help="Sepcify the from date. E.g. '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
@click.option(
    "--to",
    type=str,
    required=False,
    default="now",
    help="Sepcify the to date. E.g. 'now', or '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
def template(org: str, from_param: str, to: str):
    """Analyse an org."""
    pass
