import json
import random
import sys

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import recent

import hcs_cli.service.lcm as lcm
from hcs_cli.support import constant


@click.command()
@click.option(
    "--id",
    "-i",
    type=str,
    required=False,
    help="",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(constant.provider_label_lcm, case_sensitive=False),
    required=False,
    help="Provider label. Default: Azure.",
)
@click.option(
    "--name",
    "-n",
    type=str,
    required=False,
    help="",
)
@click.option(
    "--description",
    "-d",
    type=str,
    required=False,
    help="",
)
@click.option(
    "--credential-id",
    type=str,
    required=False,
    help="",
)
@click.option(
    "--client-id",
    type=str,
    required=False,
    help="",
)
@click.option(
    "--client-secret",
    type=str,
    required=False,
    help="",
)
@click.option(
    "--tenant-id",
    type=str,
    required=False,
    help="",
)
@click.option(
    "--file",
    "-f",
    type=click.File("rt"),
    default=sys.stdin,
    help="Specify the provider file name. If not specified, STDIN will be used.",
)
@cli.org_id
def create(
    id: str,
    type: str,
    name: str,
    description: str,
    credential_id: str,
    client_id: str,
    client_secret: str,
    tenant_id: str,
    file: str,
    org: str,
    **kwargs,
):
    """Create a LCM provider"""

    if not type:
        type = "AZURE"
    else:
        type = type.upper()

    if type == "ZEROCLOUD":
        data = {
            "id": id if id else _rand_id(8),
            "type": type,
            "orgId": cli.get_org_id(org),
            "name": name,
            "description": description,
        }
    elif credential_id:
        data = {
            "id": id if id else _rand_id(8),
            "type": type,
            "orgId": cli.get_org_id(org),
            "name": name,
            "description": description,
            "credentialId": credential_id,
        }
    elif client_id or client_secret or tenant_id:
        if type != "AZURE":
            raise click.BadParameter("client-id is only supported for Azure provider.")
        if not client_id:
            raise click.BadParameter("client-id is required for client-secret.")
        if not client_secret:
            raise click.BadParameter("client-secret is required for client-id.")
        if not tenant_id:
            raise click.BadParameter("tenant-id is required for Azure provider.")

        data = {
            "id": id if id else _rand_id(8),
            "type": type,
            "orgId": cli.get_org_id(org),
            "name": name,
            "description": description,
            "credentialId": credential_id,
            "tenantId": tenant_id,
            "credentials": [
                {
                    "clientId": client_id,
                    "clientSecret": client_secret,
                }
            ],
        }
    else:
        with file:
            payload = file.read()

        try:
            data = json.loads(payload)
        except Exception as e:
            msg = "Invalid data: " + str(e)
            return msg, 1

    ret = lcm.provider.create(data)
    recent.set("provider", ret["id"])
    return ret


def _rand_id(n: int):
    return "".join(random.choices("abcdefghijkmnpqrstuvwxyz23456789", k=n))
