# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator

import pytest
from click.testing import CliRunner

from pglift_cli import _site

pytest_plugins = [
    "pglift.fixtures",
    "pglift.fixtures.unit",
]


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def cache_clear() -> Iterator[None]:
    _site._settings.cache_clear()
    yield None
    _site._settings.cache_clear()
