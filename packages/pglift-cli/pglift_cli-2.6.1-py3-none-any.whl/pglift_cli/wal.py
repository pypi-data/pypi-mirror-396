# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

import click

from pglift import instances, manager
from pglift.models import PostgreSQLInstance

from .util import (
    Group,
    Obj,
    async_command,
    audit,
    instance_identifier_option,
    pass_postgresql_instance,
)


@click.group(cls=Group)
@instance_identifier_option
def cli(**kwargs: Any) -> None:
    """Manage WAL replay of a PostgreSQL instance."""


@cli.command("pause-replay")
@pass_postgresql_instance
@click.pass_obj
@async_command
async def pause_wal_replay(obj: Obj, instance: PostgreSQLInstance) -> None:
    """Pause WAL replay on PostgreSQL standby INSTANCE"""
    with obj.lock, audit():
        with manager.from_instance(instance):
            await instances.pause_wal_replay(instance)


@cli.command("resume-replay")
@pass_postgresql_instance
@click.pass_obj
@async_command
async def resume_wal_replay(obj: Obj, instance: PostgreSQLInstance) -> None:
    """Resume WAL replay on PostgreSQL standby INSTANCE"""
    with obj.lock, audit():
        with manager.from_instance(instance):
            await instances.resume_wal_replay(instance)
