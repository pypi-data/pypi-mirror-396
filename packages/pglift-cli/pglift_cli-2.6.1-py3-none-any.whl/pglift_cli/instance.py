# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
from collections.abc import Sequence
from functools import partial
from typing import Any

import click

from pglift import (
    async_hooks,
    diff,
    exceptions,
    hooks,
    hookspecs,
    instances,
    manager,
    postgresql,
    privileges,
    task,
)
from pglift.models import Instance, PostgreSQLInstance, interface
from pglift.settings import (
    POSTGRESQL_VERSIONS,
    PostgreSQLVersion,
    default_postgresql_version,
)
from pglift.types import Operation, Status, validation_context
from pglift.util import deep_update

from . import _site, model
from . import hookspecs as h
from .util import (
    ManifestData,
    Obj,
    OutputFormat,
    PluggableCommandGroup,
    async_command,
    audit,
    diff_options,
    dry_run_option,
    foreground_option,
    instance_identifier,
    manifest_option,
    model_dump,
    output_format_option,
    postgresql_instance_identifier,
    print_argspec,
    print_json_for,
    print_result_diff,
    print_schema,
    print_table_for,
)


class InstanceCommands(PluggableCommandGroup):
    """Group for 'instance' sub-commands, part of which come from registered
    plugins.
    """

    def register_plugin_commands(self, *args: Any) -> None:
        hooks(_site.PLUGIN_MANAGER, h.add_instance_commands, group=self)


def print_instance_schema(
    context: click.Context, param: click.Parameter, value: bool
) -> None:
    return print_schema(context, param, value, model=_site.INSTANCE_MODEL)


def print_instance_argspec(
    context: click.Context, param: click.Parameter, value: bool
) -> None:
    print_argspec(context, param, value, model=_site.INSTANCE_MODEL)


@click.group(cls=InstanceCommands)
@click.option(
    "--schema",
    is_flag=True,
    callback=print_instance_schema,
    expose_value=False,
    is_eager=True,
    help="Print the JSON schema of instance model and exit.",
)
@click.option(
    "--ansible-argspec",
    is_flag=True,
    callback=print_instance_argspec,
    expose_value=False,
    is_eager=True,
    hidden=True,
    help="Print the Ansible argspec of instance model and exit.",
)
def cli() -> None:
    """Manage instances."""


@cli.command("create")
@model.as_parameters(_site.INSTANCE_MODEL, "create")
@click.option(
    "--drop-on-error/--no-drop-on-error",
    default=True,
    help=(
        "On error, drop partially initialized instance by possibly "
        "rolling back operations (true by default)."
    ),
)
@click.pass_obj
@async_command
async def create(obj: Obj, instance: interface.Instance, drop_on_error: bool) -> None:
    """Initialize a PostgreSQL instance"""
    with obj.lock, audit():
        if instances.exists(instance.name, instance.version, _site.SETTINGS):
            raise click.ClickException("instance already exists")
        with manager.from_manifest(instance, settings=_site.SETTINGS):
            async with task.async_transaction(drop_on_error):
                await instances.apply(_site.SETTINGS, instance)


@cli.command("alter")
@instance_identifier(nargs=1)
@model.as_parameters(_site.INSTANCE_MODEL, "update")
@diff_options["unified"]
@diff_options["ansible"]
@output_format_option
@click.pass_obj  # type: ignore[arg-type]
@async_command
async def alter(
    obj: Obj,
    instance: Instance,
    output_format: OutputFormat | None,
    diff_format: diff.Format | None,
    **changes: Any,
) -> None:
    """Alter PostgreSQL INSTANCE"""
    with obj.lock, audit():
        status = await postgresql.status(instance.postgresql)
        manifest = await instances._get(instance, status)
        values = manifest.model_dump(by_alias=True, exclude={"settings"})
        values = deep_update(values, changes)
        # No need for 'settings' in validation_context() as a 'version' key
        # must be present in 'values' when altering.
        with validation_context(operation="update", instance=manifest):
            altered = _site.INSTANCE_MODEL.model_validate(values)
        with (
            diff.enabled(diff_format),
            manager.from_manifest(altered, settings=_site.SETTINGS),
        ):
            ret = await instances.apply(
                _site.SETTINGS, altered, _is_running=status == Status.running
            )
        if output_format == "json":
            print_json_for(ret)
        else:
            print_result_diff(ret)


@cli.command("apply", hidden=True)
@manifest_option
@output_format_option
@diff_options["unified"]
@diff_options["ansible"]
@dry_run_option
@click.pass_obj
@async_command
async def apply(
    obj: Obj,
    data: ManifestData,
    output_format: OutputFormat | None,
    dry_run: bool,
    diff_format: diff.Format | None,
) -> None:
    """Apply manifest as a PostgreSQL instance"""
    name, version = data["name"], data.get("version")
    if version is None:
        version = default_postgresql_version(_site.SETTINGS.postgresql)
    elif not isinstance(version, str):
        version = str(version)
    try:
        actual = await instances.get((name, version), settings=_site.SETTINGS)
    except exceptions.InstanceNotFound:
        actual = None
    op: Operation = "create"
    if data.get("state") == "absent" or actual is not None:
        op = "update"
    with validation_context(operation=op, settings=_site.SETTINGS, instance=actual):
        instance = _site.INSTANCE_MODEL.model_validate(data)
    if dry_run:
        ret = interface.InstanceApplyResult(change_state=None)
    else:
        with (
            obj.lock,
            audit(dry_run=dry_run),
            diff.enabled(diff_format),
            manager.from_manifest(actual or instance, settings=_site.SETTINGS),
        ):
            ret = await instances.apply(_site.SETTINGS, instance)
    if output_format == "json":
        print_json_for(ret)
    else:
        print_result_diff(ret)


@cli.command("promote")
@instance_identifier(nargs=1)
@click.pass_obj
@async_command
async def promote(obj: Obj, instance: Instance) -> None:
    """Promote standby PostgreSQL INSTANCE"""
    with obj.lock, audit(), manager.from_instance(instance.postgresql):
        await instances.promote(instance)


@cli.command("demote")
@instance_identifier(nargs=1)
@model.as_parameters(postgresql.RewindSource, "create")
@click.option(
    "--start/--no-start",
    help="Start the instance at the end of the demotion process",
    default=True,
    show_default=True,
)
@click.argument("rewind_opts", nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
@async_command
async def demote(
    obj: Obj,
    instance: Instance,
    rewindsource: postgresql.RewindSource,
    start: bool,
    rewind_opts: tuple[str, ...],
) -> None:
    """Demote PostgreSQL INSTANCE as standby of specified source server using pg_rewind.

    The instance must not be running and it may be started at the end of the
    "demotion" process.

    Extra options can be passed to the pg_rewind command. They may need to
    be prefixed with -- to separate them from the current command options
    when confusion arises. When using extra options, providing the instance
    identifier is required.
    """
    with obj.lock, audit(), manager.from_instance(instance.postgresql):
        await instances.demote(instance, rewindsource, rewind_opts=rewind_opts)
        if start:
            await instances.start(instance)


@cli.command("get")
@output_format_option
@instance_identifier(nargs=1)
@async_command
async def get(instance: Instance, output_format: OutputFormat | None) -> None:
    """Get the description of PostgreSQL INSTANCE.

    Unless --output-format is specified, 'settings' and 'state' fields are not
    shown as well as 'standby' information if INSTANCE is not a standby.
    """
    i = await instances.get(instance)
    if output_format == "json":
        print_json_for(model_dump(i))
    else:
        exclude = {
            "settings",
            "state",
            "data_directory",
            "wal_directory",
            "powa",
        }
        if not instance.postgresql.standby:
            exclude.add("standby")
        print_table_for(
            [i],
            partial(model_dump, exclude=exclude, context={"pretty": True}),
            box=None,
        )


@cli.command("list")
@click.option(
    "--version",
    type=click.Choice(POSTGRESQL_VERSIONS),
    help="Only list instances of specified version.",
)
@output_format_option
@async_command
async def ls(
    version: PostgreSQLVersion | None, output_format: OutputFormat | None
) -> None:
    """List the available instances"""
    items = [i async for i in instances.ls(_site.SETTINGS, version=version)]
    if output_format == "json":
        print_json_for([model_dump(m) for m in items])
    else:
        print_table_for(items, model_dump)


@cli.command("drop")
@instance_identifier(nargs=-1)
@click.pass_obj
@async_command
async def drop(obj: Obj, instance: tuple[Instance, ...]) -> None:
    """Drop PostgreSQL INSTANCE"""
    with obj.lock, audit():
        for i in instance:
            with manager.from_instance(i.postgresql):
                await instances.drop(i)


@cli.command("status")
@instance_identifier(nargs=1)
@click.pass_context
@async_command
async def status(context: click.Context, instance: Instance) -> None:
    """Check the status of instance and all satellite components.

    Output the status string value ('running', 'not running') for each component.
    If not all services are running, the command exit code will be 3.
    """
    exit_code = Status.running.value
    results = list(
        filter(
            None,
            await async_hooks(
                instance._settings, hookspecs.instance_status, instance=instance
            ),
        )
    )
    for status, component in reversed(results):
        if status != Status.running:
            exit_code = Status.not_running.value
        click.echo(f"{component}: {status.name.replace('_', ' ')}")
    context.exit(exit_code)


@cli.command("start")
@instance_identifier(nargs=-1)
@foreground_option
@click.option("--all", "_all_instances", is_flag=True, help="Start all instances.")
@click.pass_obj
@async_command
async def start(
    obj: Obj,
    instance: tuple[Instance, ...],
    foreground: bool,
    _all_instances: bool,
) -> None:
    """Start PostgreSQL INSTANCE"""
    if foreground and len(instance) != 1:
        raise click.UsageError(
            "only one INSTANCE argument may be given with --foreground"
        )
    with obj.lock, audit():
        for i in instance:
            with manager.from_instance(i.postgresql):
                await instances.start(i, foreground=foreground)


@cli.command("stop")
@instance_identifier(nargs=-1)
@click.option("--all", "_all_instances", is_flag=True, help="Stop all instances.")
@click.pass_obj
@async_command
async def stop(obj: Obj, instance: tuple[Instance, ...], _all_instances: bool) -> None:
    """Stop PostgreSQL INSTANCE"""
    with obj.lock, audit():
        for i in instance:
            with manager.from_instance(i.postgresql):
                await instances.stop(i)


@cli.command("reload")
@postgresql_instance_identifier(nargs=-1)
@click.option("--all", "_all_instances", is_flag=True, help="Reload all instances.")
@click.pass_obj
@async_command
async def reload(
    obj: Obj, instance: tuple[PostgreSQLInstance, ...], _all_instances: bool
) -> None:
    """Reload PostgreSQL INSTANCE"""
    with obj.lock, audit():
        for i in instance:
            with manager.from_instance(i):
                await instances.reload(i)


@cli.command("restart")
@instance_identifier(nargs=-1)
@click.option("--all", "_all_instances", is_flag=True, help="Restart all instances.")
@click.pass_obj
@async_command
async def restart(
    obj: Obj, instance: tuple[Instance, ...], _all_instances: bool
) -> None:
    """Restart PostgreSQL INSTANCE"""
    with obj.lock, audit():
        for i in instance:
            with manager.from_instance(i.postgresql):
                await instances.restart(i)


@cli.command("exec")
@instance_identifier(nargs=1, required=True)
@click.argument("command", required=True, nargs=-1, type=click.UNPROCESSED)
def exec(instance: Instance, command: tuple[str, ...]) -> None:
    """Execute COMMAND in the libpq environment for PostgreSQL INSTANCE.

    COMMAND parts may need to be prefixed with -- to separate them from
    options when confusion arises.
    """
    instances.exec(instance, command)


def get_shell(
    _context: click.Context, param: click.Parameter, value: str | None
) -> str:
    if value is None:
        try:
            value = os.environ["SHELL"]
        except KeyError:
            raise click.UsageError(
                f"SHELL environment variable not found; try to use {'/'.join(param.opts)} option"
            ) from None
    return value


@cli.command("shell")
@instance_identifier(nargs=1)
@click.option(
    "--shell",
    type=click.Path(exists=True, dir_okay=False),
    callback=get_shell,
    help="Path to shell executable",
)
def shell(instance: Instance, shell: str) -> None:
    """Start a shell with instance environment.

    Unless --shell option is specified, the $SHELL environment variable is
    used to guess which shell executable to use.
    """
    env = instances.env_for(instance, path=True)
    click.echo(f"Starting {shell!r} with {instance} environment")
    os.execle(shell, shell, os.environ | env)  # nosec


@cli.command("env")
@instance_identifier(nargs=1)
@output_format_option
def env(instance: Instance, output_format: OutputFormat | None) -> None:
    """Output environment variables suitable to handle to PostgreSQL INSTANCE.

    This can be injected in shell using:

        export $(pglift instance env myinstance)
    """
    instance_env = instances.env_for(instance, path=True)
    if output_format == "json":
        print_json_for(instance_env)
    else:
        for key, value in sorted(instance_env.items()):
            click.echo(f"{key}={value}")


@cli.command("logs")
@click.option("--follow/--no-follow", "-f/", default=False, help="Follow log output.")
@postgresql_instance_identifier(nargs=1)
def logs(instance: PostgreSQLInstance, follow: bool) -> None:
    """Output PostgreSQL logs of INSTANCE.

    This assumes that the PostgreSQL instance is configured to use file-based
    logging (i.e. log_destination amongst 'stderr' or 'csvlog').
    """
    if follow:
        logstream = postgresql.logs(instance)
    else:
        logstream = postgresql.logs(instance, timeout=0)
    try:
        for line in logstream:
            click.echo(line, nl=False)
    except TimeoutError:
        pass
    except FileNotFoundError as e:
        raise click.ClickException(str(e)) from None


@cli.command("privileges")
@postgresql_instance_identifier(nargs=1)
@click.option(
    "-d",
    "--database",
    "databases",
    multiple=True,
    help="Database to inspect. When not provided, all databases are inspected.",
)
@click.option("-r", "--role", "roles", multiple=True, help="Role to inspect")
@click.option("--default", "defaults", is_flag=True, help="Display default privileges")
@output_format_option
@async_command
async def list_privileges(
    instance: PostgreSQLInstance,
    databases: Sequence[str],
    roles: Sequence[str],
    defaults: bool,
    output_format: OutputFormat | None,
) -> None:
    """List privileges on INSTANCE's databases."""
    async with postgresql.running(instance):
        try:
            prvlgs = await privileges.get(
                instance, databases=databases, roles=roles, defaults=defaults
            )
        except ValueError as e:
            raise click.ClickException(str(e)) from None
    if output_format == "json":
        print_json_for([model_dump(p) for p in prvlgs])
    else:
        if defaults:
            title = f"Default privileges on instance {instance}"
        else:
            title = f"Privileges on instance {instance}"
        print_table_for(prvlgs, model_dump, title=title)


@cli.command("upgrade")
@instance_identifier(nargs=1)
@click.option(
    "--version",
    "newversion",
    type=click.Choice(POSTGRESQL_VERSIONS),
    help="PostgreSQL version of the new instance (default to site-configured value).",
)
@click.option(
    "--name", "newname", help="Name of the new instance (default to old instance name)."
)
@click.option(
    "--port", required=False, type=click.INT, help="Port of the new instance."
)
@click.argument("extra_opts", nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
@async_command
async def upgrade(
    obj: Obj,
    instance: Instance,
    newversion: PostgreSQLVersion | None,
    newname: str | None,
    port: int | None,
    extra_opts: tuple[str, ...],
) -> None:
    """Upgrade INSTANCE using pg_upgrade

    Extra options can be passed to the pg_upgrade command. They may need to be prefixed
    with -- to separate them from the current command options when confusion arises. When using
    extra options, providing the instance identifier is required.
    """
    with obj.lock, audit():
        await postgresql.check_status(instance.postgresql, Status.not_running)
        with manager.from_instance(instance.postgresql):
            async with task.async_transaction():
                new_instance = await instances.upgrade(
                    instance,
                    version=newversion,
                    name=newname,
                    port=port,
                    extra_opts=extra_opts,
                )
                await instances.start(new_instance)
