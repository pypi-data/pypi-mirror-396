# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

import pytest

from pglift.settings import Settings
from pglift_cli import hookspecs, pm


def test_pluginmanager_all() -> None:
    p = pm.PluginManager.all(hookspecs)
    assert {name for name, _ in p.list_name_plugin()} == {
        "pglift_cli.patroni",
        "pglift_cli.pgbackrest",
        "pglift_cli.pgbackrest.repo_path",
        "pglift_cli.prometheus",
    }


def test_pluginmanager_get(settings: Settings) -> None:
    p = pm.PluginManager.get(settings, hookspecs)
    assert {name for name, _ in p.list_name_plugin()} == {
        "pglift_cli.patroni",
        "pglift_cli.pgbackrest",
        "pglift_cli.pgbackrest.repo_path",
        "pglift_cli.prometheus",
    }


@pytest.mark.parametrize(
    "update, expected",
    [
        pytest.param(
            {"prometheus": None},
            {"patroni", "pgbackrest", "pgbackrest.repo_path"},
            id="no prometheus",
        ),
        pytest.param(
            {"patroni": None},
            {"pgbackrest", "pgbackrest.repo_path", "prometheus"},
            id="no patroni",
        ),
        pytest.param(
            {"pgbackrest": None},
            {"patroni", "prometheus"},
            id="no pgbackrest",
        ),
    ],
)
def test_pluginmanager_get_unregistered(
    settings: Settings, update: dict[str, Any], expected: set[str]
) -> None:
    new_settings = Settings.model_validate(settings.model_dump() | update)
    p = pm.PluginManager.get(new_settings, hookspecs)
    assert {name for name, _ in p.list_name_plugin()} == {
        f"pglift_cli.{m}" for m in expected
    }
