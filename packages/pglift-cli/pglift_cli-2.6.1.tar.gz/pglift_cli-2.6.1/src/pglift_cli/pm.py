# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pglift.pm import PluginManager as BasePluginManager

from . import __name__ as pkgname


class PluginManager(BasePluginManager):
    ns = pkgname
    modules = (
        "patroni",
        "pgbackrest",
        "pgbackrest.repo_path",
        "prometheus",
    )
