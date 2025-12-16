# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from pglift import exceptions
from pglift_cli._settings import CLISettings
from pglift_cli.util import audit


def test_audit(tmp_path: Path) -> None:
    with audit(["test", "no", "audit"], CLISettings(audit=None)):
        logging.getLogger("pglift").error("not logged")

    audit_logpath = tmp_path / "audit.log"
    settings = CLISettings.model_validate(
        {
            "audit": {
                "path": audit_logpath,
                "log_format": "%(levelname)s:%(name)s %(message)s",
            }
        }
    )
    audit_logpath.touch()
    with audit_logpath.open() as logf:
        with pytest.raises(RuntimeError):
            with audit(["test", "error"], settings):
                logging.getLogger("pglift").error("oups")
                raise RuntimeError("err")
        assert logf.read().splitlines() == [
            "INFO:pglift_cli.audit command: test error",
            "ERROR:pglift oups",
            "ERROR:pglift_cli.audit command failed (0 seconds)",
        ]

        with audit(["test", "ok"], settings, dry_run=True):
            logging.getLogger("pglift").debug("running")
        assert logf.read().splitlines() == [
            "INFO:pglift_cli.audit command: test ok (DRY RUN)",
            "DEBUG:pglift running",
            "INFO:pglift_cli.audit command completed (0 seconds)",
        ]

        with pytest.raises(exceptions.Cancelled):
            with audit(["test", "cancel"], settings, dry_run=False):
                logging.getLogger("pglift").info("trying")
                raise exceptions.Cancelled("forget about it")
        assert logf.read().splitlines() == [
            "INFO:pglift_cli.audit command: test cancel",
            "INFO:pglift trying",
            "WARNING:pglift_cli.audit command cancelled (0 seconds)",
        ]
