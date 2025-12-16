# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

import click

from pglift import patroni
from pglift.models import Instance
from pglift.patroni import impl
from pglift.patroni import register_if as register_if

from . import _site, hookimpl
from .util import Group, instance_identifier_option, pass_instance


@click.group("patroni", cls=Group)
@instance_identifier_option
def cli(**kwargs: Any) -> None:
    """Handle Patroni service for an instance."""


@cli.command("logs")
@pass_instance
def logs(instance: Instance) -> None:
    """Output Patroni logs."""
    settings = patroni.get_settings(_site.SETTINGS)
    for line in impl.logs(instance.qualname, settings):
        click.echo(line, nl=False)


@hookimpl
def command() -> click.Group:
    return cli
