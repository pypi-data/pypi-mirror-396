# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import subprocess
from datetime import datetime
from typing import Any

import click

from pglift import pgbackrest, postgresql, types
from pglift.models import Instance
from pglift.pgbackrest import models
from pglift.pgbackrest import register_if as register_if

from .. import _site, hookimpl
from ..util import (
    Command,
    Obj,
    OutputFormat,
    async_command,
    audit,
    instance_identifier,
    instance_identifier_option,
    model_dump,
    output_format_option,
    print_json_for,
    print_table_for,
)


@click.command(
    "pgbackrest",
    hidden=True,
    cls=Command,
    context_settings={"ignore_unknown_options": True},
)
@instance_identifier_option
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def pgbackrest_proxy(
    context: click.Context, /, command: tuple[str, ...], **kwargs: Any
) -> None:
    """Proxy to pgbackrest operations on an instance"""
    s = context.obj.instance.service(models.Service)
    settings = pgbackrest.get_settings(_site.SETTINGS)
    cmd_args = pgbackrest.make_cmd(s.stanza, settings, *command)
    try:
        subprocess.run(cmd_args, capture_output=False, check=True)  # nosec
    except subprocess.CalledProcessError as e:
        raise click.ClickException(str(e)) from e


@click.command("restore", cls=Command)
@instance_identifier(nargs=1)
@click.option("--label", help="Label of backup to restore")
@click.option("--date", type=click.DateTime(), help="Date of backup to restore")
@click.pass_obj
@async_command
async def instance_restore(
    obj: Obj, instance: Instance, label: str | None, date: datetime | None
) -> None:
    """Restore PostgreSQL INSTANCE"""
    await postgresql.check_status(instance.postgresql, types.Status.not_running)
    if label is not None and date is not None:
        raise click.BadArgumentUsage(
            "--label and --date arguments are mutually exclusive"
        ) from None
    settings = pgbackrest.get_settings(_site.SETTINGS)
    with obj.lock, audit():
        await pgbackrest.restore(instance, settings, label=label, date=date)


@click.command("backups", cls=Command)
@output_format_option
@instance_identifier(nargs=1)
@async_command
async def instance_backups(
    instance: Instance, output_format: OutputFormat | None
) -> None:
    """List available backups for INSTANCE"""
    settings = pgbackrest.get_settings(_site.SETTINGS)
    backups = [b async for b in pgbackrest.iter_backups(instance, settings)]
    if output_format == "json":
        print_json_for([model_dump(b) for b in backups])
    else:
        print_table_for(
            backups, model_dump, title=f"Available backups for instance {instance}"
        )


@hookimpl
def command() -> click.Command:
    return pgbackrest_proxy


@hookimpl
def add_instance_commands(group: click.Group) -> None:
    group.add_command(instance_backups)
    group.add_command(instance_restore)
