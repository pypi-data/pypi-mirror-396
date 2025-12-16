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

import json
import os
import tempfile

from hcs_core.plan import actions
from hcs_core.util import pki_util


def deploy(data: dict, state: dict, save_state) -> dict:

    cn = data["cn"]

    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"{cn}.json")

    if os.path.exists(file_path):
        print("reusing cert", file_path)
        with open(file_path, "rt") as file:
            cert = json.load(file)
    else:
        print("creating new cert")
        cert = pki_util.generate_self_signed_cert(cn)
        with open(file_path, "wt") as file:
            json.dump(cert, file)
    return cert


def refresh(data: dict, state: dict) -> dict:
    pass


def decide(data: dict, state: dict):
    return actions.skip


def destroy(data: dict, state: dict, force: bool) -> dict:
    # fqdn = data['fqdn']
    # temp_dir = tempfile.gettempdir()
    # file_path = os.path.join(temp_dir, f"{fqdn}.json")
    # os.unlink(file_path)
    pass


def eta(action: str, data: dict, state: dict):
    return "2s"
