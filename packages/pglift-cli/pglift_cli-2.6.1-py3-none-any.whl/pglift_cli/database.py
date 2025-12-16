# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import functools
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import click
import psycopg
from attrs import asdict

from pglift import databases, diff, postgresql, privileges, task
from pglift.models import PostgreSQLInstance, interface
from pglift.util import deep_update

from . import model
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


@click.group("database", cls=Group)
@instance_identifier_option
@click.option(
    "--schema",
    is_flag=True,
    callback=functools.partial(print_schema, model=interface.Database),
    expose_value=False,
    is_eager=True,
    help="Print the JSON schema of database model and exit.",
)
@click.option(
    "--ansible-argspec",
    is_flag=True,
    callback=functools.partial(print_argspec, model=interface.Database),
    expose_value=False,
    is_eager=True,
    hidden=True,
    help="Print the Ansible argspec of database model and exit.",
)
def cli(**kwargs: Any) -> None:
    """Manage databases."""


@cli.command("create")
@model.as_parameters(interface.Database, "create")
@dry_run_option
@pass_postgresql_instance
@click.pass_obj
@async_command
async def create(
    obj: Obj,
    instance: PostgreSQLInstance,
    database: interface.Database,
    dry_run: bool,
) -> None:
    """Create a database in a PostgreSQL instance"""
    with obj.lock, audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            if await databases.exists(instance, database.name):
                raise click.ClickException("database already exists")
            async with task.async_transaction():
                await databases.apply(instance, database)


@cli.command("alter")
@model.as_parameters(interface.Database, "update")
@click.argument("dbname")
@dry_run_option
@pass_postgresql_instance
@click.pass_obj  # type: ignore[arg-type]
@async_command
async def alter(
    obj: Obj,
    instance: PostgreSQLInstance,
    dbname: str,
    dry_run: bool,
    **changes: Any,
) -> None:
    """Alter a database in a PostgreSQL instance"""
    with obj.lock, audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            values = (await databases.get(instance, dbname)).model_dump(by_alias=True)
            values = deep_update(values, changes)
            altered = interface.Database.model_validate(values)
            await databases.apply(instance, altered)


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
    """Apply manifest as a database"""
    database = interface.Database.model_validate(data)
    with (
        obj.lock,
        audit(dry_run=dry_run),
        diff.enabled(diff_format),
        system_configure(dry_run=dry_run),
    ):
        async with postgresql.running(instance):
            ret = await databases.apply(instance, database)
    if output_format == "json":
        print_json_for(ret)
    else:
        print_result_diff(ret)


@cli.command("get")
@output_format_option
@click.argument("name")
@pass_postgresql_instance
@async_command
async def get(
    instance: PostgreSQLInstance, name: str, output_format: OutputFormat | None
) -> None:
    """Get the description of a database"""
    async with postgresql.running(instance):
        db = await databases.get(instance, name)
    if output_format == "json":
        print_json_for(model_dump(db))
    else:
        print_table_for(
            [db], functools.partial(model_dump, context={"pretty": True}), box=None
        )


@cli.command("list")
@output_format_option
@click.option(
    "-x",
    "--exclude-database",
    "exclude_dbnames",
    multiple=True,
    help="Database to exclude from listing.",
)
@click.argument("dbname", nargs=-1)
@pass_postgresql_instance
@async_command
async def ls(
    instance: PostgreSQLInstance,
    dbname: Sequence[str],
    exclude_dbnames: Sequence[str],
    output_format: OutputFormat | None,
) -> None:
    """List databases (all or specified ones)

    Only queried databases are shown when DBNAME is specified.
    """

    async with postgresql.running(instance):
        dbs = await databases.ls(
            instance, dbnames=dbname, exclude_dbnames=exclude_dbnames
        )
    if output_format == "json":
        print_json_for([model_dump(db) for db in dbs])
    else:
        print_table_for(dbs, model_dump)


@cli.command("drop")
@model.as_parameters(interface.DatabaseDropped, "create")
@dry_run_option
@pass_postgresql_instance
@click.pass_obj
@async_command
async def drop(
    obj: Obj,
    instance: PostgreSQLInstance,
    databasedropped: interface.DatabaseDropped,
    dry_run: bool,
) -> None:
    """Drop a database"""
    with obj.lock, audit(dry_run=dry_run), system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            await databases.drop(instance, databasedropped)


@cli.command("privileges")
@click.argument("name")
@click.option("-r", "--role", "roles", multiple=True, help="Role to inspect")
@click.option("--default", "defaults", is_flag=True, help="Display default privileges")
@output_format_option
@pass_postgresql_instance
@async_command
async def list_privileges(
    instance: PostgreSQLInstance,
    name: str,
    roles: Sequence[str],
    defaults: bool,
    output_format: OutputFormat | None,
) -> None:
    """List privileges on a database."""
    async with postgresql.running(instance):
        await databases.get(instance, name)  # check existence
        try:
            prvlgs = await privileges.get(
                instance, databases=(name,), roles=roles, defaults=defaults
            )
        except ValueError as e:
            raise click.ClickException(str(e)) from None
    if output_format == "json":
        print_json_for([model_dump(p) for p in prvlgs])
    else:
        print_table_for(prvlgs, model_dump)


@cli.command("run")
@click.argument("sql_command")
@click.option(
    "-d", "--database", "dbnames", multiple=True, help="Database to run command on"
)
@click.option(
    "-x",
    "--exclude-database",
    "exclude_dbnames",
    multiple=True,
    help="Database to not run command on",
)
@output_format_option
@pass_postgresql_instance
@async_command
async def run(
    instance: PostgreSQLInstance,
    sql_command: str,
    dbnames: Sequence[str],
    exclude_dbnames: Sequence[str],
    output_format: OutputFormat | None,
) -> None:
    """Run given command on databases of a PostgreSQL instance"""
    async with postgresql.running(instance):
        try:
            result = await databases.run(
                instance,
                sql_command,
                dbnames=dbnames,
                exclude_dbnames=exclude_dbnames,
            )
        except psycopg.ProgrammingError as e:
            raise click.ClickException(str(e)) from None
    if output_format == "json":
        print_json_for(result)
    else:
        for dbname, rows in result.items():
            print_table_for(rows, lambda m: m, title=f"Database {dbname}")


@cli.command("dump")
@click.option(
    "-o",
    "--output",
    metavar="DIRECTORY",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Write dump file(s) to DIRECTORY instead of default dumps directory.",
)
@click.argument("dbname")
@pass_postgresql_instance
@dry_run_option
@async_command
async def dump(
    instance: PostgreSQLInstance, dbname: str, output: Path | None, dry_run: bool
) -> None:
    """Dump a database"""
    with system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            await databases.dump(instance, dbname, output)


@cli.command("dumps")
@click.argument("dbname", nargs=-1)
@output_format_option
@pass_postgresql_instance
@async_command
async def dumps(
    instance: PostgreSQLInstance,
    dbname: Sequence[str],
    output_format: OutputFormat | None,
) -> None:
    """List the database dumps

    Only dumps created in the default dumps directory are listed.
    """
    values = [asdict(dump) async for dump in databases.dumps(instance, dbnames=dbname)]
    if output_format == "json":
        print_json_for(values)
    else:
        dbnames = ", ".join(dbname) if dbname else "all databases"
        print_table_for(values, lambda d: d, title=f"Dumps for {dbnames}")


@cli.command("restore")
@click.argument("dump_id")
@click.argument("targetdbname", required=False)
@pass_postgresql_instance
@dry_run_option
@async_command
async def restore(
    instance: PostgreSQLInstance, dump_id: str, targetdbname: str | None, dry_run: bool
) -> None:
    """Restore a database dump

    DUMP_ID identifies the dump id.

    TARGETDBNAME identifies the (optional) name of the database in which the
    dump is reloaded. If provided, the database needs to be created beforehand.

    If TARGETDBNAME is not provided, the dump is reloaded using the database
    name that appears in the dump. In this case, the restore command will
    create the database so it needs to be dropped before running the command.
    """
    with system_configure(dry_run=dry_run):
        async with postgresql.running(instance):
            await databases.restore(instance, dump_id, targetdbname)
