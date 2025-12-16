# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import click

from pglift import pgbackrest, types
from pglift.models import Instance
from pglift.pgbackrest import repo_path
from pglift.pgbackrest.repo_path import register_if as register_if

from .. import _site, hookimpl
from ..util import Command, Obj, async_command, audit, instance_identifier


@click.command("backup", cls=Command)
@instance_identifier(nargs=1)
@click.option(
    "--type",
    "backup_type",
    type=click.Choice(types.BACKUP_TYPES),
    default=types.DEFAULT_BACKUP_TYPE,
    help="Backup type",
)
@click.pass_obj
@async_command
async def instance_backup(
    obj: Obj, instance: Instance, backup_type: types.BackupType
) -> None:
    """Back up PostgreSQL INSTANCE"""
    settings = pgbackrest.get_settings(_site.SETTINGS)
    with obj.lock, audit():
        await repo_path.backup(instance, settings, type=backup_type)


@hookimpl
def add_instance_commands(group: click.Group) -> None:
    group.add_command(instance_backup)
