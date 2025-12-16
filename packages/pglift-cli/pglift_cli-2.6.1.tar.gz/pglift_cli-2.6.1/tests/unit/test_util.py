# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Literal
from unittest.mock import patch

import click
import pydantic
import pytest
from click.testing import CliRunner
from rich.console import Console

from pglift import exceptions
from pglift.models import interface, system
from pglift.settings import PostgreSQLVersion, Settings
from pglift.types import ByteSizeType
from pglift_cli import util


@pytest.mark.parametrize(
    "value, annotations, expected",
    [
        (1024, [ByteSizeType()], "1.0 kB"),
        (1024, (), "1024"),
        ([None, 1, "foo"], (), "None, 1, foo"),
        ({"z", "b", "a"}, (), "a, b, z"),
        (None, (), ""),
        ({"foo": "bob"}, (), "foo: bob"),
        (
            {"foo": "bob", "bar": {"blah": ["some", 123]}},
            (),
            "\n".join(
                [
                    "foo: bob",
                    "bar:",
                    "  blah: some, 123",
                ]
            ),
        ),
    ],
)
def test_prettify(value: Any, annotations: Sequence[Any], expected: str) -> None:
    assert util.prettify(value, annotations) == expected


@pytest.fixture
def console() -> Console:
    return Console()


def test_print_table_for(console: Console) -> None:
    @dataclass
    class Person:
        name: str
        children: list[str]
        address: dict[str, Any]

    items = [
        Person(
            name="bob",
            children=["marley", "dylan"],
            address={"street": "main street", "zip": 31234, "city": "luz"},
        ),
        Person(
            name="janis",
            children=[],
            address={"street": "robinson lane", "zip": 38650, "city": "mars"},
        ),
    ]
    with console.capture() as capture:
        util.print_table_for(items, asdict, title="address book", console=console)
    assert (
        capture.get()
        == "\n".join(
            [
                "                  address book                   ",
                "┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓",
                "┃ name  ┃ children      ┃ address               ┃",
                "┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩",
                "│ bob   │ marley, dylan │ street: main street   │",
                "│       │               │ zip: 31234            │",
                "│       │               │ city: luz             │",
                "│ janis │               │ street: robinson lane │",
                "│       │               │ zip: 38650            │",
                "│       │               │ city: mars            │",
                "└───────┴───────────────┴───────────────────────┘",
            ]
        )
        + "\n"
    )


class Foo(pydantic.BaseModel):
    bar_: str = pydantic.Field(alias="bar")
    baz: Annotated[
        int, pydantic.PlainSerializer(float, return_type=float, when_used="json")
    ]


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            [Foo(bar="x", baz=1), Foo(bar="y", baz=3)],
            [
                {"bar": "x", "baz": 1.0},
                {"bar": "y", "baz": 3.0},
            ],
        ),
        (
            {
                "name": "p",
                "coords": {"x": 1.2, "y": 3.1415},
                "labels": ("a",),
                "date": date(2021, 10, 27),
            },
            {
                "name": "p",
                "coords": {"x": 1.2, "y": 3.1415},
                "labels": ["a"],
                "date": "2021-10-27",
            },
        ),
    ],
)
def test_print_json_for(data: Any, expected: Any, console: Console) -> None:
    with console.capture() as capture:
        util.print_json_for(data, console=console)
    assert json.loads(capture.get()) == expected


def test_print_result_diff(console: Console) -> None:
    r = interface.ApplyResult()
    assert r.diff is None
    with console.capture() as capture:
        util.print_result_diff(r, console=console)
    assert capture.get() == ""

    r = interface.ApplyResult(diff=["foo", "bar"])
    assert r.diff is not None
    with console.capture() as capture:
        util.print_result_diff(r, console=console)
    assert capture.get() == "foo\nbar\n"


def test_system_configure(runner: CliRunner) -> None:
    @click.command
    @util.dry_run_option
    def my(dry_run: bool) -> None:
        with util.system_configure(dry_run=dry_run):
            click.echo("testing...")

    result = runner.invoke(my, [])
    assert result.stderr == ""
    assert result.stdout == "testing...\n"

    result = runner.invoke(my, ["--dry-run"])
    assert result.stderr == "DRY RUN: no changes made\n"
    assert result.stdout == "testing...\n"


@click.command(cls=util.Command)
@util.output_format_option
@click.argument("error")
@click.pass_context
def mycmd(context: click.Context, error: str, output_format: util.OutputFormat) -> None:
    if error == "error":
        raise exceptions.CommandError(1, ["bad", "cmd"], "output", "errs")
    if error == "cancel":
        raise exceptions.Cancelled("flop")
    if error == "validationerror":
        raise pydantic.ValidationError.from_exception_data(
            title="invalid data",
            line_errors=[
                {
                    "type": "value_error",
                    "loc": ("some", "field"),
                    "input": {"some": {"field": 42}},
                    "ctx": {"error": "42 is not allowed"},
                }
            ],
        )
    if error == "runtimeerror":
        raise RuntimeError("oups")
    if error == "exit":
        context.exit(1)


@pytest.mark.parametrize("debug", [True, False])
def test_command_error(
    runner: CliRunner, caplog: pytest.LogCaptureFixture, debug: bool
) -> None:
    obj = util.Obj(debug=debug)
    with caplog.at_level(logging.DEBUG, logger="pglift_cli"):
        result = runner.invoke(mycmd, ["error"], obj=obj)
    assert result.exit_code == 1
    assert (
        result.stderr
        == "Error: Command '['bad', 'cmd']' returned non-zero exit status 1.\nerrs\noutput\n"
    )
    if debug:
        (error_record,) = caplog.records
        assert error_record.exc_text and error_record.exc_text.startswith(
            "Traceback (most recent call last):"
        )
    else:
        (logging_start_record, error_record) = caplog.records
        assert logging_start_record.msg == "debug logging at %s"
        assert logging_start_record.args is not None
        (debuglogfile,) = logging_start_record.args
        assert isinstance(debuglogfile, Path)
        assert error_record.exc_text is None
        assert not debuglogfile.exists()
    assert error_record.message == "an internal error occurred"


def test_command_cancelled(runner: CliRunner, caplog: pytest.LogCaptureFixture) -> None:
    obj = util.Obj()
    with caplog.at_level(logging.DEBUG, logger="pglift_cli"):
        result = runner.invoke(mycmd, ["cancel"], obj=obj)
    logging_start_record = caplog.records[0]
    assert logging_start_record.msg == "debug logging at %s"
    assert logging_start_record.args is not None
    (debuglogfile,) = logging_start_record.args
    assert isinstance(debuglogfile, Path)
    assert result.exit_code == 1
    assert result.stderr == "Aborted!\n"
    assert not debuglogfile.exists()


@pytest.mark.parametrize("output_format", [None, "json"])
def test_command_validationerror(
    runner: CliRunner,
    caplog: pytest.LogCaptureFixture,
    output_format: Literal["json"] | None,
) -> None:
    opts = []
    if output_format == "json":
        opts += ["-o", "json"]
    obj = util.Obj()
    with caplog.at_level(logging.DEBUG, logger="pglift_cli"):
        result = runner.invoke(mycmd, ["validationerror"] + opts, obj=obj)
    logging_start_record = caplog.records[0]
    assert logging_start_record.msg == "debug logging at %s"
    assert logging_start_record.args is not None
    (debuglogfile,) = logging_start_record.args
    assert isinstance(debuglogfile, Path)
    assert result.exit_code == 1
    if output_format == "json":
        assert json.loads(result.stdout) == [
            {
                "type": "value_error",
                "loc": ["some", "field"],
                "msg": "Value error, 42 is not allowed",
                "input": {"some": {"field": 42}},
            }
        ]
    pydantic_version = ".".join(pydantic.__version__.split(".", 2)[:2])
    pydantic_error_url = f"https://errors.pydantic.dev/{pydantic_version}/v/value_error"
    assert result.stderr == "\n".join(
        [
            "Error: 1 validation error for invalid data",
            "some.field",
            "  Value error, 42 is not allowed [type=value_error, input_value={'some': {'field': 42}}, input_type=dict]",
            f"    For further information visit {pydantic_error_url}",
            "",
        ]
    )
    assert not debuglogfile.exists()


def test_command_exit(runner: CliRunner, caplog: pytest.LogCaptureFixture) -> None:
    obj = util.Obj()
    with caplog.at_level(logging.DEBUG, logger="pglift_cli"):
        result = runner.invoke(mycmd, ["exit"], obj=obj)
    logging_start_record = caplog.records[0]
    assert logging_start_record.msg == "debug logging at %s"
    assert logging_start_record.args is not None
    (debuglogfile,) = logging_start_record.args
    assert isinstance(debuglogfile, Path)
    assert result.exit_code == 1
    assert not result.stdout
    assert not debuglogfile.exists()


@pytest.mark.parametrize("debug", [True, False])
def test_command_internal_error(
    runner: CliRunner, caplog: pytest.LogCaptureFixture, debug: bool
) -> None:
    """In case of internal error, either it is logged (with a traceback) in the
    debug file or it propagates (and gets shown in stderr), and click raises SystemExit.
    """
    obj = util.Obj(debug=debug)
    with caplog.at_level(logging.DEBUG, logger="pglift_cli"):
        result = runner.invoke(mycmd, ["runtimeerror"], obj=obj)
    assert result.exit_code == 1
    assert result.exc_info is not None
    if debug:
        assert not caplog.records
        exc_type, exc_value, traceback = result.exc_info
        assert exc_type is RuntimeError and str(exc_value) == "oups"
        assert traceback is not None
    else:
        assert isinstance(result.exception, SystemExit) and result.exception.code == 1
        logging_start_record, error_record = [
            r for r in caplog.records if r.name == "pglift_cli"
        ]
        assert logging_start_record.msg == "debug logging at %s"
        assert logging_start_record.args is not None
        (debuglogfile,) = logging_start_record.args
        assert isinstance(debuglogfile, Path)
        assert debuglogfile.exists()
        logcontent = debuglogfile.read_text()
        assert "an unexpected error occurred" in logcontent
        assert "Traceback (most recent call last):" in logcontent
        assert "RuntimeError: oups" in logcontent
        debuglogrecord = next(r for r in caplog.records if r.name == "pglift_cli_debug")
        assert debuglogrecord.msg == "an unexpected error occurred"
        assert (
            debuglogrecord.exc_text is not None
            and debuglogrecord.exc_text.startswith("Traceback (most recent call last):")
        )


@click.command("testasync", cls=util.Command)
@click.argument("arg")
@util.async_command
async def asynccmd(arg: str) -> None:
    click.echo(f"called async with {arg}")


def test_asynccommand(runner: CliRunner) -> None:
    obj = util.Obj()
    result = runner.invoke(asynccmd, ["value"], obj=obj)
    assert result.exit_code == 0
    assert result.output == "called async with value\n"


def test_get_instance(
    settings: Settings, pg_version: PostgreSQLVersion, instance: system.Instance
) -> None:
    assert util.get_instance(instance.name, pg_version, settings) == instance

    assert util.get_instance(instance.name, None, instance._settings) == instance

    with pytest.raises(click.BadParameter):
        util.get_instance("notfound", None, settings)

    with pytest.raises(click.BadParameter):
        util.get_instance("notfound", pg_version, settings)

    with patch.object(
        system.PostgreSQLInstance, "system_lookup", autospec=True
    ) as system_lookup:
        with pytest.raises(
            click.BadParameter,
            match="instance 'foo' exists in several PostgreSQL version",
        ):
            util.get_instance("foo", None, settings)
    assert [call.args for call in system_lookup.call_args_list] == [
        ("foo", "14", settings),
        ("foo", "17", settings),
    ]
