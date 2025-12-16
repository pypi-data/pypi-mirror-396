"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64

import click
from hcs_core.util import pki_util

from hcs_cli.service.vmhub import credentials as otp_service


@click.command()
@click.option(
    "--region",
    type=str,
    default=None,
    required=False,
    help="Specify region name",
)
@click.option("--ca-label", "-c", type=str, required=False, default="omnissa", help="CA label to use for the cert.")
@click.option("--save-cert", "-s", is_flag=True, default=False, help="Save the received cert to a file.")
@click.argument("resource-name", type=str, required=True)
@click.argument("otp", type=str, required=True)
def redeem(region: str, resource_name: str, otp: str, ca_label: str, save_cert: bool):
    """Redeem OTP with CSR, receive resource cert."""

    otp_service.use_region(region)
    csr_pem, private_key_pem = pki_util.generate_CSR(resource_name)

    ret = otp_service.redeem(resource_name, otp, csr_pem, ca_label)
    if not ret:
        return "Failed to redeem OTP", 1
    if save_cert:
        _write_file("./ca.crt", ret.caCrt)
        _write_file(f"./{resource_name}.crt", ret.clientCrt)
        _write_file(f"./{resource_name}.key", private_key_pem, decode_base64=False)
        return
    else:
        ret.private_key = private_key_pem
        return ret


def _write_file(file_name: str, data: str, decode_base64: bool = True) -> None:
    text = base64.b64decode(data).decode("utf-8") if decode_base64 else data
    with open(file_name, "w") as f:
        f.write(text)
    click.echo(f"Writing file: {file_name}")
