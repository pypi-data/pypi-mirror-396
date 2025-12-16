# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import click

from pglift import postgresql
from pglift.exceptions import InstanceNotFound
from pglift.models import PostgreSQLInstance
from pglift.system import cmd

from . import _site


def instance_from_qualname(
    context: click.Context, _param: click.Parameter, value: str
) -> PostgreSQLInstance:
    try:
        return PostgreSQLInstance.from_qualname(value, _site.SETTINGS)
    except (ValueError, InstanceNotFound) as e:
        raise click.BadParameter(str(e), context) from None


@click.command("postgres", hidden=True)
@click.argument("instance", callback=instance_from_qualname)
def cli(instance: PostgreSQLInstance) -> None:
    """Start postgres for specified INSTANCE, identified as <version>-<name>."""
    args = [str(postgresql.bindir(instance) / "postgres"), "-D", str(instance.datadir)]
    cmd.execute_program(args)
