# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import json
import random
import sys
import time
from typing import Union

import click
from hcs_core.ctxp import profile
from yumako.time import display as display_time

from ohcs.lcm.verify.helper import context, create_pool, fail, get_akka_plan_file_path, step, trivial
from ohcs.common.utils import error_details, run_cli


@step(10)
def check_hcs_cli_availability():
    try:
        version = run_cli("hcs --version", inherit_output=False).stdout.strip()
        trivial(version)
    except Exception as e:
        trivial(error_details(e))
        fail("hcs-cli is not available.")


@step(11, "[Check Precondition] identify the current user organization from login session")
def identify_user_organization():
    try:
        org_info = run_cli("hcs org get", output_json=True)
    except Exception as e:
        trivial(error_details(e))

        click.echo("It seems the curernt login session is not valid.")
        click.prompt(
            "Press ENTER to launch browser to login Horizon Cloud Service...",
            prompt_suffix="",
            default="",
            show_default=False,
        )
        run_cli("hcs login")
        click.echo()
        trivial("Login successful")
        org_info = run_cli("hcs org get", output_json=True)

    context.org_id = org_info["orgId"]
    trivial(f"Organization: {org_info['orgName']} ({context.org_id})")


@step(12, "[Check Precondition] check HCS connectivity")
def check_hcs_connectivity():
    trivial(f"HCS URL: {profile.current().hcs.url}")
    try:
        run_cli("hcs site list --ids", output_json=True)
    except Exception as e:
        trivial(error_details(e))
        fail("HCS connectivity or authentication is not successful.")


def _cleanup_impl():
    trivial("Cleaning up test resources...")
    pool_ids = run_cli("hcs template list --search 'name $like lcm_test_' --ids", output_json=True)

    for pool_id in pool_ids:
        run_cli(f"hcs template delete -y {pool_id}", inherit_output=False, raise_on_error=False)

    first = True
    for pool_id in pool_ids:
        if first:
            first = False
            time_to_wait = "10m"
        else:
            time_to_wait = "1m"
        run_cli(f"hcs template delete -y -w{time_to_wait} {pool_id}", inherit_output=False, raise_on_error=False)

    if context.akka_deployment:
        trivial("Destroying Akka stack...")
        run_cli(f"hcs plan destroy -f {get_akka_plan_file_path()}")
        context.akka_deployment = None

    trivial("Test resources are cleaned up.")


@step(20)
def cleanup_previous_test_resources_if_any():
    _cleanup_impl()


@step(30, "[Resource] Verify or create provider")
def verify_or_create_provider():
    if context.user_provider_id:
        trivial(f"Verifying user specified provider: {context.user_provider_id}")
        provider_info = run_cli(f"hcs provider get {context.user_provider_id}", output_json=True, raise_on_error=False)

        if provider_info:
            context.provider_id = provider_info["id"]
            trivial(f"Provider: {context.provider_id} ({provider_info['type']}/{provider_info['name']})")
        else:
            fail(f"Provider: {context.user_provider_id} not found")
        return

    if context.mode_config == "builtin:akka":
        run_cli(f"hcs plan apply -f {get_akka_plan_file_path()}", output_json=False, inherit_output=True)
        deployment_info = run_cli("hcs plan output", output_json=True)
        trivial("Akka stack created successfully.")
        context.akka_deployment = deployment_info
        return

    if context.mode_config == "builtin:plugin-simulator":
        payload = {
            "orgId": context.org_id,
            "providerLabel": "custom",
            "name": "lcm-test",
            "edgeGatewayNeeded": False,
            "providerDetails": {
                "method": "ByCustomPlugin",
                "data": {"platformName": "testPlatform", "geoLocationLat": "37.38", "geoLocationLong": "-122"},
            },
        }
        provider_info = run_cli("hcs provider create", output_json=True, input=payload)
        context.provider_id = provider_info["id"]
        trivial(f"Provider created: {provider_info['id']} ({context.provider_type}/{payload['name']})")

    if context.mode_config.startswith("file:"):
        return
    if context.mode_config.startswith("id:"):
        return
    raise click.ClickException(f"Invalid config: {context.mode_config}.")


@step(31)
def create_pool1():
    pool_info = create_pool(random.randint(100, 199))
    context.pool_id_1 = pool_info["id"]

    trivial(f"Pool created: {pool_info['id']} ({pool_info['templateType']}/{pool_info['name']})")

    trivial("Waiting for pool to be ready...")

    try:
        run_cli(f"hcs template wait {context.pool_id_1} -t20m")
    except Exception as e:
        pool_info = run_cli(f"hcs template get {context.pool_id_1}", output_json=True)
        click.echo()
        click.echo("---- Start pool dump ----")
        if "customVariables" in pool_info:
            pool_info["customVariables"] = f"<redacted> ({len(pool_info['customVariables'])})"
        if "customTemplate" in pool_info:
            pool_info["customTemplate"] = f"<redacted> ({len(pool_info['customTemplate'])})"
        click.echo(json.dumps(pool_info, indent=4, default=vars))
        click.echo("---- End pool dump ----")
        fail(error_details(e))


@step(32, "[VM Basis] Verify the first VM")
def verify_vm():
    vm = run_cli(f"hcs vm list --first {context.pool_id_1}", output_json=True)

    trivial(f"The first VM is: {vm['id']}")
    context.t1_vm0 = context.pool_id_1 + "/" + vm["id"]

    lifecycle_status = vm["lifecycleStatus"]
    if lifecycle_status != "PROVISIONED":
        fail(f"The first VM is not provisioned. Lifecycle status: {lifecycle_status}. Error: {vm.get('error')}")
    trivial("The first VM lifecycle status is PROVISIONED.")

    power_state = vm.get("powerState")
    if power_state is None:
        # Rare case that the VM is not yet powered on
        time.sleep(5)
        vm = run_cli(f"hcs vm list --first {context.pool_id_1}", output_json=True)
        power_state = vm.get("powerState")
    if power_state != "PoweredOn":
        fail(f"The first VM is not powered on. Power state: {power_state}. Error: {vm.get('error')}")
    trivial("The first VM is powered on.")

    agent_status = vm["agentStatus"]
    if agent_status != "AVAILABLE":
        fail(f"The first VM agent is not available. Agent status: {agent_status}. Error: {vm.get('error')}")
    trivial("The first VM agent is AVAILABLE.")


@step(40)
def test_power_off():
    vm = run_cli(f"hcs vm poweroff -w5m {context.t1_vm0}", output_json=True)
    power_state = vm["powerState"]
    if power_state != "PoweredOff":
        fail(f"The first VM is not powered off. Power state: {power_state}")


@step(41)
def test_power_on():
    vm = run_cli(f"hcs vm poweron -w5m {context.t1_vm0}", output_json=True)
    power_state = vm["powerState"]
    if power_state != "PoweredOn":
        fail(f"The first VM is not powered on. Power state: {power_state}")


@step(42)
def test_shutdown():
    run_cli(f"hcs vm shutdown -w5m {context.t1_vm0}", output_json=True)


@step(43)
def test_restart():
    run_cli(f"hcs vm poweron -w5m {context.t1_vm0}", output_json=True)
    run_cli(f"hcs vm restart {context.t1_vm0}", output_json=True)

    time.sleep(15)

    # wait for the VM to be PoweredOn again
    run_cli(
        f"hcs vm wait --property powerState=PoweredOn --timeout 5m {context.t1_vm0}",
        output_json=True,
        inherit_output=False,
    )


@step(44)
def test_delete_vm():
    # shrink sparePolicy.min to 0, to prevent from auto recreation
    run_cli(f"hcs template update -u sparePolicy.min=0 -u sparePolicy.max=2 {context.pool_id_1}", output_json=True)
    run_cli(f"hcs vm delete -y -w5m {context.t1_vm0}", output_json=False, inherit_output=False)
    vm_ids = run_cli(f"hcs vm list {context.pool_id_1} --ids", output_json=True)

    if context.t1_vm0 in vm_ids:
        fail(f"The first VM is not deleted. VM ID: {context.t1_vm0}")


@step(50, "[Pool Operation] Expand the pool with 2 more VMs concurrently")
def test_parallel_expansion():
    run_cli(
        f"hcs template update -u sparePolicy.min=2 -u sparePolicy.max=2 {context.pool_id_1}",
        output_json=True,
    )
    trivial("Waiting for two more VMs to be created in parallel")

    start_time = time.time()
    while time.time() - start_time < 5 * 60:
        pool_info = run_cli(f"hcs template get --field reportedStatus {context.pool_id_1}", output_json=True)
        provisioned_vms = pool_info["reportedStatus"]["provisionedVMs"]
        if provisioned_vms >= 2:
            break
        time.sleep(30)


@step(51)
def test_delete_pool():
    run_cli(f"hcs template delete -y -w5m {context.pool_id_1}", inherit_output=False)


@step(60, "[Parallel Operation] Test parallel creation of multiple pools")
def create_two_pools():
    pool_info2 = create_pool(random.randint(200, 299), 2)
    context.pool_id_2 = pool_info2["id"]
    trivial(f"Pool2 created: {pool_info2['id']} ({pool_info2['templateType']}/{pool_info2['name']})")
    pool_info3 = create_pool(random.randint(300, 399), 2)
    context.pool_id_3 = pool_info3["id"]
    trivial(f"Template3 created: {pool_info3['id']} ({pool_info3['templateType']}/{pool_info3['name']})")

    run_cli(f"hcs template wait -t20m {context.pool_id_2}")
    run_cli(f"hcs template wait -t1m {context.pool_id_3}")


@step(61, "[Parallel Operation] Test parallel operations on multiple pools: power off all VMs")
def power_off_all_vms():
    t2_vms = run_cli(f"hcs vm list --ids {context.pool_id_2}", output_json=True)
    t3_vms = run_cli(f"hcs vm list --ids {context.pool_id_3}", output_json=True)
    payload = {"ids": t2_vms}
    run_cli(
        f"hcs api --post /admin/v2/templates/{context.pool_id_2}/vms?action=powerOff&org_id={context.org_id}",
        input=payload,
        output_json=True,
    )
    payload = {"ids": t3_vms}
    run_cli(
        f"hcs api --post /admin/v2/templates/{context.pool_id_3}/vms?action=powerOff&org_id={context.org_id}",
        input=payload,
        output_json=True,
    )

    full_vm_paths = [f"{context.pool_id_2}/{id}" for id in t2_vms] + [f"{context.pool_id_3}/{id}" for id in t3_vms]
    first = True
    for full_vm_path in full_vm_paths:
        if first:
            first = False
            time_to_wait = "5m"
        else:
            time_to_wait = "1m"
        run_cli(
            f"hcs vm wait --property powerState=PoweredOff --timeout {time_to_wait} {full_vm_path}", output_json=True
        )
    trivial("All VMs from all pools are powered off")


@step(70, "[Parallel Operation] Test deletion of multiple pools in parallel.")
def delete_two_pools():
    run_cli(f"hcs template delete -y {context.pool_id_2}", inherit_output=False)
    run_cli(f"hcs template delete -y {context.pool_id_3}", inherit_output=False)
    run_cli(f"hcs template delete -y {context.pool_id_2} -w10m", inherit_output=False)
    trivial("Pool 2 deleted")
    # Because they are deleted in parallel, now we should not wait for long.
    run_cli(f"hcs template delete -y {context.pool_id_3} -w1m", inherit_output=False)
    trivial("Pool 3 deleted")


@step(100)
def clean_up_test_resources():
    _cleanup_impl()


def run(
    mode_config: str,
    provider_id: str,
    specific_step: Union[str, int] = None,
    from_step: int = None,
    to_step: int = None,
):
    context.user_provider_id = provider_id
    context.mode_config = mode_config

    start_time = time.time()
    step.run(module=sys.modules[__name__], specific=specific_step, from_step=from_step, to_step=to_step)  # type: ignore[attr-defined]
    print()
    click.echo("✓ Complete. " + click.style(f"({display_time(time.time() - start_time)})", fg="bright_black"))


def clean():
    clean_up_test_resources()
