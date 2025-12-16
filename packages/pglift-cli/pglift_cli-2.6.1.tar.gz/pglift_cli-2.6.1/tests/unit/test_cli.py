# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import click
import pytest
import yaml
from click.shell_completion import ShellComplete
from click.testing import CliRunner
from pgtoolkit.hba import HBARecord
from pgtoolkit.hba import parse as parse_hba
from rich.console import ConsoleDimensions

from pglift import instances, postgresql
from pglift.models import Instance, PostgreSQLInstance, interface, system
from pglift.settings import Settings as BaseSettings
from pglift.system import cmd
from pglift.types import Status
from pglift_cli import _site, patroni, postgres, prometheus
from pglift_cli._settings import Settings
from pglift_cli.main import cli
from pglift_cli.main import console as cli_console
from pglift_cli.util import (
    Command,
    Group,
    Obj,
    instance_identifier,
    instance_identifier_option,
    pass_instance,
    pass_postgresql_instance,
    postgresql_instance_identifier,
)

from . import click_result_traceback

instance_arg_guessed_or_given = pytest.mark.parametrize(
    "args", [[], ["test"]], ids=["instance:guessed", "instance:given"]
)


@pytest.fixture(autouse=True)
def _no_command_runners() -> Iterator[None]:
    with patch.object(
        cmd,
        "run",
        side_effect=lambda *args, **kwargs: pytest.fail(
            "unexpected call to command runner"
        ),
    ):
        yield None


@pytest.fixture
def settings(settings: BaseSettings) -> Settings:
    return Settings.model_validate(
        settings.model_dump()
        | {
            "cli": {
                "log_format": "%(levelname)-4s %(message)s",
            }
        }
    )


@pytest.fixture
def site_settings(settings: Settings, tmp_path: Path) -> Iterator[Settings]:
    """Make _site.SETTINGS filled with the value of 'settings' fixture."""
    sf = tmp_path / "settings.yaml"
    sf.write_text(yaml.dump(settings.model_dump(mode="json")))
    _site.clear_caches()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(_site.SiteSettings, "yaml_file", sf)
        yield _site.SETTINGS
    _site.clear_caches()


@pytest.fixture
def installed(site_settings: Settings) -> Iterator[None]:
    with patch(
        "pglift.system.install.check", return_value=True, autospec=True
    ) as check:
        yield None
    check.assert_called_once_with(site_settings)


@pytest.fixture
def obj() -> Obj:
    return Obj()


@pytest.fixture
def instance(instance: system.Instance, site_settings: Settings) -> system.Instance:
    """The system Instance value as returned by instance_lookup(); built from
    upper conftest.py but bound to _site.SETTINGS.
    """
    object.__setattr__(instance, "_settings", site_settings)
    return instance


@pytest.fixture
def pg_instance(
    pg_instance: system.PostgreSQLInstance, site_settings: Settings
) -> system.PostgreSQLInstance:
    """The system PostgreSQLInstance value as returned by instance_lookup(); built from
    upper conftest.py but bound to _site.SETTINGS.
    """
    object.__setattr__(pg_instance, "_settings", site_settings)
    return pg_instance


@contextmanager
def set_console_width(width: int) -> Iterator[None]:
    old_size = cli_console.size
    cli_console.size = ConsoleDimensions(width, old_size.height)
    try:
        yield
    finally:
        cli_console.size = ConsoleDimensions(old_size.width, old_size.height)


def test_instance_identifier(runner: CliRunner, obj: Obj, instance: Instance) -> None:
    @click.command(cls=Command)
    @postgresql_instance_identifier(nargs=1)
    def one(instance: system.PostgreSQLInstance) -> None:
        """One"""
        assert type(instance) is system.PostgreSQLInstance
        click.echo(instance, nl=False)

    @click.command(cls=Command)
    @instance_identifier(nargs=-1)
    def many(instance: tuple[system.Instance]) -> None:
        """Many"""
        click.echo(", ".join(str(i) for i in instance), nl=False)

    @click.command(cls=Command)
    @instance_identifier(nargs=1, required=True)
    def one_required(instance: system.Instance) -> None:
        """One INSTANCE required"""
        assert type(instance) is system.Instance
        click.echo("instance is REQUIRED", nl=False)

    result = runner.invoke(one, [], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == str(instance)

    result = runner.invoke(many, [], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == str(instance)

    result = runner.invoke(one, [str(instance)], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == str(instance)

    result = runner.invoke(many, [str(instance), instance.name], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == f"{instance}, {instance}"

    result = runner.invoke(one_required, [], obj=obj)
    assert result.exit_code == 2
    assert "Missing argument 'INSTANCE'." in result.stderr

    result = runner.invoke(one_required, [instance.name], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == "instance is REQUIRED"


def test_instance_identifier_all_instances(
    runner: CliRunner, obj: Obj, instance: Instance, instance2: Instance
) -> None:
    @click.command(cls=Command)
    @instance_identifier(nargs=-1)
    @click.option("--all", "_all_instances", is_flag=True)
    def all(instance: tuple[system.Instance], _all_instances: bool) -> None:
        """All"""
        click.echo(", ".join(str(i) for i in instance), nl=False)

    result = runner.invoke(all, [str(instance)], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == str(instance)

    result = runner.invoke(all, [str(instance), instance2.name], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == f"{instance}, {instance2}"

    result = runner.invoke(all, ["--all"], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert result.stdout == f"{instance}, {instance2}"


@pytest.fixture
def cli_app() -> click.Group:
    @click.group
    @instance_identifier_option
    def app(**kwargs: Any) -> None:
        assert kwargs.pop("instance") is None
        assert not kwargs

    @app.command
    @pass_instance
    def cmd(instance: system.Instance) -> None:
        print(f"cmd on {instance.qualname!r}")

    @app.command
    @pass_postgresql_instance
    def pgcmd(instance: system.PostgreSQLInstance) -> None:
        print(f"pgcmd on {instance.qualname!r}")

    return app


@pytest.mark.parametrize("command", ["cmd", "pgcmd"])
@pytest.mark.usefixtures("site_settings")
def test_instance_identifier_option_missing(
    runner: CliRunner, obj: Obj, cli_app: click.Group, command: str
) -> None:
    result = runner.invoke(cli_app, [command], obj=obj)
    assert result.exit_code == 2
    assert "Error: no instance found; create one first." in result.stderr


@pytest.mark.parametrize("command", ["cmd", "pgcmd"])
def test_instance_identifier_option_implicit(
    runner: CliRunner,
    obj: Obj,
    instance: Instance,
    cli_app: click.Group,
    pg_version: str,
    command: str,
) -> None:
    result = runner.invoke(cli_app, [command], obj=obj)
    assert result.exit_code == 0
    assert result.stdout == f"{command} on '{pg_version}-{instance.name}'\n"


@pytest.mark.parametrize("command", ["cmd", "pgcmd"])
@pytest.mark.usefixtures("instance", "instance2")
def test_instance_identifier_option_ambiguous(
    runner: CliRunner, obj: Obj, cli_app: click.Group, command: str
) -> None:
    result = runner.invoke(cli_app, [command], obj=obj)
    assert result.exit_code == 2
    assert (
        "Error: several instances found; option '-i' / '--instance' is required."
        in result.stderr
    )


def test_command_as_root(runner: CliRunner, obj: Obj) -> None:
    @click.group(cls=Group)
    def app(**kwargs: Any) -> None:
        pass

    @app.command
    def cmd(instance: system.Instance) -> None:
        """Something for testing."""

    with patch("pglift_cli.util.is_root", autospec=True, return_value=True) as is_root:
        result = runner.invoke(app, ["cmd"], obj=obj)
    is_root.assert_called_once()
    assert result.exit_code == 1
    assert "Error: pglift cannot be used as root" in result.stderr

    # Invocation with --help is allowed though.
    with patch("pglift_cli.util.is_root", autospec=True, return_value=True) as is_root:
        result = runner.invoke(app, ["cmd", "myinstance", "--help"], obj=obj)
    assert not is_root.called
    assert result.exit_code == 0
    assert "Something for testing." in result.stdout


@pytest.mark.usefixtures("site_settings")
def test_instance_commands_completion(obj: Obj) -> None:
    from pglift_cli import instance as instance_cli

    group = instance_cli.cli
    assert group.name
    comp = ShellComplete(group, {"obj": obj}, group.name, "_CLICK_COMPLETE")
    commands = [c.value for c in comp.get_completions([], "")]
    assert commands == [
        "alter",
        "backup",
        "backups",
        "create",
        "demote",
        "drop",
        "env",
        "exec",
        "get",
        "list",
        "logs",
        "privileges",
        "promote",
        "reload",
        "restart",
        "restore",
        "shell",
        "start",
        "status",
        "stop",
        "upgrade",
    ]


@pytest.mark.usefixtures("site_settings")
def test_site_settings_yaml(runner: CliRunner, settings: Settings, obj: Obj) -> None:
    s = settings.model_dump(mode="json")
    assert s["powa"]
    with set_console_width(500):
        result = runner.invoke(cli, ["site-settings"], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert yaml.safe_load(result.output) == s


@pytest.mark.usefixtures("site_settings")
def test_site_settings_json(runner: CliRunner, settings: Settings, obj: Obj) -> None:
    s = settings.model_dump(mode="json")
    result = runner.invoke(cli, ["site-settings", "-o", "json"], obj=obj)
    assert result.exit_code == 0, result.stderr
    assert json.loads(result.output) == s


@pytest.mark.usefixtures("site_settings")
def test_site_settings_defaults(runner: CliRunner, obj: Obj) -> None:
    """site-settings --defaults returns default settings, not accounting for
    settings.yaml or env vars.
    """
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_PREFIX", "/srv/pglift")
        result = runner.invoke(
            cli, ["site-settings", "-o", "json", "--defaults"], obj=obj
        )
        assert result.exit_code == 0, result.stderr
    defaults_s = json.loads(result.output)
    assert defaults_s["prefix"] != "/srv/pglift"
    assert defaults_s["powa"] is None


@pytest.mark.usefixtures("site_settings")
def test_site_settings_no_defaults(
    runner: CliRunner,
    settings: Settings,
    obj: Obj,
) -> None:
    s = settings.model_dump(mode="json")
    assert s["powa"] is not None
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PGLIFT_PREFIX", "/srv/pglift")
        result = runner.invoke(
            cli, ["site-settings", "-o", "json", "--no-defaults"], obj=obj
        )
        assert result.exit_code == 0, result.stderr
    no_defaults_s = json.loads(result.output)
    # lock_file is not explicitly defined, but is computed from environment
    assert no_defaults_s["cli"]["lock_file"] == s["cli"]["lock_file"]
    # powa is defined explicitly (empty)
    assert no_defaults_s["powa"] != s["powa"]
    # systemd contains values computed from environment (unit_path) and some
    # not explicitly defined (sudo)
    assert "sudo" not in no_defaults_s["systemd"] and "sudo" in s["systemd"]
    assert no_defaults_s["systemd"]["unit_path"] == s["systemd"]["unit_path"]


@pytest.mark.usefixtures("site_settings")
def test_site_settings_schema(runner: CliRunner, settings: Settings, obj: Obj) -> None:
    result = runner.invoke(cli, ["site-settings", "--schema", "-o", "json"], obj=obj)
    assert result.exit_code == 0, result.stderr
    schema = json.loads(result.output)
    schema.pop("title")
    expected = settings.model_json_schema()
    expected.pop("title")
    assert schema == expected


@pytest.mark.parametrize(
    "args, command, objtype",
    [
        ("instance --ansible-argspec", cli, "Instance"),
        ("role --ansible-argspec", cli, "Role"),
        ("database --ansible-argspec", cli, "Database"),
        ("--ansible-argspec", prometheus.cli, "PostgresExporter"),
    ],
)
@pytest.mark.usefixtures("site_settings")
def test_argspec(
    runner: CliRunner,
    obj: Obj,
    args: str,
    command: click.Command,
    objtype: str,
) -> None:
    with patch(
        "pglift_cli.util.helpers.argspec_from_model", return_value={"type": objtype}
    ) as mocked:
        result = runner.invoke(command, args.split(), obj=obj)
    (call,) = mocked.call_args_list
    (arg,) = call.args
    assert arg.__name__ == objtype
    data = json.loads(result.stdout)
    assert data == {"type": objtype}


@pytest.mark.usefixtures("site_settings")
def test_instance_schema(runner: CliRunner, obj: Obj) -> None:
    result = runner.invoke(cli, ["instance", "--schema"], obj=obj)
    schema = json.loads(result.output)
    assert schema["title"] == "Instance"
    assert (
        schema["description"].splitlines()[0]
        == "A pglift instance, on top of a PostgreSQL instance."
    )
    assert schema["required"] == ["name"]


@pytest.mark.usefixtures("installed")
def test_instance_shell_var_missing(
    runner: CliRunner, instance: Instance, obj: Obj, monkeypatch: pytest.MonkeyPatch
) -> None:
    with patch("os.execle", autospec=True) as execle:
        monkeypatch.delenv("SHELL", raising=False)
        r = runner.invoke(
            cli,
            ["instance", "shell", instance.name],
            obj=obj,
        )
    assert not execle.called
    assert r.exit_code == 2
    assert (
        "Error: SHELL environment variable not found; try to use --shell option"
        in r.stderr
    )


@pytest.mark.usefixtures("installed")
def test_instance_shell(
    runner: CliRunner, instance: Instance, obj: Obj, monkeypatch: pytest.MonkeyPatch
) -> None:
    with patch("os.execle", autospec=True) as execle:
        monkeypatch.setenv("SHELL", "fooshell")
        runner.invoke(
            cli,
            ["instance", "shell", instance.name],
            obj=obj,
        )
    path, arg, env = execle.call_args.args
    assert path == arg == "fooshell"
    assert env["PGHOST"] == "/socks"


@pytest.mark.usefixtures("installed")
def test_pgconf_edit(
    runner: CliRunner,
    obj: Obj,
    pg_version: str,
    pg_instance: Instance,
    instance: Instance,
    postgresql_conf: str,
) -> None:
    manifest = interface.Instance(
        name="test",
        version=pg_version,
        settings={
            "unix_socket_directories": "/socks",
            "cluster_name": "unittests",
        },
    )
    with (
        patch("click.edit", return_value="bonjour = bonsoir\n", autospec=True) as edit,
        patch.object(
            postgresql, "status", return_value=Status.running, autospec=True
        ) as status,
        patch.object(instances, "_get", return_value=manifest, autospec=True) as _get,
        patch.object(
            instances,
            "configure",
            return_value=instances.ConfigureResult(
                changes={"bonjour": ("on", "'matin")}
            ),
            new_callable=AsyncMock,
        ) as configure,
    ):
        result = runner.invoke(
            cli,
            ["pgconf", f"--instance={instance}", "edit"],
            obj=obj,
        )
    assert result.exit_code == 0, result.stderr
    status.assert_awaited_once_with(pg_instance)
    _get.assert_awaited_once_with(instance, Status.running, port_from_config=True)
    edit.assert_called_once_with(text=postgresql_conf)
    assert manifest.settings == {"bonjour": "bonsoir"}
    configure.assert_awaited_once_with(pg_instance, manifest, _is_running=True)
    assert result.stderr == "bonjour: on -> 'matin\n"


@pytest.mark.usefixtures("installed")
def test_pghba_edit(runner: CliRunner, obj: Obj, instance: Instance) -> None:
    hba_r = HBARecord(
        conntype="local", user="santaclaus", database="list", method="md5"
    )
    hba_f = postgresql.hba_path(instance.postgresql)
    assert hba_r not in parse_hba(hba_f)
    with (
        patch("click.edit", return_value=str(hba_r), autospec=True),
        # Unfortunately we patch postgresql.is_running(), because we can't
        # inject a custom (fake) instance manager here. Indeed pytest and the
        # pglift CLI do not share the same event loop. Since the instance
        # manager is passed via a ContextVar, and ContextVars are local to their
        # event loop, it is not accessible across that "boundary".
        patch.object(postgresql, "is_running", return_value=False),
    ):
        result = runner.invoke(
            cli,
            ["pghba", f"--instance={instance}", "edit"],
            obj=obj,
        )
        assert result.exit_code == 0, result.stderr
    assert hba_r in parse_hba(hba_f)


@pytest.mark.usefixtures("installed")
def test_pgconf_edit_no_change(
    runner: CliRunner, obj: Obj, instance: Instance, postgresql_conf: str
) -> None:
    with (
        patch("click.edit", return_value=None, autospec=True) as edit,
        patch.object(postgresql, "status", autospec=True) as status,
        patch.object(instances, "_get", autospec=True) as _get,
        patch.object(instances, "configure", new_callable=AsyncMock) as configure,
    ):
        result = runner.invoke(
            cli, ["pgconf", f"--instance={instance}", "edit"], obj=obj
        )
    edit.assert_called_once_with(text=postgresql_conf)
    status.assert_not_awaited()
    _get.assert_not_awaited()
    configure.assert_not_awaited()
    assert result.stderr == "no change\n"


@pytest.mark.usefixtures("site_settings")
def test_role_schema(runner: CliRunner, obj: Obj) -> None:
    result = runner.invoke(cli, ["role", "--schema"], obj=obj)
    schema = json.loads(result.output)
    assert schema["title"] == "Role"
    assert schema["description"] == "PostgreSQL role"
    assert schema["required"] == ["name"]


@pytest.mark.usefixtures("site_settings")
def test_database_schema(runner: CliRunner, obj: Obj) -> None:
    result = runner.invoke(cli, ["database", "--schema"], obj=obj)
    schema = json.loads(result.output)
    assert schema["title"] == "Database"
    assert schema["description"] == "PostgreSQL database"


def test_postgres(runner: CliRunner, pg_instance: PostgreSQLInstance, obj: Obj) -> None:
    result = runner.invoke(postgres.cli, ["no-suchinstance"], obj=obj)
    assert result.exit_code == 2
    assert (
        "Invalid value for 'INSTANCE': instance 'no/suchinstance' not found: 'no' is not a valid"
        in result.stderr
    )

    result = runner.invoke(postgres.cli, [pg_instance.name], obj=obj)
    assert result.exit_code == 2
    assert (
        "Invalid value for 'INSTANCE': invalid qualified name 'test'" in result.stderr
    )

    with patch("pglift_cli.postgres.cmd.execute_program", autospec=True) as p:
        result = runner.invoke(
            postgres.cli, [f"{pg_instance.version}-{pg_instance.name}"], obj=obj
        )
    assert result.exit_code == 0
    p.assert_called_once_with(
        [
            str(postgresql.bindir(pg_instance) / "postgres"),
            "-D",
            str(pg_instance.datadir),
        ]
    )


def test_postgres_exporter_schema(runner: CliRunner, obj: Obj) -> None:
    result = runner.invoke(prometheus.cli, ["--schema"], obj=obj)
    schema = json.loads(result.output)
    assert schema["title"] == "PostgresExporter"
    assert schema["description"] == "Prometheus postgres_exporter service."


@pytest.mark.usefixtures("installed")
def test_patroni_logs(
    runner: CliRunner, obj: Obj, settings: Settings, instance: system.Instance
) -> None:
    with patch(
        "pglift.patroni.impl.logs", return_value=["l1\n", "l2\n"], autospec=True
    ) as logs:
        result = runner.invoke(patroni.cli, ["-i", str(instance), "logs"], obj=obj)
    assert result.exit_code == 0, click_result_traceback(result)
    logs.assert_called_once_with(instance.qualname, settings.patroni)
    assert result.output == "l1\nl2\n"
