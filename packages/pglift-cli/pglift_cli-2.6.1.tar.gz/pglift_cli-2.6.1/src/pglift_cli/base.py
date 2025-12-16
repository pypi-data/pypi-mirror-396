# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib

import click

from pglift import hooks

from . import __name__ as pkgname
from . import _site
from . import hookspecs as h


class CLIGroup(click.Group):
    """Group gathering main commands (defined here), commands from submodules
    and commands from plugins.
    """

    submodules = [
        "instance",
        "pgconf",
        "role",
        "database",
        "postgres",
        "pghba",
        "wal",
    ]

    @classmethod
    def submodule_command(cls, name: str) -> click.Command:
        """Load the main command (cli() function) from a submodule."""
        mod = importlib.import_module(f".{name}", package=pkgname)
        command = mod.cli
        assert isinstance(command, click.Command), command
        return command

    def list_commands(self, context: click.Context) -> list[str]:
        main_commands = super().list_commands(context)
        plugins_commands: list[str] = sorted(
            g.name  # type: ignore[misc]
            for g in hooks(_site.PLUGIN_MANAGER, h.command)
        )
        return main_commands + self.submodules + plugins_commands

    def get_command(self, context: click.Context, name: str) -> click.Command | None:
        main_command = super().get_command(context, name)
        if main_command is not None:
            return main_command
        if name in self.submodules:
            return self.submodule_command(name)
        for group in hooks(_site.PLUGIN_MANAGER, h.command):
            assert isinstance(group, click.Command)
            if group.name == name:
                return group
        return None
