#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Sync reports.
"""
import shutil
import zipfile

import parzzley.builtin.log_formatters.json


class SyncReport(parzzley.sync.aspect.Aspect):
    """
    Writes a report after each sync run for later problem diagnostics or performance analysis.
    """

    _DATA__REPORT_DONE = parzzley.sync.aspect.events.Data(False)

    @parzzley.sync.aspect.event_handler()
    async def write_report(self, event: parzzley.sync.aspect.events.sync_run.Close):
        """
        Write the report.
        """
        if SyncReport._DATA__REPORT_DONE.get(event):
            return
        SyncReport._DATA__REPORT_DONE.set(event, True)

        report = parzzley.builtin.log_formatters.json.Formatter().format(event.sync_run, event.all_log_entries)
        str(report)

        volume_reports_dir = event.sync_run.manager_var_dir / "reports" / event.sync_run.volume_name
        volume_reports_dir.mkdir(exist_ok=True, parents=True)

        for old_working_file in volume_reports_dir.glob("~*"):
            old_working_file.unlink()

        report_file_i = 0
        last_report_file = None
        next_report_file = None
        while not next_report_file or next_report_file.exists():
            last_report_file = next_report_file
            report_file_name = f"{str(report_file_i).rjust(8, "0")}.zip"
            next_report_file = volume_reports_dir / report_file_name
            report_file_i += 1

        report_file = last_report_file or next_report_file

        if report_file.exists():

            if report_file.stat().st_size > 200 * 1024**2:
                report_file = next_report_file
            else:
                with zipfile.ZipFile(report_file, "r") as last_report_zip:
                    if len(last_report_zip.namelist()) >= 10_000:
                        report_file = next_report_file

        report_file_working = report_file.parent / f"~{report_file.name}"

        if report_file.exists():
            shutil.copyfile(report_file, report_file_working)

        with zipfile.ZipFile(report_file_working, "a", zipfile.ZIP_LZMA) as report_zip:
            report_zip.writestr(f"#{event.sync_run.sn}", report)

        report_file_working.rename(report_file)
