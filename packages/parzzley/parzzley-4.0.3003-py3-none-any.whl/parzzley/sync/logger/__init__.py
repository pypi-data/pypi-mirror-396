#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Sync logging. See :py:class:`Logger`.
"""
import abc
import enum
import functools
import logging
import traceback
import typing as t

if t.TYPE_CHECKING:
    import parzzley.sync.run


_logger = logging.getLogger(__name__)


@functools.total_ordering
class Severity(enum.Enum):
    """
    Message severity.
    """

    #: Debug severity.
    DEBUG = enum.auto()

    #: Info severity.
    INFO = enum.auto()

    #: Warning severity.
    WARNING = enum.auto()

    #: Fatal severity.
    FATAL = enum.auto()

    def __lt__(self, other):
        if type(self) is type(other):
            return self.value < other.value
        return None


class Logger(abc.ABC):
    """
    Base class for a sync logger, as used for logging e.g. by aspects and the sync engine itself.
    """

    @abc.abstractmethod
    def _log(self, severity: Severity, message: str, message_args: t.Sequence[t.Any]) -> None:
        """
        Log a message.

        :param severity: The message severity.
        :param message: The message text (as Python logging format string; see :code:`message_args`).
        :param message_args: The message arguments.
        """

    def debug(self, message: str, *message_args: t.Sequence[t.Any]) -> None:
        """
        Log a message with 'debug' severity.

        :param message: The message text (as Python logging format string; see :code:`message_args`).
        :param message_args: The message arguments.
        """
        self._log(Severity.DEBUG, message, message_args)

    def info(self, message: str, *message_args: t.Sequence[t.Any]) -> None:
        """
        Log a message with 'info' severity.

        :param message: The message text (as Python logging format string; see :code:`message_args`).
        :param message_args: The message arguments.
        """
        self._log(Severity.INFO, message, message_args)

    def warning(self, message: str, *message_args: t.Sequence[t.Any]) -> None:
        """
        Log a message with 'warning' severity.

        :param message: The message text (as Python logging format string; see :code:`message_args`).
        :param message_args: The message arguments.
        """
        self._log(Severity.WARNING, message, message_args)

    def fatal(self, message: str, *message_args: t.Sequence[t.Any]) -> None:
        """
        Log a message with 'fatal' severity.

        :param message: The message text (as Python logging format string; see :code:`message_args`).
        :param message_args: The message arguments.
        """
        self._log(Severity.FATAL, message, message_args)


class Entry:
    """
    Represents a single sync log entry.
    """

    def __init__(
        self,
        *,
        severity: Severity,
        message: str,
        message_args: t.Iterable[t.Any],
        item: "parzzley.fs.Item|None",
        stream: str | None
    ):
        """
        :param severity: The entry severity.
        :param message: The entry message (as Python logging format string; see :code:`message_args`).
        :param message_args: The entry message arguments.
        :param item: The associated item.
        :param stream: The associated stream name.
        """
        self.__severity = severity
        self.__message = message
        self.__message_args = message_args
        self.__item = item
        self.__stream = stream
        self.__resolved_message = None

    @property
    def severity(self) -> Severity:
        """
        The entry severity.
        """
        return self.__severity

    @property
    def message(self) -> str:
        """
        The entry message.

        This is already the resolved final string, with the :code:`message_args` applied.
        """
        if self.__resolved_message is None:
            self.__resolved_message = self.__message % self.__message_args
        return self.__resolved_message

    @property
    def item(self) -> "parzzley.fs.Item|None":
        """
        The associated item.
        """
        return self.__item

    @property
    def stream(self) -> str | None:
        """
        The associated stream name.
        """
        return self.__stream


class Logging:
    """
    Represents one logging setup (usually as specified in some configuration file).

    This is mostly used by the engine in order to provide the sync reports (i.e. the final product of this entire
    module).
    """

    def __init__(
        self,
        *,
        min_severity: Severity | None,
        max_severity: Severity | None = None,
        out: t.Iterable["Out"],
        formatter: "Formatter",
        exclude: t.Iterable["Exclude"] = ()
    ):
        """
        :param min_severity: The minimal severity.
        :param max_severity: The maximal severity.
        :param out: The logger output channels.
        :param formatter: The log formatter.
        :param exclude: The log exclusions.
        """
        self.__min_severity = min_severity
        self.__max_severity = max_severity
        self.__out = tuple(out)
        self.__formatter = formatter
        self.__exclude = tuple(exclude)

    def emit(self, sync_run: "parzzley.sync.run.SyncRun|None", entries: t.Iterable[Entry]) -> None:
        """
        Emit a list of entries, after filtering as specified, formatted by the formatter, to the specified logger output
        channels.

        If errors are raised from the formatter or the output channels, this method will log these callstacks to Python
        logging, but does not forward these errors! It will just return normally instead.

        :param sync_run: The sync run (or :code:`None` if this report is not associated to a particular sync run).
        :param entries: The entries.
        """
        actual_entries = []
        for entry in entries:
            if self.__min_severity is not None and entry.severity < self.__min_severity:
                continue
            if self.__max_severity is not None and entry.severity > self.__max_severity:
                continue

            exclude = False
            for exclusion in self.__exclude:
                if exclusion.is_met(entry):
                    exclude = True
                    break
            if exclude:
                continue

            actual_entries.append(entry)

        if not actual_entries:
            return

        try:
            output = self.__formatter.format(sync_run, actual_entries)
        except Exception:  # pylint: disable=broad-exception-caught
            _logger.warning(traceback.format_exc())
            return

        for out in self.__out:
            try:
                out.emit_text(sync_run, output)
            except Exception:  # pylint: disable=broad-exception-caught
                _logger.warning(traceback.format_exc())


class Formatter(abc.ABC):
    """
    Base class for an implementation of a log formatter.
    """

    @abc.abstractmethod
    def format(self, sync_run: "parzzley.sync.run.SyncRun|None", entries: t.Iterable[Entry]) -> str:
        """
        Format the given entries to a textual representation.

        :param sync_run: The sync run (or :code:`None` if this report is not associated to a particular sync run).
        :param entries: The entries.
        """


class Out(abc.ABC):
    """
    Base class for an implementation of a logger output channel.
    """

    @abc.abstractmethod
    def emit_text(self, sync_run: "parzzley.sync.run.SyncRun|None", s: str) -> None:
        """
        Emit the text via this output channel.

        :param sync_run: The sync run (or :code:`None` if this report is not associated to a particular sync run).
        :param s: The text to emit.
        """


class Exclude:
    """
    Represents an entry exclusion definition.
    """

    def __init__(self, conditions: t.Iterable["Exclude.Condition"]):
        """
        :param conditions: The conditions. A message gets excluded if it matches at least one of these conditions.
        """
        conditions_ = conditions
        # pylint: disable=cyclic-import,import-outside-toplevel
        from parzzley.sync.logger.conditions import ConditionAnyOf

        self.__inner_condition = ConditionAnyOf(conditions=conditions_)

    def is_met(self, entry: Entry) -> bool:
        """
        Return whether this exclusion definition is met by the given log entry.

        :param entry: The log entry.
        """
        return self.__inner_condition.is_met(entry)

    class Condition(abc.ABC):
        """
        Represents an exclusion condition.

        See subclasses in :py:mod:`parzzley.sync.logger.conditions`.
        """

        @abc.abstractmethod
        def is_met(self, entry: Entry) -> bool:
            """
            Return whether this condition is met by the given log entry.

            :param entry: The log entry.
            """


_registered_formatters = {}


def register_formatter(formatter_type: type[Formatter]) -> type[Formatter]:
    """
    Make a log formatter class available to be used, e.g. in logger configurations, by its kind name.
    The kind name is the parent module name (e.g. :code:`"baz"` if the type is implemented in a package like
    :code:`foo.bar.baz`).

    :param formatter_type: The log formatter class to register.
    """
    _registered_formatters[formatter_type.__module__.rpartition(".")[2]] = formatter_type
    return formatter_type


def formatter_type_by_kind(kind: str) -> type[Formatter] | None:
    """
    Return a log formatter type by the kind name.

    :param kind: The log formatter kind.
    """
    return _registered_formatters.get(kind)


_registered_outs = {}


def register_out(out_type: type[Out]) -> type[Out]:
    """
    Make a logger output channel class available to be used, e.g. in logger configurations, by its kind name.
    The kind name is the parent module name (e.g. :code:`"baz"` if the type is implemented in a package like
    :code:`foo.bar.baz`).

    :param out_type: The logger output channel class to register.
    """
    _registered_outs[out_type.__module__.rpartition(".")[2]] = out_type
    return out_type


def out_by_kind(kind: str) -> type[Out] | None:
    """
    Return a logger output channel type by the kind name.

    :param kind: The logger output channel kind.
    """
    return _registered_outs.get(kind)
