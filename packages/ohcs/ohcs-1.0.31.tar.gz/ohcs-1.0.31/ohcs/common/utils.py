# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import json
import os
import sys
from typing import Any, Callable, Union

import click
from hcs_cli.support.exec_util import run_cli as run_cli_original
from hcs_core.ctxp.util import error_details as error_details


class OhcsSdkException(Exception):
    pass


class PluginException(Exception):
    pass


def with_local_file(file_path: str, data: Union[str, dict], fn: Callable, delete_on_error: bool = False):
    if isinstance(data, dict):
        data = json.dumps(data)

    delete_file = True
    try:
        with open(file_path, "w") as f:
            f.write(data)

        return fn(file_path)
    except Exception as e:
        if not delete_on_error:
            delete_file = False
        print("----- FILE DUMP START -----")
        print(data)
        print("----- FILE DUMP END -----")
        raise e
    finally:
        if delete_file and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


def fail(message, code=1):
    click.echo("✗ " + message)
    sys.exit(code)


def good(message):
    click.echo("✓ " + message)


def trivial(message):
    click.echo(click.style(message, fg="bright_black"))


def warning(message):
    click.echo(click.style(message, fg="yellow"))


def run_cli(
    cmd: str,
    output_json=False,
    raise_on_error=True,
    inherit_output: Union[bool, None] = None,
    input: Union[str, dict[Any, Any], list[Any]] = None,
    show_command: bool = True,
    log_error: bool = True,
    env: dict = None,
):
    if isinstance(cmd, str) and cmd.startswith("hcs "):
        if _use_hcs_module_as_executable():
            cmd = cmd[4:]
            cmd = "python -m hcs_cli " + cmd

    result = run_cli_original(
        cmd,
        output_json=output_json,
        raise_on_error=raise_on_error,
        inherit_output=inherit_output,
        input=input,
        show_command=show_command,
        log_error=log_error,
        env=env,
    )
    return result


_use_hcs_module_for_cli = None


def _use_hcs_module_as_executable():
    """Test if the 'hcs' CLI executable is available in the system PATH."""

    global _use_hcs_module_for_cli

    if _use_hcs_module_for_cli is None:
        if os.name == "nt":
            import shutil

            # Check if 'hcs' or 'hcs.exe' is in PATH
            hcs_path = shutil.which("hcs")

            if hcs_path:
                _use_hcs_module_for_cli = False
            else:
                click.echo(
                    "'hcs' executable not found in PATH, this is a known difficulty with Windows Python module installation. Falling back to 'python -m hcs_cli' for all 'hcs' commands."
                )
                _use_hcs_module_for_cli = True
        else:
            _use_hcs_module_for_cli = False

    return _use_hcs_module_for_cli
