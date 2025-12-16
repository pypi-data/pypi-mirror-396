# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from functools import partial

import click

from pglift import diff, exceptions, prometheus, task, types
from pglift.models import interface
from pglift.prometheus import impl
from pglift.prometheus import register_if as register_if
from pglift.prometheus.models.interface import PostgresExporter

from . import _site, hookimpl, model
from .util import (
    Group,
    ManifestData,
    Obj,
    OutputFormat,
    async_command,
    audit,
    diff_options,
    dry_run_option,
    foreground_option,
    manifest_option,
    output_format_option,
    print_argspec,
    print_json_for,
    print_result_diff,
    print_schema,
)


@click.group("postgres_exporter", cls=Group)
@click.option(
    "--schema",
    is_flag=True,
    callback=partial(print_schema, model=PostgresExporter),
    expose_value=False,
    is_eager=True,
    help="Print the JSON schema of postgres_exporter model and exit.",
)
@click.option(
    "--ansible-argspec",
    is_flag=True,
    callback=partial(print_argspec, model=PostgresExporter),
    expose_value=False,
    is_eager=True,
    hidden=True,
    help="Print the Ansible argspec of postgres_exporter model and exit.",
)
def cli() -> None:
    """Handle Prometheus postgres_exporter"""


@cli.command("apply")
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
    """Apply manifest as a Prometheus postgres_exporter."""
    settings = prometheus.get_settings(_site.SETTINGS)
    name = data["name"]
    op: types.Operation = "update" if impl.exists(name, settings) else "create"
    with types.validation_context(operation=op):
        exporter = PostgresExporter.model_validate(data)
    if dry_run:
        ret = interface.ApplyResult(change_state=None)
    else:
        with obj.lock, audit(dry_run=dry_run), diff.enabled(diff_format):
            ret = await impl.apply(exporter, _site.SETTINGS, settings)
    if output_format == "json":
        print_json_for(ret)
    else:
        print_result_diff(ret)


@cli.command("install")
@model.as_parameters(PostgresExporter, "create")
@click.pass_obj
@async_command
async def install(obj: Obj, postgresexporter: PostgresExporter) -> None:
    """Install the service for a (non-local) instance."""
    settings = prometheus.get_settings(_site.SETTINGS)
    with obj.lock, audit():
        async with task.async_transaction():
            await impl.apply(postgresexporter, _site.SETTINGS, settings)


@cli.command("uninstall")
@click.argument("name")
@click.pass_obj
@async_command
async def uninstall(obj: Obj, name: str) -> None:
    """Uninstall the service."""
    with obj.lock, audit():
        await impl.drop(_site.SETTINGS, name)


@cli.command("start")
@click.argument("name")
@foreground_option
@click.pass_obj
@async_command
async def start(obj: Obj, name: str, foreground: bool) -> None:
    """Start postgres_exporter service NAME.

    The NAME argument is a local identifier for the postgres_exporter
    service. If the service is bound to a local instance, it should be
    <version>-<name>.
    """
    settings = prometheus.get_settings(_site.SETTINGS)
    with obj.lock, audit():
        service = impl.system_lookup(name, settings)
        if service is None:
            raise exceptions.InstanceNotFound(name)
        await impl.start(_site.SETTINGS, service, foreground=foreground)


@cli.command("stop")
@click.argument("name")
@click.pass_obj
@async_command
async def stop(obj: Obj, name: str) -> None:
    """Stop postgres_exporter service NAME.

    The NAME argument is a local identifier for the postgres_exporter
    service. If the service is bound to a local instance, it should be
    <version>-<name>.
    """
    settings = prometheus.get_settings(_site.SETTINGS)
    with obj.lock, audit():
        service = impl.system_lookup(name, settings)
        if service is None:
            raise exceptions.InstanceNotFound(name)
        await impl.stop(_site.SETTINGS, service)


@hookimpl
def command() -> click.Group:
    return cli
