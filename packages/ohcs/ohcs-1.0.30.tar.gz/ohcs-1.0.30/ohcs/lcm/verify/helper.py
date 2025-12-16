# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import functools
import inspect
import json
import os
import random
import string
import sys
import time
import traceback

import click
from yumako import state_file
from yumako.time import display as display_time

from ohcs.common.utils import OhcsSdkException, error_details, run_cli, fail as fail, trivial as trivial

context = state_file(".ohcs_context.json")
_pool_example = None


def timer(func):
    """Decorator to measure and display function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = int(time.time() - start_time)
        click.secho(f"Time taken: {display_time(duration)}", fg="bright_black")
        return result

    return wrapper


def step(step_index, description=None):
    def decorator(func):
        # Store step metadata as attributes on the function
        func._step_index = step_index
        func._step_description = description
        func._is_step = True

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            try:
                click.echo(
                    "-------------------------------------------------------------------------------------------------------"
                )
                # Check if progress info is passed in kwargs
                progress = kwargs.pop("_progress", None)
                total_steps = kwargs.pop("_total_steps", None)

                if total_steps:
                    msg = f"[{progress}/{total_steps}] {func_name}"
                else:
                    msg = f"{func_name}"

                click.echo(msg)

                if description:
                    click.secho(description, fg="bright_black")

                start_time = time.time()
                result = func(*args, **kwargs)
                duration = display_time(time.time() - start_time)
                click.echo("✓ Success " + click.style(f"({duration})", fg="bright_black"))
                return result
            except Exception as e:
                if _need_stack_trace(e):
                    traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                duration = display_time(time.time() - start_time)
                click.echo(
                    "✗ FAILED " + click.style(f"({duration})", fg="bright_black") + f" {func_name}: {error_details(e)}"
                )
                sys.exit(1)

        return wrapper

    return decorator


def _need_stack_trace(e):
    if isinstance(e, click.ClickException) or isinstance(e, OhcsSdkException):
        return False
    return True


def _run_all_steps(module=None, specific=None, from_step=None, to_step=None):
    # Find all step functions in the module
    step_functions = []
    verify_index = {}

    target_specific_step = None

    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and hasattr(obj, "_is_step") and obj._is_step:
            step_functions.append(obj)
            index = getattr(obj, "_step_index", None)
            if index in verify_index:
                raise click.ClickException(
                    f"Two steps ({name} and {verify_index[index]}) have the same index {index}. Duplicated index is invalid."
                )
            verify_index[index] = name

            if specific is not None:
                if name == specific:
                    target_specific_step = obj
                elif str(index) == specific:
                    target_specific_step = obj

    if specific is not None:
        if target_specific_step is None:
            raise click.ClickException(f"Step {specific} not found.")
        return target_specific_step()

    # Sort by step index
    step_functions.sort(key=lambda f: f._step_index)

    total_steps = len(step_functions)
    for index, func in enumerate(step_functions):
        if from_step and index + 1 < from_step:
            continue

        if to_step and index + 1 > to_step:
            break

        func(_progress=index + 1, _total_steps=total_steps)


step.run = _run_all_steps  # type: ignore[attr-defined]


def _generate_random_password():
    ret = random.choice(string.ascii_letters).capitalize()
    ret += "".join(random.choices(string.ascii_letters + string.digits, k=12))
    return ret


def create_pool(test_id: int, capacity: int = 1):
    global _pool_example
    if not _pool_example:
        if context.mode_config == "builtin:akka":
            deployment_input = run_cli("hcs plan input", output_json=True)
            _pool_example = deployment_input["myPoolDedicated"]
        elif context.mode_config == "builtin:plugin-simulator":
            file_path = os.path.join(os.path.dirname(__file__), "plugin-simulator.json")
            _pool_example = load_pool_file(file_path)
        elif context.mode_config.startswith("file:"):
            file_path = context.mode_config.replace("file:", "", 1)
            _pool_example = load_pool_file(file_path)
        elif context.mode_config.startswith("id:"):
            pool_id = context.mode_config.replace("id:", "", 1)
            _pool_example = run_cli(f"hcs template get {pool_id}", output_json=True)
            if not _pool_example:
                raise click.ClickException(f"The specified example pool {pool_id} not found.")
            _pool_example["desktopAdminPassword"] = _generate_random_password()
            unnecessary_fields = [
                "id",
                "location",
                "reportedStatus",
                "syncStatus",
                "protocols",
                "networkType",
                "clientAccessLicenseApplicable",
                "providerLabel",
                "maxQuiescingVMs",
                "availabilityZoneEnabled",
                "osType",
                "reuseVmId",
                "hibernateSettings",
                "templateConnectivityStatus",
                "transientLoadThresholdSecs",
                "deleting",
                "resourceTagStatus",
                "unmanaged",
                "provisioningDisabled",
                "agentCustomization",
                "desktopAdminCredentialId",
                "hdc",
                "createdAt",
                "updatedAt",
            ]
            for field in unnecessary_fields:
                _pool_example.pop(field, None)
        else:
            raise click.ClickException(f"Invalid mode config: {context.mode_config}.")

    pool = _pool_example.copy()
    name = f"lcm_test_{test_id}"
    pool["id"] = name
    pool["name"] = name
    pool["orgId"] = context.org_id
    pool["vmNamePattern"] = f"t{test_id}vm"
    pool["sparePolicy"] = {"limit": 3, "max": capacity, "min": capacity}
    pool["powerPolicy"] = {"enabled": False}
    try:
        return run_cli("hcs template create", output_json=True, input=pool)
    except Exception as e:
        click.echo()
        click.echo("---- Start pool dump ----")
        click.echo(json.dumps(pool, indent=4, default=vars))
        click.echo("---- End pool dump ----")
        raise e


def load_pool_file(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise click.ClickException(f"Pool file {file_path} not found")
    with open(file_path, "r") as f:
        return json.load(f)


def get_akka_plan_file_path() -> str:
    abs_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(abs_dir, "akka.plan.yml")
