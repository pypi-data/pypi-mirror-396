# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path

import click
import pytest

from pglift_cli import _site


@pytest.mark.usefixtures("cache_clear")
@pytest.mark.parametrize("prefix_dir", ["", "foo"])
def test_site_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, prefix_dir: str
) -> None:
    prefix = tmp_path / prefix_dir
    monkeypatch.setenv("PGLIFT_PREFIX", str(prefix))
    s = _site.SETTINGS
    assert s.prefix == prefix


@pytest.mark.usefixtures("cache_clear")
def test_settings_global(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("pglift_postgresql", json.dumps({"invalid": None}))
    with pytest.raises(click.ClickException, match="invalid site settings"):
        _ = _site.SETTINGS


@pytest.mark.usefixtures("cache_clear")
def test_yaml_site_settings_error(tmp_path: Path) -> None:
    configdir = tmp_path / "pglift"
    configdir.mkdir()
    settings_fpath = configdir / "settings.yaml"
    settings_fpath.write_text("this is not yaml")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(_site.SiteSettings, "yaml_file", settings_fpath)
        with pytest.raises(click.ClickException, match="invalid site settings"):
            _ = _site.SETTINGS
