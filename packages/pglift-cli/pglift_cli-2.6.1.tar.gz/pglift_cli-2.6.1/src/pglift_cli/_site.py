# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Site globals for the CLI.

Module attributes are accessed lazily through a custom __getattr__() function
which delegates to (cached) getter functions.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import cache
from typing import Any

import click
import pydantic

from pglift import exceptions, plugin_manager
from pglift.models import interface

from . import hookspecs
from ._settings import Settings
from ._settings import SiteSettings as SiteSettings
from .pm import PluginManager


@cache
def _settings() -> Settings:
    try:
        return SiteSettings()
    except (exceptions.SettingsError, pydantic.ValidationError) as e:
        raise click.ClickException(f"invalid site settings\n{e}") from e


_default_settings = cache(Settings)


@cache
def _plugin_manager() -> PluginManager:
    return PluginManager.get(_settings(), hookspecs)


@cache
def _instance_model() -> type[interface.Instance]:
    pm = plugin_manager(_settings())
    return interface.Instance.composite(pm)


@cache
def _role_model() -> type[interface.Role]:
    pm = plugin_manager(_settings())
    return interface.Role.composite(pm)


objs: dict[str, Callable[[], Any]] = {
    "SETTINGS": _settings,
    "DEFAULT_SETTINGS": _default_settings,
    "PLUGIN_MANAGER": _plugin_manager,
    "INSTANCE_MODEL": _instance_model,
    "ROLE_MODEL": _role_model,
}
__all__ = list(objs) + ["clear_caches"]


def __dir__() -> list[str]:
    return __all__[:]


def __getattr__(name: str) -> Any:
    try:
        getter = objs[name]
    except KeyError as e:
        raise AttributeError(name) from e
    return getter()


def clear_caches(key: str | None = None) -> None:
    """Test helper to clear getters cache."""
    if key is not None:
        objs[key].cache_clear()  # type: ignore[attr-defined]
    else:
        for fn in objs.values():
            fn.cache_clear()  # type: ignore[attr-defined]
