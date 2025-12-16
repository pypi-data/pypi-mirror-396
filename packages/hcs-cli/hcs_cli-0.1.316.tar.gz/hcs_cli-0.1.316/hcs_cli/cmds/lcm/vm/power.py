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

import time

import click
import hcs_core.sglib.cli_options as cli
import yumako
from hcs_core.ctxp import CtxpException

import hcs_cli.service.inventory as inventory
import hcs_cli.service.lcm as lcm
from hcs_cli.support.param_util import parse_vm_path


def _get_vm(template_id, vm_id, org_id):
    vm_info = _get_vm(template_id, vm_id, org_id)
    if "powerState" not in vm_info:
        # This happens for Akka VMs.
        vm_info = inventory.vm.get(template_id, vm_id, org_id)
    return vm_info


def _wait_for_power_state(template_id, vm_id, org_id, wait, state):
    seconds = yumako.time.duration(wait)
    state = state.lower()

    start = time.time()
    while True:
        vm = _get_vm(template_id, vm_id, org_id)
        if vm["powerState"].lower() == state:
            return vm
        elasped = time.time() - start
        remaining = seconds - elasped
        delay = min(remaining, 5)
        if remaining <= 0:
            raise CtxpException(f"Timeout waiting for VM {vm_id} to reach state '{state}'")
        time.sleep(delay)


@click.command()
@click.argument("vm_path", type=str, required=False)
@cli.org_id
@cli.wait
def poweron(vm_path: str, org: str, wait: str, **kwargs):
    """Power on a VM."""
    template_id, vm_id = parse_vm_path(vm_path)
    org_id = cli.get_org_id(org)
    lcm.vm.power_on(template_id, vm_id, org_id, **kwargs)
    if wait != "0":
        return _wait_for_power_state(template_id, vm_id, org_id, wait, "PoweredOn")
    return _get_vm(template_id, vm_id, org_id)


@click.command()
@click.argument("vm_path", type=str, required=False)
@cli.org_id
@cli.wait
def poweroff(vm_path: str, org: str, wait: str, **kwargs):
    """Power off a VM."""
    template_id, vm_id = parse_vm_path(vm_path)
    org_id = cli.get_org_id(org)
    lcm.vm.power_off(template_id, vm_id, org_id, **kwargs)
    if wait != "0":
        return _wait_for_power_state(template_id, vm_id, org_id, wait, "PoweredOff")
    return _get_vm(template_id, vm_id, org_id)


@click.command()
@click.argument("vm_path", type=str, required=False)
@cli.org_id
@cli.wait
def restart(vm_path: str, org: str, wait: str, **kwargs):
    """Restart a VM."""
    template_id, vm_id = parse_vm_path(vm_path)
    org_id = cli.get_org_id(org)
    lcm.vm.restart(template_id, vm_id, org_id, **kwargs)
    if wait != "0":
        time.sleep(5)
        return _wait_for_power_state(template_id, vm_id, org_id, wait, "PoweredOn")
    return _get_vm(template_id, vm_id, org_id)


@click.command()
@click.argument("vm_path", type=str, required=False)
@cli.org_id
@cli.wait
def shutdown(vm_path: str, org: str, wait: str, **kwargs):
    """Shutdown a VM."""
    template_id, vm_id = parse_vm_path(vm_path)
    org_id = cli.get_org_id(org)
    lcm.vm.shutdown(template_id, vm_id, org_id, **kwargs)
    if wait != "0":
        return _wait_for_power_state(template_id, vm_id, org_id, wait, "PoweredOff")
    return _get_vm(template_id, vm_id, org_id)
