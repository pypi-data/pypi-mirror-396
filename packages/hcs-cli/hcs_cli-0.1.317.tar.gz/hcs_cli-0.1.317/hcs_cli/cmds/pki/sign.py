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

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.util import pki_util

from hcs_cli.service.pki import certificate


def _write_file(file_path: str, text: str):
    with open(file_path, "w") as file:
        file.write(text)


@click.command()
@click.argument("resource-name", type=str, required=True)
@click.option(
    "--key-length",
    type=int,
    default=2048,
    required=False,
    help="Private key length",
)
@click.option(
    "--validity-in-days",
    type=int,
    default=365,
    required=False,
    help="Days before the certificate expires",
)
@click.option("--ca-label", type=str, default="omnissa")
@click.option(
    "--no-org",
    is_flag=True,
    help="Sign the certificate without the org signing CA in the chain.",
    default=False,
)
@cli.org_id
def sign(resource_name: str, key_length: int, org: str, validity_in_days: int, ca_label: str, no_org: bool):
    """Create certificate for a specific resource. This command will generate cert chain and private key file stored in the current directory."""
    org_id = cli.get_org_id(org)
    csr_pem, private_key_pem = pki_util.generate_CSR(resource_name, key_length=key_length)
    if no_org:
        ret = certificate.sign_resource_cert_without_org(org_id, csr_pem, validity_in_days, ca_label)
    else:
        ret = certificate.sign_resource_cert_with_org(org_id, csr_pem, validity_in_days, ca_label)

    key_file = resource_name + ".key"
    print("Private key: " + key_file)
    _write_file(key_file, private_key_pem)

    print("CSR: " + resource_name + ".csr")
    _write_file(resource_name + ".csr", csr_pem)

    client_cert_chain_file = resource_name + ".crt"
    print("Signed certificate: " + client_cert_chain_file)
    _write_file(client_cert_chain_file, ret)

    print("To view the cert details:")
    print(f"  openssl x509 -text -noout -in {client_cert_chain_file}")

    print("To view the private key details:")
    print(f"  openssl rsa -text -noout -in {key_file}")
