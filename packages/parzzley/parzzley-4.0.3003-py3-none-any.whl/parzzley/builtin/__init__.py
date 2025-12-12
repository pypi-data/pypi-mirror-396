#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Builtin implementations of some interfaces.
"""
import parzzley.sync


def load_builtin_implementations():
    """
    Load all builtin implementations.

    Do not use it directly. It is already called implicitly.
    """
    # pylint: disable=import-outside-toplevel
    import parzzley.builtin.aspects as _aspect_implementations
    import parzzley.builtin.fs as _fs_implementations
    import parzzley.builtin.log_formatters as _log_formatters_implementations
    import parzzley.builtin.log_outs as _log_outs_implementations

    parzzley.sync.load_implementations_from_package(_aspect_implementations.__name__)
    parzzley.sync.load_implementations_from_package(_fs_implementations.__name__)
    parzzley.sync.load_implementations_from_package(_log_formatters_implementations.__name__)
    parzzley.sync.load_implementations_from_package(_log_outs_implementations.__name__)
