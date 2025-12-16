# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Annotated, Any

from pydantic import BeforeValidator, Field

from pglift.settings import Settings as BaseSettings
from pglift.settings import SiteSettings as BaseSiteSettings
from pglift.settings.base import BaseModel, LogPath, RunPath
from pglift.types import LogLevel


class AuditSettings(BaseModel):
    """Settings for change operations auditing."""

    path: Annotated[
        Annotated[Path, LogPath],
        Field(description="Log file path"),
    ]
    log_format: Annotated[
        str,
        Field(description="Format for log messages"),
    ] = "%(levelname)-8s - %(asctime)s - %(name)s - %(message)s"
    date_format: Annotated[
        str,
        Field(description="Date format in log messages"),
    ] = "%Y-%m-%d %H:%M:%S"


def _upper(value: Any) -> Any:
    if isinstance(value, str):
        return value.upper()
    return value


class CLISettings(BaseModel):
    """Settings for pglift's command-line interface."""

    log_format: Annotated[
        str, Field(description="Format for log messages when written to a file")
    ] = "%(asctime)s %(levelname)-8s %(name)s - %(message)s"

    log_level: Annotated[
        LogLevel | None, Field(description="Log level"), BeforeValidator(_upper)
    ] = None

    date_format: Annotated[
        str, Field(description="Date format in log messages when written to a file")
    ] = "%Y-%m-%d %H:%M:%S"

    lock_file: Annotated[
        Path, RunPath, Field(description="Path to lock file dedicated to pglift")
    ] = Path(".pglift.lock")

    audit: Annotated[
        AuditSettings | None,
        Field(description="Settings for change operations auditing"),
    ] = None


class Settings(BaseSettings):
    cli: Annotated[CLISettings, Field(default_factory=CLISettings)]


class SiteSettings(Settings, BaseSiteSettings):
    pass
