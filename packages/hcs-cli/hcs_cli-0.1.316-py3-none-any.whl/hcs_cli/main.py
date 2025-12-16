#!/usr/bin/env -S python -W ignore

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


import logging
import os
import os.path as path
import sys
import warnings

# Suppress urllib3 SSL warnings at the earliest possible point
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL 1.1.1+.*", category=UserWarning)
os.environ["PYTHONWARNINGS"] = "ignore::UserWarning:urllib3.*"

import click
from dotenv import load_dotenv
from yumako import env

_script_dir = path.abspath(path.join(path.dirname(path.realpath(__file__)), "."))
_module_dir = _script_dir
if __name__ == "__main__":
    _cli_dir = path.dirname(_module_dir)
    sys.path.append(_cli_dir)

import hcs_core.ctxp as ctxp

# -----------------------------------------------------------
import hcs_core.ctxp.logger as logger

logger.setup()
logging.getLogger("charset_normalizer").setLevel(logging.WARN)
logging.getLogger("csp").setLevel(logging.INFO)
logging.getLogger("context").setLevel(logging.WARN)
logging.getLogger("init").setLevel(logging.WARN)
logging.getLogger("profile").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)
logging.getLogger("urllib3").setLevel(logging.ERROR)
# logging.getLogger("hcs_core.sglib.login_support").setLevel(logging.DEBUG)
# logging.getLogger("login_support").setLevel(logging.DEBUG)
# -----------------------------------------------------------
import hcs_core.sglib.ez_client as ez_client

ez_client._print_http_error = False

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(package_name="hcs-cli")
@click.option("--profile", "-p", type=str, required=False, help="Specify the profile to use. Optional.")
@click.option("--no-upgrade-check", is_flag=True, default=False, help="Check new version of HCS CLI.")
@click.option("--no-telemetry", is_flag=True, default=False, help="Disable telemetry collection")
def cli(profile: str, no_upgrade_check: bool, no_telemetry: bool, **kwargs):

    if not no_upgrade_check:
        _check_upgrade()

    if no_telemetry:
        ctxp.telemetry.disable()

    if profile:
        ctxp.profile._active_profile_name = profile

    # ensure the default profile is available during fresh start
    if ctxp.profile.name() == "default":
        import hcs_cli.support.profile as profile_support

        profile_support.ensure_default_production_profile()


def _check_upgrade():
    check_flag_from_env = env.bool("HCS_CLI_CHECK_UPGRADE", True)
    if not check_flag_from_env:
        return
    if len(sys.argv) > 1 and sys.argv[1] == "upgrade":
        return
    from hcs_core.util.versions import check_upgrade

    check_upgrade()


def main():
    config_path = path.join(_module_dir, "config")
    ctxp.init(app_name="hcs", config_path=config_path)
    commands_dir = path.join(_module_dir, "cmds")
    load_dotenv(".env")
    ctxp.init_cli(main_cli=cli, commands_dir=commands_dir)


if __name__ == "__main__":
    main()
