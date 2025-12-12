#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Out`.
"""
import subprocess

import parzzley.sync.logger


@parzzley.sync.logger.register_out
class Out(parzzley.sync.logger.Out):
    """
    Shell logger output channel.
    """

    def __init__(self, *, cmdline: str):
        self.__cmdline = cmdline

    def emit_text(self, sync_run, s):
        with subprocess.Popen(["sh", "-c", self.__cmdline], stdin=subprocess.PIPE, start_new_session=True) as p:
            p.communicate(s.encode())
            if p.returncode:
                raise RuntimeError(f"the command line {self.__cmdline!r} returned with exit code {p.returncode}")
