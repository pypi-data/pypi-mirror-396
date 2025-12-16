# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import click
import pluggy

from . import __name__ as pkgname

hookspec = pluggy.HookspecMarker(pkgname)


@hookspec
def command() -> click.Command:
    """Return command-line entry point as click Command (or Group) for the plugin."""
    raise NotImplementedError


@hookspec
def add_instance_commands(group: click.Group) -> None:
    """Extend instance commands 'group' with extra commands from the plugin."""
    raise NotImplementedError
