# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import traceback

from click.testing import Result


def click_result_traceback(result: Result) -> str:
    assert result.exc_info
    exc_type, exc, tb = result.exc_info
    return "".join(traceback.format_exception(exc_type, exc, tb))
