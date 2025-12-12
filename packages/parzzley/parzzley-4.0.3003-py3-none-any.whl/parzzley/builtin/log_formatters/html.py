#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Formatter`.
"""
import html
import typing as t

import parzzley.sync.logger
import parzzley.sync.run


@parzzley.sync.logger.register_formatter
class Formatter(parzzley.sync.logger.Formatter):
    """
    HTML log formatter.
    """

    def format(self, sync_run, entries):
        title = f"Parzzley{f" — {self.__title(sync_run)}" if sync_run else ""}"
        return (
            f"<!DOCTYPE html>\n"
            f"<html>"
            f"  <head>"
            f"    <title>{html.escape(title)}</title>"
            f"    <style>{self.__style()}</style>"
            f"  </head>"
            f"  <body>"
            f"    {self.__header(sync_run)}"
            f"    {self.__entries(entries)}"
            f"  </body>"
            f"</html>"
        )

    def __header(self, sync_run: parzzley.sync.run.SyncRun | None) -> str:
        if not sync_run:
            return ""

        return (
            f"<h1>{html.escape(self.__title(sync_run))}</h1>"
            f"<div class='aux_info'>{html.escape(sync_run.started_at.strftime("on %x at %X"))}</div>"
            f"<div class='aux_info'>{html.escape(f"with sites {", ".join(_.name for _ in sync_run.sites)}")}</div>"
        )

    def __entries(self, entries: t.Iterable[parzzley.sync.logger.Entry]) -> str:
        severity_to_class = {
            parzzley.sync.logger.Severity.DEBUG: "debug",
            parzzley.sync.logger.Severity.INFO: "info",
            parzzley.sync.logger.Severity.WARNING: "warning",
            parzzley.sync.logger.Severity.FATAL: "fatal",
        }

        table_rows = (
            (
                f"<tr>"
                f"<td class='item'>"
                f"{html.escape(f"/{entry.item.path.decode(errors="replace")}") if entry.item is not None else ""}"
                f"</td>"
                f"<td class='stream'>"
                f"{html.escape(entry.stream or "main") if entry.stream is not None else ""}"
                f"</td>"
                f"<td class='{severity_to_class[entry.severity]}'>"
                f"{html.escape(entry.message)}"
                f"</td>"
                f"</tr>"
            )
            for entry in entries
        )

        return f"<table class='report_table'>" f"    {"".join(table_rows)}" f"</table>"

    def __title(self, sync_run: parzzley.sync.run.SyncRun) -> str:
        return f"Sync Run #{sync_run.sn} for {sync_run.volume_name!r}"

    def __style(self) -> str:
        return (
            "h1, .aux_info { padding: 0; margin: 0; text-align: right; }\n"
            ".report_table { border-collapse: collapse; }\n"
            ".report_table td { border: dotted #8888; border-width: 1px 0; }\n"
            ".report_table .debug { color: #9af; }\n"
            ".report_table .info { color: #555; }\n"
            ".report_table .warning { color: #870; }\n"
            ".report_table .fatal { color: #a00; }\n"
            ".report_table .item { color: #777; font-family: monospace; white-space: pre-wrap; }\n"
            ".report_table .stream { color: #777; font-family: monospace; font-size: 0.6rem; }\n"
            ".report_table .item, .report_table .stream { padding-right: 10pt; }\n"
            "@media (prefers-color-scheme: dark) {\n"
            "    body { background: #333; color: #eee; }\n"
            "    .report_table .debug { color: #66a; }\n"
            "    .report_table .info { color: #bbb; }\n"
            "    .report_table .warning { color: #ff7; }\n"
            "    .report_table .fatal { color: #f66; }\n"
            "    .report_table .item { color: #999; }\n"
            "    .report_table .stream { color: #999; }\n"
            "}\n"
        )
