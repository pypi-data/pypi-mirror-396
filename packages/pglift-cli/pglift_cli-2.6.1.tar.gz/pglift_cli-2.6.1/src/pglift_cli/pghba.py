# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

import click
from pgtoolkit.hba import parse as parse_hba

from pglift import diff, hba, manager
from pglift.models import PostgreSQLInstance, interface

from . import model
from .console import console
from .util import (
    Group,
    Obj,
    async_command,
    audit,
    diff_options,
    dry_run_option,
    instance_identifier_option,
    pass_postgresql_instance,
    system_configure,
)


@click.group(cls=Group)
@instance_identifier_option
def cli(**kwargs: Any) -> None:
    """Manage entries in HBA configuration of a PostgreSQL instance."""


@cli.command("add")
@model.as_parameters(interface.HbaRecord, "create")
@pass_postgresql_instance
@dry_run_option
@diff_options["unified"]
@diff_options["ansible"]
@click.pass_obj
@async_command
async def add(
    obj: Obj,
    instance: PostgreSQLInstance,
    hbarecord: interface.HbaRecord,
    diff_format: diff.Format | None,
    dry_run: bool,
) -> None:
    """Add a record in HBA configuration.

    If no --connection-* option is specified, a 'local' record is added.
    """
    with (
        obj.lock,
        audit(dry_run=dry_run),
        diff.enabled(diff_format),
        system_configure(dry_run=dry_run),
        manager.from_instance(instance),
    ):
        await hba.add(instance, hbarecord)
        if (diffvalue := diff.get()) is not None:
            for diffitem in diffvalue:
                console.print(diffitem)


@cli.command("remove")
@model.as_parameters(interface.HbaRecord, "create")
@pass_postgresql_instance
@dry_run_option
@diff_options["unified"]
@diff_options["ansible"]
@click.pass_obj
@async_command
async def remove(
    obj: Obj,
    instance: PostgreSQLInstance,
    hbarecord: interface.HbaRecord,
    diff_format: diff.Format | None,
    dry_run: bool,
) -> None:
    """Remove a record from HBA configuration.

    If no --connection-* option is specified, a 'local' record is removed.
    """
    with (
        obj.lock,
        audit(dry_run=dry_run),
        diff.enabled(diff_format),
        system_configure(dry_run=dry_run),
        manager.from_instance(instance),
    ):
        await hba.remove(instance, hbarecord)
        if (diffvalue := diff.get()) is not None:
            for diffitem in diffvalue:
                console.print(diffitem)


@cli.command("edit")
@pass_postgresql_instance
@click.pass_obj
@async_command
async def edit(obj: Obj, instance: PostgreSQLInstance) -> None:
    """Edit managed HBA records."""
    with obj.lock, audit():
        with manager.from_instance(instance):
            hba_ = await hba.get(instance)
            actual_hba = "\n".join([str(r) for r in hba_.lines])
        edited = click.edit(text=actual_hba)
        if edited is None:
            click.echo("no change", err=True)
            return
        entries = parse_hba(edited.splitlines())
        with manager.from_instance(instance):
            await hba.save(instance, entries, reload_on_change=True)
