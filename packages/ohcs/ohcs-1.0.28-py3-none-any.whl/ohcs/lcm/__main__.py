#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import logging
import os
import sys
import traceback

import click

from ohcs import __version__
from ohcs.common.utils import OhcsSdkException, error_details, good
from ohcs.common.logging_config import setup_logging

log = logging.getLogger(__name__)

setup_logging()


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """OHCS (Omnissa Horizon Cloud Service) lifecycle management extension"""
    pass


@cli.command()
def version():
    """Show version information"""
    click.echo(f"Omnissa Horizon Cloud Service LCM SDK, v{__version__}")


@cli.command()
@click.option("--org", "-o", type=str, required=False, help="The organization ID.")
@click.option(
    "--provider",
    "-p",
    type=str,
    required=False,
    help="The provider instance to pair with. If not specified, local configuration will be reused if exists, otherwise a new one will be created.",
)
@click.option("--no-stub", is_flag=True, default=False, help="Do not create stub plugin implementation and tutorial.")
@click.option(
    "--config",
    "customization_file",
    required=False,
    help="Optional. Specify properties file path to override default settings.",
)
def pair(org: str, provider: str = None, no_stub: bool = False, customization_file: str = None):
    """Pair with Horizon Cloud Service. If the local config.yml file exists, it will reuse provider and edge from the previous configuration, if exists. Otherwise, new provider and edge record will be created."""

    if not org:
        from hcs_core.ctxp import profile

        current_profile = profile.current(exit_on_failure=False)
        if not current_profile:
            if not org:
                click.echo("Org ID not found in profile. Specify --org <org-id>.")
                return 1
            click.echo("Initializing HCS default profile for first time usage...")

            from ohcs.common.utils import run_cli

            run_cli("hcs profile init", inherit_output=False)

        org = profile.current().csp.orgId
        if not org:
            click.echo("Org ID not found in profile. Specify --org <org-id>.")
            return 1

    if customization_file:
        if not os.path.exists(customization_file):
            click.echo(f"Config file not found: {customization_file}")
            return 1

    from . import pair

    if provider:
        config = pair.pair_existing(org, customization_file, provider)
    else:
        config = pair.pair_existing_or_new(org, customization_file)

    if no_stub:
        pass
    else:
        pair.create_stub_plugin_and_tutorial(config)


@cli.command()
@click.option("--org", "-o", type=str, required=False, help="The organization ID.")
@click.option("--all", is_flag=True, default=False, help="Delete all custom provider instances from the cloud.")
@click.option("--confirm", "-y", is_flag=True, default=False, help="Confirm the operation without prompt.")
def reset(org: str, all: bool, confirm: bool):
    """Reset the pairing, delete records from cloud and local pairing configuration."""

    from . import pair

    if all:
        pair.reset_all(org, confirm)
    else:
        pair.reset(org, confirm)
    good("Reset completed.")


@cli.command()
@click.option(
    "--config",
    "-c",
    "config_file",
    type=str,
    required=False,
    default=None,
    help="Specify the path of config file to use",
)
def serve(config_file: str):
    """Serve the local lifecycle management extension"""

    from ohcs.lcm.serve import serve

    serve(config_file)


@cli.command()
@click.option(
    "--pool-file",
    "-f",
    type=str,
    required=False,
    help="Specify the pool file for testing. New pools will be created using the given pool file.",
)
@click.option(
    "--pool-id",
    "-i",
    type=str,
    required=False,
    help="Specify the ID of an existing pool, to copy settings for test poolss. The specified pool will not be changed.",
)
@click.option(
    "--akka",
    is_flag=True,
    required=False,
    help="Use the AKKA pool for testing.",
)
@click.option(
    "--plugin-simulator",
    is_flag=True,
    required=False,
    help="Use the plugin simulator pool for testing.",
)
@click.option(
    "--provider", "-p", type=str, required=False, help="Override the provider instance ID to use for the test."
)
@click.option(
    "--step",
    "-s",
    type=str,
    required=False,
    help="Run a single specific step, either by name or index",
)
@click.option(
    "--from",
    "from_step",
    type=int,
    required=False,
    help="Run from a specific step index",
)
@click.option("--to", "to_step", type=int, required=False, help="Run to a specific step index")
@click.option(
    "--clean", "-c", is_flag=True, required=False, help="Clean up the test environment. Do not run test steps."
)
def verify(
    pool_file: str,
    pool_id: str,
    akka: bool,
    plugin_simulator: bool,
    provider: str,
    step: str,
    from_step: int,
    to_step: int,
    clean: bool,
):
    """Run lifecycle management (LCM) verification test. This will invoke cloud API to create/delete pools and VMs to verify the provider and LCM plugin."""

    from . import verify

    if clean:
        if pool_file or pool_id or akka or plugin_simulator or provider or step or from_step or to_step:
            raise click.ClickException("Cannot specify --clean and other options at the same time")
        return verify.clean()

    if akka and pool_file:
        raise click.ClickException("Cannot specify both --akka and --pool-file")
    if akka and pool_id:
        raise click.ClickException("Cannot specify both --akka and --pool-id")
    if akka and plugin_simulator:
        raise click.ClickException("Cannot specify both --akka and --plugin-simulator")
    if akka and provider:
        raise click.ClickException(
            "Cannot specify both --akka and --provider. For akka mode, the provider will be automatically created."
        )
    if plugin_simulator and pool_file:
        raise click.ClickException("Cannot specify both --plugin-simulator and --pool-file")
    if plugin_simulator and pool_id:
        raise click.ClickException("Cannot specify both --plugin-simulator and --pool-id")
    if pool_file and pool_id:
        raise click.ClickException("Cannot specify both --pool-file and --pool-id")
    if step and from_step:
        raise click.ClickException("Cannot specify both step and from_step")
    if step and to_step:
        raise click.ClickException("Cannot specify both step and to_step")

    if akka:
        mode_config = "builtin:akka"
    elif plugin_simulator:
        mode_config = "builtin:plugin-simulator"
    elif pool_file:
        mode_config = "file:" + pool_file
    elif pool_id:
        mode_config = "id:" + pool_id
    else:
        raise click.ClickException(
            "Pool file or pool ID is required. Specify --pool <file-path> or --pool-id <pool-id>."
        )

    return verify.run(mode_config, provider, specific_step=step, from_step=from_step, to_step=to_step)


@cli.command()
def info():
    """Show information about the running lifecycle management process"""
    import json
    from ohcs.common import stats
    from ohcs import __version__

    # Read stats from shared memory
    global_stats = stats.read_shared()

    # Build info response
    info_data = {"version": __version__, "stats": global_stats}

    click.echo(json.dumps(info_data, indent=4))


def _need_error_traceback(e):
    for type in []:
        if isinstance(e, type):
            return False
    return True


if __name__ == "__main__":
    try:
        cli()
    except OhcsSdkException as e:
        log.error(f"OHCS Error: {error_details(e)}")
        sys.exit(1)
    except Exception as e:
        if _need_error_traceback(e):
            traceback.print_exc()
        log.exception(f"Unexpected error: {error_details(e)}")
        sys.exit(1)
