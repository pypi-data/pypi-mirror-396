# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import sys
import typing
import warnings
from functools import partial
from importlib.metadata import version
from pathlib import Path
from typing import Literal

import click
import click.exceptions
import rich.logging
import rich.text
import rich.tree
import yaml
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.syntax import Syntax

from pglift import ui
from pglift._compat import assert_never
from pglift.system import install
from pglift.types import LogLevel

from . import __name__ as pkgname
from . import _site, loggers
from ._settings import Settings
from .base import CLIGroup
from .console import console as console
from .util import (
    InteractiveUserInterface,
    Obj,
    OutputFormat,
    async_command,
    audit,
    output_format_option,
)


def completion(
    context: click.Context,
    _param: click.Parameter,
    value: Literal["bash", "fish", "zsh"],
) -> None:
    if not value or context.resilient_parsing:
        return
    shell_complete_class_map = {
        "bash": click.shell_completion.BashComplete,
        "fish": click.shell_completion.FishComplete,
        "zsh": click.shell_completion.ZshComplete,
    }
    click.echo(
        shell_complete_class_map[value](cli, {}, "pglift", "_PGLIFT_COMPLETE").source(),
        nl=False,
    )
    context.exit()


def print_version(context: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or context.resilient_parsing:
        return
    cli_version, lib_version = version(pkgname), version("pglift")
    if cli_version == lib_version:
        click.echo(f"pglift version {cli_version}")
    else:
        click.echo(
            f"pglift version {version(pkgname)} (library version {version('pglift')})"
        )
    context.exit()


def log_level(
    _context: click.Context, _param: click.Parameter, value: str | None
) -> int | None:
    if value is None:
        return None
    return getattr(logging, value)  # type: ignore[no-any-return]


@click.group(cls=CLIGroup)
@click.option(
    "-L",
    "--log-level",
    type=click.Choice(typing.get_args(LogLevel), case_sensitive=False),
    default=None,
    callback=log_level,
    help="Set log threshold (default to INFO when logging to stderr or WARNING when logging to a file).",
)
@click.option(
    "-l",
    "--log-file",
    type=click.Path(dir_okay=False, resolve_path=True, path_type=Path),
    metavar="LOGFILE",
    help="Write logs to LOGFILE, instead of stderr.",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    hidden=True,
    help="Set log level to DEBUG and eventually display tracebacks.",
)
@click.option(
    "--interactive/--non-interactive",
    default=True,
    help=(
        "Interactively prompt for confirmation when needed (the default), "
        "or automatically pick the default option for all choices."
    ),
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show program version.",
)
@click.option(
    "--completion",
    type=click.Choice(["bash", "fish", "zsh"]),
    callback=completion,
    expose_value=False,
    is_eager=True,
    help="Output completion for specified shell and exit.",
)
@click.pass_context
def cli(
    context: click.Context,
    log_level: int | None,
    log_file: Path | None,
    debug: bool,
    interactive: bool,
) -> None:
    """Deploy production-ready instances of PostgreSQL"""
    if (cli_version := version(pkgname)) != (lib_version := version("pglift")):
        warnings.warn(
            f"possibly incompatible versions of the library and CLI packages: {lib_version}, {cli_version}",
            RuntimeWarning,
            stacklevel=1,
        )
    if not context.obj:
        context.obj = Obj(debug=debug)
    else:
        assert isinstance(context.obj, Obj), context.obj

    ui_token: ui.Token | None = None
    if interactive:
        ui_token = ui.set(InteractiveUserInterface())

    handler: logging.Handler | rich.logging.RichHandler
    if debug:
        log_level = logging.DEBUG
    cli_settings = _site.SETTINGS.cli
    if log_level is None and (log_level_settings := cli_settings.log_level):
        log_level = getattr(logging, log_level_settings)
    if log_file or not sys.stderr.isatty():
        if log_file:
            handler = logging.FileHandler(log_file)
            context.call_on_close(handler.close)
        else:
            handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt=cli_settings.log_format, datefmt=cli_settings.date_format
        )
        handler.setFormatter(formatter)
        handler.setLevel(log_level or logging.WARNING)
    else:
        handler = rich.logging.RichHandler(
            level=log_level or logging.INFO,
            console=Console(stderr=True),
            show_time=False,
            show_path=False,
            highlighter=NullHighlighter(),
        )

    for name in loggers:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        # Remove rich handler on close since this would pollute all tests
        # stderr otherwise.
        context.call_on_close(partial(logger.removeHandler, handler))

    # Reset contextvars
    if ui_token is not None:
        context.call_on_close(partial(ui.reset, ui_token))


@cli.command("site-settings", hidden=True)
@click.option(
    "--defaults/--no-defaults",
    default=None,
    help="Output only default settings, or only site configuration.",
    show_default=True,
)
@click.option(
    "--schema", is_flag=True, help="Print the JSON Schema of site settings model."
)
@output_format_option
def site_settings(
    defaults: bool | None, schema: bool, output_format: OutputFormat | None
) -> None:
    """Show site settings.

    Without any option, the combination of site configuration and default
    values is shown.
    With --defaults, only default values and those depending on the
    environment are shown (not accounting for site configuration).
    With --no-defaults, the site configuration is shown alone and default
    values are excluded.
    """
    if schema:
        value = Settings.model_json_schema()
    else:
        if defaults:
            value = _site.DEFAULT_SETTINGS.model_dump(mode="json")
        else:
            value = _site.SETTINGS.model_dump(
                mode="json", exclude_defaults=defaults is False
            )
    if output_format == "json":
        console.print_json(data=value)
    else:
        assert output_format is None
        output = yaml.safe_dump(value)
        syntax = Syntax(output, "yaml", background_color="default")
        console.print(syntax)


@cli.command(
    "site-configure",
    hidden=True,
)
@click.argument(
    "action",
    type=click.Choice(["install", "uninstall", "check", "list"]),
    default="install",
)
@click.pass_obj
@click.pass_context
@async_command
async def site_configure(
    context: click.Context, obj: Obj, action: Literal["install", "uninstall", "check"]
) -> None:
    """Manage installation of extra data files for pglift.

    This is an INTERNAL command.
    """
    with obj.lock, audit():
        if action == "install":
            await install.do(_site.SETTINGS)
        elif action == "uninstall":
            await install.undo(_site.SETTINGS)
        elif action == "check":
            if not install.check(_site.SETTINGS):
                context.exit(1)
        elif action == "list":
            for p in install.ls(_site.SETTINGS):
                click.echo(p)
        else:
            assert_never(action)
