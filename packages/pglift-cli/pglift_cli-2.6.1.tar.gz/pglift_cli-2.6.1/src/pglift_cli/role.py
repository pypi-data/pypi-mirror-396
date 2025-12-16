# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import Any

import click

from pglift import diff, manager, postgresql, privileges, profiles, roles
from pglift.models import PostgreSQLInstance, interface
from pglift.types import Operation, validation_context
from pglift.util import deep_update

from . import _site, model
from .util import (
    Group,
    ManifestData,
    Obj,
    OutputFormat,
    async_command,
    audit,
    diff_options,
    dry_run_option,
    instance_identifier_option,
    manifest_option,
    model_dump,
    output_format_option,
    pass_postgresql_instance,
    print_argspec,
    print_json_for,
    print_result_diff,
    print_schema,
    print_table_for,
    system_configure,
)


def print_role_schema(
    context: click.Context, param: click.Parameter, value: bool
) -> None:
    return print_schema(context, param, value, model=_site.ROLE_MODEL)


def print_role_argspec(
    context: click.Context, param: click.Parameter, value: bool
) -> None:
    print_argspec(context, param, value, model=_site.ROLE_MODEL)


@click.group("role", cls=Group)
@instance_identifier_option
@click.option(
    "--schema",
    is_flag=True,
    callback=print_role_schema,
    expose_value=False,
    is_eager=True,
    help="Print the JSON schema of role model and exit.",
)
@click.option(
    "--ansible-argspec",
    is_flag=True,
    callback=print_role_argspec,
    expose_value=False,
    is_eager=True,
    hidden=True,
    help="Print the Ansible argspec of role model and exit.",
)
def cli(**kwargs: Any) -> None:
    """Manage roles."""


@cli.command("create")
@model.as_parameters(_site.ROLE_MODEL, "create")
@pass_postgresql_instance
@dry_run_option
@click.pass_obj
@async_command
async def create(
    obj: Obj, instance: PostgreSQLInstance, role: interface.Role, dry_run: bool
) -> None:
    """Create a role in a PostgreSQL instance"""
    with obj.lock, audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            if await roles.exists(instance, role.name):
                raise click.ClickException("role already exists")
            with manager.from_instance(instance):
                await roles.apply(instance, role)


@cli.command("alter")
@model.as_parameters(_site.ROLE_MODEL, "update")
@click.argument("rolname")
@pass_postgresql_instance
@dry_run_option
@click.pass_obj  # type: ignore[arg-type]
@async_command
async def alter(
    obj: Obj, instance: PostgreSQLInstance, rolname: str, dry_run: bool, **changes: Any
) -> None:
    """Alter a role in a PostgreSQL instance"""
    with obj.lock, audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            with manager.from_instance(instance):
                values = model_dump(await roles.get(instance, rolname))
            values = deep_update(values, changes)
            altered = _site.ROLE_MODEL.model_validate(values)
            with manager.from_instance(instance):
                await roles.apply(instance, altered)


@cli.command("apply", hidden=True)
@manifest_option
@output_format_option
@diff_options["unified"]
@diff_options["ansible"]
@dry_run_option
@pass_postgresql_instance
@click.pass_obj
@async_command
async def apply(
    obj: Obj,
    instance: PostgreSQLInstance,
    data: ManifestData,
    output_format: OutputFormat | None,
    dry_run: bool,
    diff_format: diff.Format | None,
) -> None:
    """Apply manifest as a role"""
    op: Operation = (
        "update"
        if (
            data.get("state") == "absent"
            or await roles.exists(instance, name=data["name"])
        )
        else "create"
    )
    with validation_context(operation=op, settings=_site.SETTINGS):
        role = _site.ROLE_MODEL.model_validate(data)
    with (
        obj.lock,
        audit(dry_run=dry_run),
        diff.enabled(diff_format),
        system_configure(dry_run=dry_run),
    ):
        async with postgresql.running(instance):
            with manager.from_instance(instance):
                ret = await roles.apply(instance, role)
    if output_format == "json":
        print_json_for(ret)
    else:
        print_result_diff(ret)


@cli.command("list")
@output_format_option
@pass_postgresql_instance
@async_command
async def ls(instance: PostgreSQLInstance, output_format: OutputFormat | None) -> None:
    """List roles in instance"""
    async with postgresql.running(instance):
        with manager.from_instance(instance):
            rls = await roles.ls(instance)
    if output_format == "json":
        print_json_for([model_dump(r) for r in rls])
    else:
        print_table_for(
            rls,
            partial(
                model_dump,
                context={"pretty": True},
                exclude={"hba_records", "validity"},
            ),
        )


@cli.command("get")
@output_format_option
@click.argument("name")
@pass_postgresql_instance
@async_command
async def get(
    instance: PostgreSQLInstance, name: str, output_format: OutputFormat | None
) -> None:
    """Get the description of a role"""
    async with postgresql.running(instance):
        with manager.from_instance(instance):
            r = await roles.get(instance, name)
    if output_format == "json":
        print_json_for(model_dump(r))
    else:
        print_table_for(
            [r],
            partial(
                model_dump,
                context={"pretty": True},
                exclude={"hba_records", "validity"},
            ),
            box=None,
        )


@cli.command("drop")
@model.as_parameters(interface.RoleDropped, "create")
@pass_postgresql_instance
@dry_run_option
@async_command
async def drop(
    instance: PostgreSQLInstance, roledropped: interface.RoleDropped, dry_run: bool
) -> None:
    """Drop a role"""
    with audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            with manager.from_instance(instance):
                await roles.drop(instance, roledropped)


@cli.command("privileges")
@click.argument("name")
@click.option(
    "-d", "--database", "databases", multiple=True, help="Database to inspect"
)
@click.option("--default", "defaults", is_flag=True, help="Display default privileges")
@output_format_option
@pass_postgresql_instance
@async_command
async def list_privileges(
    instance: PostgreSQLInstance,
    name: str,
    databases: Sequence[str],
    defaults: bool,
    output_format: OutputFormat | None,
) -> None:
    """List privileges of a role."""
    async with postgresql.running(instance):
        with manager.from_instance(instance):
            await roles.get(instance, name)  # check existence
        try:
            prvlgs = await privileges.get(
                instance, databases=databases, roles=(name,), defaults=defaults
            )
        except ValueError as e:
            raise click.ClickException(str(e)) from None
    if output_format == "json":
        print_json_for([model_dump(p) for p in prvlgs])
    else:
        print_table_for(prvlgs, model_dump)


@cli.command("set-profile")
@click.argument("role")
@model.as_parameters(interface.RoleProfile, "create")
@pass_postgresql_instance
@async_command
async def set_profile(
    instance: PostgreSQLInstance,
    role: str,
    roleprofile: interface.RoleProfile,
) -> None:
    """Set profile (read-only, read-write) for a specific role within a database and schema"""
    async with postgresql.running(instance):
        with manager.from_instance(instance):
            await roles.get(instance, role)  # check existence
        await profiles.set_for_role(instance, role, profile=roleprofile)
