# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import re

import click
import pytest
from click.testing import CliRunner

from pglift import ui
from pglift_cli import main
from pglift_cli.util import Obj


@pytest.fixture
def obj() -> Obj:
    return Obj()


def test_cli(runner: CliRunner, obj: Obj) -> None:
    # invoke the CLI with no option, sanity check
    result = runner.invoke(main.cli, obj=obj)
    assert result.exit_code == 2
    assert result.stderr.splitlines()[0] == "Usage: cli [OPTIONS] COMMAND [ARGS]..."


def test_non_interactive(runner: CliRunner) -> None:
    @main.cli.command("confirmme")
    def confirm_me() -> None:
        if not ui.confirm("Confirm?", default=True):
            raise click.Abort()
        print("confirmed")

    result = runner.invoke(main.cli, ["confirmme"], input="n\n")
    assert result.exit_code == 1 and "Aborted!" in result.stderr

    result = runner.invoke(main.cli, ["--non-interactive", "confirmme"])
    assert result.exit_code == 0 and "confirmed" in result.stdout


def test_version(runner: CliRunner, obj: Obj) -> None:
    result = runner.invoke(main.cli, ["--version"], obj=obj)
    assert re.match(r"pglift version (\d\.).*", result.stdout)


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
def test_completion(runner: CliRunner, shell: str) -> None:
    result = runner.invoke(main.cli, ["--completion", shell])
    assert result.exit_code == 0, result
    assert "_pglift_completion" in result.output


@pytest.mark.usefixtures("cache_clear")
def test_log_level(runner: CliRunner, obj: Obj) -> None:
    @main.cli.command("foo")
    def foo() -> None:
        logger = logging.getLogger("pglift")
        logger.debug("debug message")
        print("something")

    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_CLI__LOG_LEVEL", "invalid")
        result = runner.invoke(main.cli, ["foo"], obj=obj)
        assert result.exit_code == 1
        assert (
            "Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'"
            in result.stderr
        )

    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_CLI__LOG_LEVEL", "debug")
        result = runner.invoke(main.cli, ["foo"])
        assert result.exit_code == 0 and "something" in result.stdout, result.stderr
        assert "debug message" in result.stderr

    with pytest.MonkeyPatch.context() as mp:
        # -L option takes precedence
        mp.setenv("PGLIFT_CLI__LOG_LEVEL", "debug")
        result = runner.invoke(main.cli, ["-Linfo", "foo"], obj=obj)
        assert result.exit_code == 0 and "something" in result.stdout, result.stderr
        assert "debug message" not in result.stderr
