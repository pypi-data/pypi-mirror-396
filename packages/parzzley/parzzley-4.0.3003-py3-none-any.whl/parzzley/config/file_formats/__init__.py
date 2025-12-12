# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
File formats for Parzzley configuration files.

See also the submodules.
"""
import abc
import datetime
import pathlib
import typing as t

import parzzley.sync.logger

if t.TYPE_CHECKING:
    import parzzley.config


class FileFormat(abc.ABC):
    """
    A file format for Parzzley configuration files.
    """

    def parse_file(self, config_file: pathlib.Path) -> t.Any:
        """
        Read and return the configuration from the given configuration file.

        :param config_file: The configuration file to parse.
        """


_formats = {}


def register_file_format(format_name: str):
    """
    Return a decorator that registers a file format for Parzzley configuration files.

    :param format_name: The format name.
    """

    def decorator(format_type: type["FileFormat"]):
        _formats[format_name] = format_type()
        return format_type

    return decorator


def parse(path: pathlib.Path | str) -> t.Any:
    """
    Parse a Parzzley configuration file.

    :param path: The configuration file.
    """
    return _file_format("xml").parse_file(pathlib.Path(path))


def read_configuration(parzzley_config_dir: pathlib.Path | str) -> "parzzley.config.Configuration":
    """
    Parse an entire Parzzley configuration directory.

    :param parzzley_config_dir: The configuration directory.
    """
    volumes = []
    loggings = []
    for parzzley_config_file in pathlib.Path(parzzley_config_dir).iterdir():
        if file_format := _file_format(parzzley_config_file.suffix[1:].lower()):
            entity = file_format.parse_file(parzzley_config_file)
            if isinstance(entity, parzzley.config.Volume):
                volumes.append(entity)
            elif isinstance(entity, parzzley.config.Logging):
                loggings.append(entity)
            else:
                raise RuntimeError(f"unknown entity type: {type(entity)}")

    return parzzley.config.Configuration(volumes=volumes, loggings=loggings)


def timedelta(s: str | float | datetime.timedelta) -> datetime.timedelta:
    """
    Translate a timedelta specification (usually a string when it comes from configuration files) to a timedelta.

    :param s: The timedelta specification.
    """
    if isinstance(s, datetime.timedelta):
        return s
    if isinstance(s, float):
        s = f"{s}s"
    if isinstance(s, str):
        for unit, factor in (("d", 24 * 60 * 60), ("h", 60 * 60), ("m", 60), ("s", 1), ("", 1)):
            if s.endswith(unit):
                return datetime.timedelta(seconds=float(s[: -len(unit)]) * factor)
    raise ValueError(f"invalid timedelta: {s}")


def log_severity(s: "str|parzzley.sync.logger.Severity") -> "parzzley.sync.logger.Severity":
    """
    Translate a log severity specification (usually a string when it comes from configuration files) to a log severity.

    :param s: The log severity specification.
    """
    if isinstance(s, parzzley.sync.logger.Severity):
        return s
    if isinstance(s, str):
        return getattr(parzzley.sync.logger.Severity, s)
    raise ValueError(f"invalid log severity: {s}")


def _file_format(format_name: str) -> "FileFormat|None":
    """
    Return the file format by name.

    :param format_name: The format name. See :py:func:`register_file_format`.
    """
    import parzzley.config.file_formats.xml as _  # pylint: disable=cyclic-import,import-outside-toplevel

    return _formats.get(format_name)
