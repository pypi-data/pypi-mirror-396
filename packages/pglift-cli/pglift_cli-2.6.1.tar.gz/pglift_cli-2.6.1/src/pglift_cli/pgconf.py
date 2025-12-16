# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import click
import pgtoolkit.conf as pgconf

from pglift import instances, manager, postgresql
from pglift.models import Instance, PostgreSQLInstance
from pglift.types import ConfigChanges, Status

from .util import (
    Group,
    Obj,
    async_command,
    audit,
    dry_run_option,
    instance_identifier_option,
    pass_instance,
    pass_postgresql_instance,
    system_configure,
)


@click.group(cls=Group)
@instance_identifier_option
def cli(**kwargs: Any) -> None:
    """Manage configuration of a PostgreSQL instance."""


def show_configuration_changes(
    changes: ConfigChanges, parameters: Iterable[str] | None = None
) -> None:
    for param, (old, new) in sorted(changes.items()):
        click.secho(f"{param}: {old} -> {new}", err=True, fg="green")
    if parameters is None:
        return
    if unchanged := set(parameters) - set(changes):
        click.secho(
            f"changes in {', '.join(map(repr, sorted(unchanged)))} not applied",
            err=True,
            fg="red",
        )
        click.secho(
            " hint: either these changes have no effect (values already set) "
            "or specified parameters are already defined in an un-managed file "
            "(e.g. 'postgresql.conf')",
            err=True,
            fg="blue",
        )


@cli.command("show")
@click.argument("parameter", nargs=-1)
@pass_postgresql_instance
def show(instance: PostgreSQLInstance, parameter: tuple[str]) -> None:
    """Show configuration (all parameters or specified ones).

    Only uncommented parameters are shown when no PARAMETER is specified. When
    specific PARAMETERs are queried, commented values are also shown.
    """
    config = instance.configuration()
    for entry in config.entries.values():
        if parameter:
            if entry.name in parameter:
                if entry.commented:
                    click.echo(f"# {entry.name} = {entry.serialize()}")
                else:
                    click.echo(f"{entry.name} = {entry.serialize()}")
        elif not entry.commented:
            click.echo(f"{entry.name} = {entry.serialize()}")


def validate_configuration_parameters(
    _context: click.Context, _param: click.Parameter, value: tuple[str]
) -> dict[str, str]:
    items = {}
    for v in value:
        try:
            key, val = v.split("=", 1)
        except ValueError:
            raise click.BadParameter(v) from None
        items[key] = val
    return items


@cli.command("set")
@click.argument(
    "parameters",
    metavar="<PARAMETER>=<VALUE>...",
    nargs=-1,
    callback=validate_configuration_parameters,
    required=True,
)
@pass_instance
@dry_run_option
@click.pass_obj
@async_command
async def set_(
    obj: Obj, instance: Instance, parameters: dict[str, Any], dry_run: bool
) -> None:
    """Set configuration items."""
    pg_instance = instance.postgresql
    with obj.lock, audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        status = await postgresql.status(pg_instance)
        manifest = await instances._get(instance, status, port_from_config=True)
        manifest.settings.update(parameters)
        with manager.from_instance(pg_instance):
            r = await instances.configure(
                pg_instance, manifest, _is_running=status == Status.running
            )
        show_configuration_changes(r.changes, parameters.keys())


@cli.command("remove")
@click.argument("parameters", nargs=-1, required=True)
@pass_instance
@dry_run_option
@click.pass_obj
@async_command
async def remove(
    obj: Obj, instance: Instance, parameters: tuple[str], dry_run: bool
) -> None:
    """Remove configuration items."""
    pg_instance = instance.postgresql
    with obj.lock, audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        status = await postgresql.status(pg_instance)
        manifest = await instances._get(instance, status, port_from_config=True)
        for p in parameters:
            try:
                del manifest.settings[p]
            except KeyError:
                raise click.ClickException(
                    f"{p!r} not found in managed configuration"
                ) from None
        with manager.from_instance(pg_instance):
            r = await instances.configure(
                pg_instance, manifest, _is_running=status == Status.running
            )
        show_configuration_changes(r.changes, parameters)


@cli.command("edit")
@pass_instance
@click.pass_obj
@async_command
async def edit(obj: Obj, instance: Instance) -> None:
    """Edit managed configuration."""
    pg_instance = instance.postgresql
    with obj.lock, audit():
        with manager.from_instance(pg_instance):
            actual_config = "".join(
                (await instances.postgresql_editable_conf(pg_instance)).lines
            )
        edited = click.edit(text=actual_config)
        if edited is None:
            click.echo("no change", err=True)
            return
        config = pgconf.parse_string(edited)
        values = config.as_dict()
        status = await postgresql.status(pg_instance)
        manifest = await instances._get(instance, status, port_from_config=True)
        manifest.settings.clear()
        manifest.settings.update(values)
        with manager.from_instance(pg_instance):
            r = await instances.configure(
                pg_instance, manifest, _is_running=status == Status.running
            )
        show_configuration_changes(r.changes)
