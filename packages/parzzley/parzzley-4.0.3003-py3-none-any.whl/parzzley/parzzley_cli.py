#!/usr/bin/env python3
# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
The Parzzley CLI.
"""
import argparse
import logging
import os
import signal
import sys
import typing as t

try:  # weird, but useful in some cases ;)
    if "__main__" == __name__:
        import parzzley
except ModuleNotFoundError:
    sys.path.append(os.path.abspath(os.path.realpath(__file__) + "/../.."))

import parzzley.asset
import parzzley.sync.manager
import parzzley.service


_logger = logging.getLogger("parzzley.parzzley_cli")


def main() -> None:
    """
    The CLI main routine.
    """
    _setup_logging(debug=os.environ.get("PARZZLEY_LOG_DEBUG", "") == "1")
    args = parser(only_documentation=False).parse_args().__dict__
    command_name = (args.pop("command") or "studio").replace("-", "_")
    getattr(Commands(), command_name)(**args)


# noinspection PyUnusedLocal
def parser(*, only_documentation: bool = True) -> argparse.ArgumentParser:
    """
    Return an argument parser.

    :param only_documentation: Whether to include only parameters that are relevant for documentation.
    """
    arg_parser = argparse.ArgumentParser(
        description=(
            None
            if only_documentation
            else f"Welcome to Parzzley {parzzley.asset.project_info.version}! For more information, read"
            f" {"file://"+str(parzzley.asset.data.readme_pdf("en"))!r} and visit"
            f" {parzzley.asset.project_info.homepage_url!r}."
        )
    )
    p_cmd = arg_parser.add_subparsers(help="What to do?", required=False, dest="command", metavar="[command]")

    p_cmd_sync = p_cmd.add_parser("sync", help="Execute synchronization for once for a given volume.")
    p_cmd_sync.add_argument("config_dir", type=str, help="Directory with the Parzzley sync configuration.")
    p_cmd_sync.add_argument(
        "volume_names",
        type=str,
        help="Names of the volumes to sync. If none are specified," " all volumes will be synced.",
        nargs="*",
    )

    p_cmd_sync_loop = p_cmd.add_parser(
        "sync_loop",
        help="Execute synchronization loop. Note: This should be done by a"
        " background service. Depending on how Parzzley was set up,"
        " such a service already exists and is running!",
    )
    p_cmd_sync_loop.add_argument("config_dir", type=str, help="Directory with the Parzzley sync configuration.")

    return arg_parser


class Commands:
    """
    Parzzley CLI commands.
    """

    def sync(self, config_dir: str, volume_names: t.Sequence[str], **_) -> None:
        """
        Execute sync once.

        :param config_dir: The Parzzley configuration directory.
        :param volume_names: The volumes to sync.
        """
        volume_names = tuple(volume_names) or None
        with parzzley.sync.manager.Manager.for_config_directory(config_dir) as manager:
            for volume in manager.volumes:
                if volume_names is None or volume.name in volume_names:
                    manager.run_sync(volume)

    def sync_loop(self, config_dir: str, **_) -> None:
        """
        Execute sync service loop.

        :param config_dir: The Parzzley configuration directory.
        """
        service = parzzley.service.Service(config_dir=config_dir)

        def stop_signal_handler(_sig, _frame):
            service.stop_soon()

        signal.signal(signal.SIGINT, stop_signal_handler)
        signal.signal(signal.SIGTERM, stop_signal_handler)

        service.run()


def _setup_logging(*, debug: bool = False):
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(fmt="[%(levelname)8s] %(message)s"))
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.addHandler(handler)
    parzzley_logger = logging.getLogger(parzzley.__name__)
    parzzley_logger.setLevel(logging.DEBUG if debug else logging.WARNING)


if __name__ == "__main__":
    main()
