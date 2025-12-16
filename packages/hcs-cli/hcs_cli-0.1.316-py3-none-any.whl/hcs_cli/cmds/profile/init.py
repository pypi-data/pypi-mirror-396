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
from hcs_core.ctxp import profile

import hcs_cli.support.profile as profile_support


@click.command()
@click.option("--name", "-n", type=str, required=False, help="Name of the profile.")
@click.option("--dev/--no-dev", type=bool, default=False, help="Initialize default development profiles.")
@click.option("--feature-stack", "-fs", type=str, required=False, help="A profile for feature stack.")
@click.option("--org", type=str, required=False, help="Set initial property")
@click.option("--client-id", type=str, required=False, help="Set initial property")
@click.option("--client-secret", type=str, required=False, help="Set initial property")
@click.option("--api-token", type=str, required=False, help="Set initial property")
@click.option("--basic", type=str, required=False, help="Set initial property")
@click.option("--copy", type=str, required=False, help="Copy an existing profile to a new profile with the given name.")
def init(name: str, dev: bool, feature_stack: str, org: str, client_id: str, client_secret: str, api_token: str, basic: str, copy: str):
    """Init profile.

    Examples:

        hcs profile init --name lab

        hcs profile init --feature-stack <name> --org <orgId> --client-id <id> --client-secret <secret>
    """

    profile_support.ensure_default_production_profile()

    if dev:
        profile_support.ensure_dev_profiles()
        print()
        print("Next step:")
        print("  'hcs profile --help' : to know profile operations.")
        print("  'hcs profile use'    : to swtich profile.")
        print("  'hcs login --help'   : to complete authentication for the current profile.")
        return

    def _override(data: dict):
        csp = data["csp"]
        if org:
            csp["orgId"] = org
        if client_id:
            csp["clientId"] = client_id
        if client_secret:
            csp["clientSecret"] = client_secret
        if api_token:
            csp["apiToken"] = api_token
        if basic:
            csp["basic"] = basic
        return data

    data = None
    if feature_stack:
        if not name:
            name = feature_stack
        data = profile_support.get_dev_profile_template()
        url = f"https://{feature_stack}.fs.devframe.cp.horizon.omnissa.com"
        data["hcs"]["url"] = url
        for r in data["hcs"]["regions"]:
            r["url"] = url
    elif copy:
        data = profile_support.get_profile_template(copy)
        if not data:
            return f"Profile template {copy} not found.", 1
    else:
        data = profile_support.get_default_profile_template()

    data = _override(data)
    if not name:
        name = "default"
    profile.create(name, data, overwrite=True)
