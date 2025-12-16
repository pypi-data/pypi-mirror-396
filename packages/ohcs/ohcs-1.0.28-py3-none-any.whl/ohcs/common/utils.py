# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import json
import os
import sys
from typing import Callable, Union

import click
from hcs_cli.support.exec_util import run_cli as run_cli
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


def fail(message):
    click.echo("✗ " + message)
    sys.exit(1)


def good(message):
    click.echo("✓ " + message)


def trivial(message):
    click.echo(click.style(message, fg="bright_black"))
