#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Formatter`.
"""
import datetime
import json

import parzzley.sync.logger


@parzzley.sync.logger.register_formatter
class Formatter(parzzley.sync.logger.Formatter):
    """
    JSON log formatter.
    """

    def format(self, sync_run, entries):
        return json.dumps(
            {
                "sync_run_sn": sync_run.sn if sync_run else None,
                "volume": sync_run.volume_name if sync_run else None,
                "sites": [_.name for _ in sync_run.sites] if sync_run else None,
                "started_at": (
                    sync_run.started_at.astimezone(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S") if sync_run else None
                ),
                "entries": [
                    (_.severity.name, _.message, repr(_.item.path)[2:-1] if _.item else None, _.stream) for _ in entries
                ],
            },
            indent=1,
        )
