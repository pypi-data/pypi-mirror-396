# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os

import pluggy

logger = logging.getLogger(__name__)
try:
    loggers = list(os.environ["PGLIFT_LOGGERS"].split(","))
except KeyError:
    loggers = [__name__, "pglift"]
hookimpl = pluggy.HookimplMarker(__name__)
