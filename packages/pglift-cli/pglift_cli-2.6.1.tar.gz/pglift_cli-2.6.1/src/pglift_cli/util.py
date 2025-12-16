# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import abc
import asyncio
import inspect
import json
import logging
import logging.handlers
import os
import shlex
import sys
import tempfile
import time
import typing
from collections.abc import Callable, Coroutine, Iterable, Iterator, Sequence
from contextlib import contextmanager, nullcontext
from datetime import timedelta
from functools import cache, cached_property, partial, singledispatch, wraps
from pathlib import Path
from typing import IO, Any, Literal, ParamSpec, TypedDict, TypeVar

import click
import filelock
import humanize
import psycopg
import pydantic
import pydantic_core
import rich
import rich.prompt
import yaml
from click.shell_completion import CompletionItem
from rich.console import Console
from rich.table import Table

from pglift import exceptions, instances, system
from pglift.models import Instance, PostgreSQLInstance, helpers, interface
from pglift.settings import PostgreSQLVersion, Settings
from pglift.system import install
from pglift.types import ByteSizeType

from . import __name__ as pkgname
from . import _site, logger, loggers
from ._settings import CLISettings
from .console import console


def model_dump(
    m: pydantic.BaseModel, by_alias: bool = True, **kwargs: Any
) -> dict[str, Any]:
    return m.model_dump(by_alias=by_alias, **kwargs)


@singledispatch
def prettify(value: Any, *args: Any) -> str:
    """Prettify a value."""
    return str(value)


@prettify.register(int)
def _(value: int, annotations: Sequence[Any] = ()) -> str:
    """Prettify an integer value"""
    for a in annotations:
        if isinstance(a, ByteSizeType):
            return a.human_readable(value)
    return str(value)


@prettify.register(list)
def _(value: list[Any], *args: Any) -> str:
    """Prettify a List value"""
    return ", ".join(str(x) for x in value)


@prettify.register(set)
def _(value: set[Any], annotations: Sequence[Any] = ()) -> str:
    """Prettify a Set value"""
    return prettify(sorted(value), annotations)


@prettify.register(type(None))
def _(*args: Any) -> str:
    """Prettify a None value"""
    return ""


@prettify.register(dict)
def _(value: dict[str, Any], *args: Any) -> str:
    """Prettify a Dict value"""

    def prettify_dict(
        d: dict[str, Any], level: int = 0, indent: str = "  "
    ) -> Iterator[str]:
        for key, value in d.items():
            row = f"{indent * level}{key}:"
            if isinstance(value, dict):
                yield row
                yield from prettify_dict(value, level + 1)
            else:
                yield row + " " + prettify(value)

    return "\n".join(prettify_dict(value))


_I = TypeVar("_I")


def print_table_for(
    items: Iterable[_I],
    asdict: Callable[[_I], dict[str, Any]],
    title: str | None = None,
    *,
    console: Console = console,
    **kwargs: Any,
) -> None:
    """Render a list of items as a table."""
    headers: list[str] = []
    rows = []
    for item in items:
        row = []
        hdr = []
        annotations = typing.get_type_hints(item.__class__, include_extras=True)
        for k, v in asdict(item).items():
            f_annotations = []
            try:
                i_annotations = annotations[k]
            except KeyError:
                pass
            else:
                if args := typing.get_args(i_annotations):
                    _, *f_annotations = args
            hdr.append(k)
            row.append(prettify(v, f_annotations))
        if not headers:
            headers = hdr[:]
        rows.append(row)
    if not rows:
        return
    table = Table(title=title, **kwargs)
    # https://github.com/Textualize/rich/issues/3761
    overflow: Literal["ellipsis", "fold"] = (
        "fold" if console.options.ascii_only else "ellipsis"
    )
    for header in headers:
        table.add_column(header, overflow=overflow)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_json_for(data: Any, *, console: Console = console) -> None:
    """Render `data` as JSON."""
    console.print_json(data=pydantic_core.to_jsonable_python(data, by_alias=True))


def print_result_diff(
    r: interface.ApplyResult, /, *, console: Console = console
) -> None:
    if r.diff is not None:
        for diffitem in r.diff:
            console.print(diffitem)


P = ParamSpec("P")


def print_schema(
    context: click.Context,
    _param: click.Parameter,
    value: bool,
    *,
    model: type[pydantic.BaseModel],
    console: Console = console,
) -> None:
    """Callback for --schema flag."""
    if value:
        console.print_json(data=model.model_json_schema())
        context.exit()


def print_argspec(
    context: click.Context,
    _param: click.Parameter,
    value: bool,
    *,
    model: type[pydantic.BaseModel],
) -> None:
    """Callback for --ansible-argspec flag."""
    if value:
        click.echo(
            json.dumps(helpers.argspec_from_model(model), sort_keys=False, indent=2)
        )
        context.exit()


def pass_instance(f: Callable[P, None]) -> Callable[P, None]:
    """Command decorator passing 'instance' bound to click.Context's object."""

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        context = click.get_current_context()
        instance = context.obj.instance
        assert isinstance(instance, Instance), instance
        context.invoke(f, instance, *args, **kwargs)

    return wrapper


def pass_postgresql_instance(f: Callable[P, None]) -> Callable[P, None]:
    """Command decorator passing PostgreSQL 'instance' bound to
    click.Context's object.
    """

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        context = click.get_current_context()
        instance = context.obj.postgresql_instance
        assert isinstance(instance, PostgreSQLInstance), instance
        context.invoke(f, instance, *args, **kwargs)

    return wrapper


def get_postgresql_instance(
    name: str, version: PostgreSQLVersion | None, settings: Settings
) -> PostgreSQLInstance:
    """Return a PostgreSQLInstance from name/version, possibly guessing version if unspecified."""
    if version is None:
        found = None
        for v in settings.postgresql.versions:
            version = v.version
            try:
                instance = PostgreSQLInstance.system_lookup(name, version, settings)
            except exceptions.InstanceNotFound:
                logger.debug("instance '%s' not found in version %s", name, version)
            else:
                if found:
                    raise click.BadParameter(
                        f"instance {name!r} exists in several PostgreSQL versions;"
                        " please select version explicitly"
                    )
                found = instance

        if found:
            return found

        raise click.BadParameter(f"instance {name!r} not found")

    try:
        return PostgreSQLInstance.system_lookup(name, version, settings)
    except Exception as e:
        raise click.BadParameter(str(e)) from None


def get_instance(
    name: str, version: PostgreSQLVersion | None, settings: Settings
) -> Instance:
    """Return an Instance from name/version, possibly guessing version if unspecified."""
    pg_instance = get_postgresql_instance(name, version, settings)
    return Instance.from_postgresql(pg_instance)


def nameversion_from_id(instance_id: str) -> tuple[str, PostgreSQLVersion | None]:
    version = None
    try:
        version, name = instance_id.split("/", 1)
    except ValueError:
        name = instance_id
    return name, typing.cast(PostgreSQLVersion, version)


def postgresql_instance_lookup(
    context: click.Context, param: click.Parameter, value: None | str | tuple[str]
) -> PostgreSQLInstance | tuple[PostgreSQLInstance, ...]:
    """Return one or more PostgreSQLInstance, possibly guessed if there
    is only one on system, depending on 'param' variadic flag (nargs).
    """

    settings = _site.SETTINGS

    def guess() -> PostgreSQLInstance:
        """Return the PostgreSQLInstance found on system, if there's
        only one, or fail.
        """
        try:
            (i,) = instances.system_list(settings)
        except ValueError:
            raise click.UsageError(
                f"argument {param.get_error_hint(context)} is required."
            ) from None
        return i

    if context.params.get("_all_instances"):
        return tuple(instances.system_list(settings))

    if param.nargs == 1:
        if value is None:
            return guess()
        else:
            assert isinstance(value, str)
            name, version = nameversion_from_id(value)
            return get_postgresql_instance(name, version, settings)

    elif param.nargs == -1:
        assert isinstance(value, tuple)
        if value:
            return tuple(
                get_postgresql_instance(*nameversion_from_id(item), settings)
                for item in value
            )
        else:
            return (guess(),)

    else:
        raise AssertionError(f"unexpected nargs={param.nargs}")


def instance_lookup(
    context: click.Context, param: click.Parameter, value: None | str | tuple[str]
) -> Instance | tuple[Instance, ...]:
    """Return one or more Instance, possibly guessed if there is only
    one on system, depending on 'param' variadic flag (nargs).
    """
    pg_value = postgresql_instance_lookup(context, param, value)
    if isinstance(pg_value, tuple):
        return tuple(Instance.from_postgresql(i) for i in pg_value)
    return Instance.from_postgresql(pg_value)


def instance_bind_context(
    context: click.Context, param: click.Parameter, value: str | None
) -> None:
    """Bind PostgreSQL instance specified as -i/--instance to context's
    object, possibly guessing from available instance if there is only one.
    """
    obj: Obj = context.obj
    if value is None:
        values = list(instances.system_list(_site.SETTINGS))
        if not values:
            obj._instance = "no instance found; create one first."
            return
        elif len(values) > 1:
            option = param.get_error_hint(context)
            obj._instance = f"several instances found; option {option} is required."
            return
        (pg_instance,) = values
    else:
        pg_instance = get_postgresql_instance(
            *nameversion_from_id(value), _site.SETTINGS
        )
    obj._instance = pg_instance


def _list_instances(
    _context: click.Context, _param: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    """Shell completion function for instance identifier <name> or <version>/<name>."""
    out = []
    iname, iversion = nameversion_from_id(incomplete)
    for i in instances.system_list(_site.SETTINGS):
        if iversion is not None and i.version.startswith(iversion):
            if i.name.startswith(iname):
                out.append(
                    CompletionItem(f"{i.version}/{i.name}", help=f"port={i.port}")
                )
            else:
                out.append(CompletionItem(i.version))
        else:
            out.append(
                CompletionItem(i.name, help=f"{i.version}/{i.name} port={i.port}")
            )
    return out


F = TypeVar("F", bound=Callable[..., Any])


def _instance_identifier(
    callback: Callable[[click.Context, click.Parameter, Any], Any],
    nargs: int = 1,
    required: bool = False,
) -> Callable[[F], F]:
    def decorator(fn: F) -> F:
        command = click.argument(
            "instance",
            nargs=nargs,
            required=required,
            callback=callback,
            shell_complete=_list_instances,
        )(fn)
        doc = inspect.getdoc(command)
        assert doc
        doc += (
            "\n\nINSTANCE identifies target instance as <version>/<name> where the "
            "<version>/ prefix may be omitted if there is only one instance "
            "matching <name>."
        )
        command.__doc__ = doc
        if not required:
            command.__doc__ += " Required if there is more than one instance on system."
        return command

    return decorator


postgresql_instance_identifier = partial(
    _instance_identifier, postgresql_instance_lookup
)
instance_identifier = partial(_instance_identifier, instance_lookup)

instance_identifier_option = click.option(
    "-i",
    "--instance",
    "instance",
    metavar="<version>/<name>",
    callback=instance_bind_context,
    shell_complete=_list_instances,
    help=(
        "Instance identifier; the <version>/ prefix may be omitted if "
        "there's only one instance matching <name>. "
        "Required if there is more than one instance on system."
    ),
)


def yaml_load(
    _ctx: click.Context, _param: click.Parameter, value: IO[str]
) -> dict[str, Any]:
    try:
        data = yaml.safe_load(value)
    except yaml.YAMLError as e:
        raise click.BadParameter(f"invalid YAML: {e}") from e
    if not isinstance(data, dict):
        raise click.BadParameter(f"invalid YAML: expecting an object, got {type(data)}")
    if "name" not in data:
        raise click.BadParameter("invalid YAML: missing required 'name' field")
    return data


manifest_option = click.option(
    "-f",
    "--file",
    "data",
    type=click.File("r"),
    metavar="MANIFEST",
    required=True,
    callback=yaml_load,
)


class ManifestData(TypedDict, total=False):
    name: str


OutputFormat = Literal["json"]


def set_output_format(
    ctx: click.Context, _param: click.Parameter, value: OutputFormat
) -> OutputFormat:
    assert ctx.obj.output_format is None
    ctx.obj.output_format = value
    return value


output_format_option = click.option(
    "-o",
    "--output-format",
    type=click.Choice(typing.get_args(OutputFormat), case_sensitive=False),
    callback=set_output_format,
    help="Specify the output format.",
)

diff_options = {
    "unified": click.option(
        "--diff",
        "diff_format",
        flag_value="unified",
        help="Include differences resulting from applied changes in returned result.",
    ),
    "ansible": click.option(
        "--ansible-diff",
        "diff_format",
        flag_value="ansible",
        help="Include differences resulting from applied changes in returned result using Ansible's diff format.",
        hidden=True,
    ),
}

dry_run_option = click.option(
    "--dry-run", is_flag=True, help="Simulate change operations."
)


def validate_foreground(
    _context: click.Context, _param: click.Parameter, value: bool
) -> bool:
    if _site.SETTINGS.service_manager == "systemd" and value:
        raise click.BadParameter("cannot be used with systemd")
    return value


foreground_option = click.option(
    "--foreground",
    is_flag=True,
    help="Start the program in foreground.",
    callback=validate_foreground,
)


@contextmanager
def system_configure(*, dry_run: bool) -> Iterator[None]:
    with system.configure(dry_run=dry_run):
        yield
    if dry_run:
        click.echo("DRY RUN: no changes made", err=True)


@contextmanager
def audit(
    command: Sequence[str] = sys.argv,
    settings: CLISettings | None = None,
    *,
    dry_run: bool = False,
) -> Iterator[None]:
    """Context manager handling log messages to the audit file, if configured
    in site settings.
    """
    if settings is None:
        settings = _site.SETTINGS.cli
    if (audit_settings := settings.audit) is None:
        yield None
        return

    audit_file = audit_settings.path
    if not audit_file.parent.exists():
        logger.debug("creating audit file parent directory")
        audit_file.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("using audit file %s", audit_file)

    handler = logging.handlers.WatchedFileHandler(audit_file)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt=audit_settings.log_format, datefmt=audit_settings.date_format
    )
    handler.setFormatter(formatter)

    loggrs = [logging.getLogger(n) for n in loggers]
    for loggr in loggrs:
        loggr.addHandler(handler)

    # The audit logger, as defined here, is only meant to emit start/end
    # messages below; and we avoid them to get propagated to higher logger.
    audit_logger = logging.getLogger(pkgname).getChild("audit")
    audit_logger.propagate = False
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.DEBUG)

    msg = "command: %s"
    if dry_run:
        msg += " (DRY RUN)"
    audit_logger.info(msg, shlex.join(command))
    started_at = time.monotonic()

    try:
        yield None
    except Exception as exc:
        if isinstance(exc, exceptions.Cancelled):
            msg, level = "command cancelled (%s)", logging.WARNING
        else:
            msg, level = "command failed (%s)", logging.ERROR
        raise
    else:
        msg, level = "command completed (%s)", logging.INFO
    finally:
        # Note: by removing the audit handler from loggers managed above, we
        # avoid termination messages (typically those emitted in
        # Command.invoke()) to be emitted in this handler.
        # If this appears to be a bad idea, removeHandler() should be invoked
        # through context.call_on_close().
        for loggr in loggrs:
            loggr.removeHandler(handler)
        elapsed = humanize.precisedelta(
            timedelta(seconds=time.monotonic() - started_at)
        )
        audit_logger.log(level, msg, elapsed)
        audit_logger.removeHandler(handler)
        handler.close()


@contextmanager
def command_logging() -> Iterator[None]:
    """Log any unexpected error, i.e. not one of our exceptions or one we
    explicitly raised, to a debug file.

    This only makes sense when not in --debug mode; otherwise, the bare
    exception will propagate to stderr.
    """
    logfilename = f"{time.time()}.log"
    with tempfile.NamedTemporaryFile(prefix="pglift-", suffix="-" + logfilename) as tmp:
        logfile = Path(tmp.name)
    logger.debug("debug logging at %s", logfile)
    handler = logging.FileHandler(logfile)
    formatter = logging.Formatter(
        fmt="%(levelname)-8s - %(asctime)s - %(name)s:%(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    for name in loggers:
        logging.getLogger(name).addHandler(handler)
    keep_logfile = False
    try:
        yield None
    except (click.Abort, click.ClickException, click.exceptions.Exit):
        raise
    except Exception:
        keep_logfile = True
        msg = "an unexpected error occurred"
        logger.error(msg)
        # Only log the traceback to the log file; for this, instantiate a
        # specific logger (unrelated to application loggers hierarchy).
        flogger = logging.getLogger(f"{pkgname}_debug")
        flogger.addHandler(handler)
        flogger.exception(msg)
        raise click.ClickException(
            "an unexpected error occurred, this is probably a bug; "
            f"details can be found at {logfile}"
        ) from None
    finally:
        if not keep_logfile:
            os.unlink(logfile)


class InteractiveUserInterface:
    """An interactive UI that prompts for confirmation."""

    def confirm(self, message: str, default: bool) -> bool:
        return rich.prompt.Confirm().ask(
            f"[yellow]>[/yellow] {message}", default=default
        )

    @cache
    def prompt(self, message: str, hide_input: bool = False) -> str:
        return rich.prompt.Prompt().ask(
            f"[yellow]>[/yellow] {message}", password=hide_input
        )


class Obj:
    """Object bound to click.Context"""

    # Set in commands taking a -i/--instance option through
    # instance_identifier_option decorator's callback.
    _instance: str | PostgreSQLInstance

    def __init__(
        self, *, debug: bool = False, output_format: OutputFormat | None = None
    ) -> None:
        self.debug = debug
        self.output_format = output_format

    @cached_property
    def lock(self) -> filelock.FileLock:
        """Lock to prevent concurrent execution."""
        lockfile = _site.SETTINGS.cli.lock_file
        lockfile.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        return filelock.FileLock(lockfile, timeout=0)

    @cached_property
    def postgresql_instance(self) -> PostgreSQLInstance:
        if isinstance(self._instance, PostgreSQLInstance):
            return self._instance
        else:
            assert isinstance(self._instance, str)
            raise click.UsageError(self._instance)

    @cached_property
    def instance(self) -> Instance:
        return Instance.from_postgresql(self.postgresql_instance)


def async_command(
    callback: Callable[P, Coroutine[None, None, None]],
) -> Callable[P, None]:
    @wraps(callback)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.run(callback(*args, **kwargs))

    return wrapper


class Command(click.Command):
    def invoke(self, context: click.Context) -> Any:
        obj: Obj = context.obj
        with command_logging() if not obj.debug else nullcontext(None):
            try:
                return super().invoke(context)
            except filelock.Timeout:
                raise click.ClickException("another operation is in progress") from None
            except exceptions.Cancelled as e:
                logger.warning(str(e))
                raise click.Abort from None
            except pydantic.ValidationError as e:
                logger.debug("a validation error occurred", exc_info=obj.debug)
                if context.obj.output_format == "json":
                    console.print_json(e.json(include_url=False, include_context=False))
                raise click.ClickException(str(e)) from None
            except exceptions.Error as e:
                logger.debug("an internal error occurred", exc_info=obj.debug)
                msg = str(e)
                if isinstance(e, exceptions.CommandError):
                    if e.stderr:
                        msg += f"\n{e.stderr}"
                    if e.stdout:
                        msg += f"\n{e.stdout}"
                raise click.ClickException(msg) from None
            except psycopg.DatabaseError as e:
                logger.debug(
                    "a database error occurred: %s (SQLSTATE=%s)",
                    e,
                    e.sqlstate,
                    exc_info=obj.debug,
                )
                raise click.ClickException(str(e).strip()) from None


def is_root() -> bool:
    return os.getuid() == 0


class Group(click.Group):
    command_class = Command
    group_class = type

    def add_command(self, command: click.Command, name: str | None = None) -> None:
        name = name or command.name
        assert name not in self.commands, f"command {name!r} already registered"
        super().add_command(command, name)

    def invoke(self, ctx: click.Context) -> Any:
        if set(ctx.help_option_names) - set(ctx.args):
            if is_root():
                raise click.ClickException("pglift cannot be used as root")
            if not install.check(_site.SETTINGS):
                raise click.ClickException(
                    "broken installation; did you run 'site-configure install'?",
                )
        return super().invoke(ctx)


class PluggableCommandGroup(abc.ABC, Group):
    _plugin_commands_loaded: bool = False

    @abc.abstractmethod
    def register_plugin_commands(self, obj: Obj) -> None: ...

    def _load_plugins_commands(self, context: click.Context) -> None:
        if self._plugin_commands_loaded:
            return
        obj: Obj | None = context.obj
        if obj is None:
            obj = context.ensure_object(Obj)
        if obj is None:
            return
        self.register_plugin_commands(obj)
        self._plugin_commands_loaded = True

    def list_commands(self, context: click.Context) -> list[str]:
        self._load_plugins_commands(context)
        return super().list_commands(context)

    def get_command(self, context: click.Context, name: str) -> click.Command | None:
        self._load_plugins_commands(context)
        return super().get_command(context, name)
