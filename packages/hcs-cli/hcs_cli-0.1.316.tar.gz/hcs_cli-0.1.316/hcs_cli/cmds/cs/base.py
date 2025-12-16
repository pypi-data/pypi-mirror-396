import click

from hcs_cli.service import cs


@click.command()
@click.option("--region", "-r", required=False, help="Region to use for the command")
def keys(region: str, **kwargs):
    """List JWKS"""
    return cs.region(region).keys(**kwargs)["keys"]
