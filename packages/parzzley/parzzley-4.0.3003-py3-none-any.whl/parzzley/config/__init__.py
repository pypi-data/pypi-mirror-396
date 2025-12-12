#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Parzzley configuration.
"""
# pylint: disable=duplicate-code
import datetime
import typing as t

import parzzley.config.file_formats


class Aspect:
    """
    Configuration for one aspect instance.

    At runtime, this will be transferred to an instance of an implementation of :py:class:`parzzley.sync.aspect.Aspect`.
    """

    def __init__(self, *, type_name: str, arguments: dict[str, str] | None = None):
        """
        :param type_name: The aspect type name.
        :param arguments: The aspect arguments.
        """
        self.__type_name = type_name
        self.__arguments = dict(arguments or ())

    @property
    def type_name(self) -> str:
        """
        The aspect type name.
        """
        return self.__type_name

    @property
    def arguments(self) -> dict[str, str]:
        """
        The aspect arguments.
        """
        return dict(self.__arguments)


class Site:
    """
    Configuration for one site instance.

    At runtime, this will eventually (with some indirections) be transferred to an instance of
    :py:class:`parzzley.fs.Site`.
    """

    def __init__(
        self,
        name: str,
        *,
        kind: str,
        arguments: dict[str, str] | None = None,
        aspects: t.Iterable[Aspect] = (),
        warn_after: datetime.timedelta | None = None
    ):
        """
        :param name: The site name.
        :param kind: The site kind.
        :param arguments: The site arguments.
        :param aspects: The aspects configured specifically for this site.
        :param warn_after: The warn-after duration. See :py:attr:`warn_after`.
        """
        if not name:
            raise ValueError("name must not be empty")
        self.__name = name
        self.__kind = kind
        self.__arguments = dict(arguments or ())
        self.__aspects = tuple(aspects)
        self.__warn_after = warn_after

    @property
    def name(self) -> str:
        """
        The site name.
        """
        return self.__name

    @property
    def kind(self) -> str:
        """
        The site kind.

        See :py:func:`parzzley.fs.register_backend`.
        """
        return self.__kind

    @property
    def warn_after(self) -> datetime.timedelta | None:
        """
        The warn-after duration.

        When Parzzley was not able to successfully synchronize this site for that duration, it will emit a warning
        message.
        """
        return self.__warn_after

    @property
    def arguments(self) -> dict[str, str]:
        """
        The site arguments.
        """
        return dict(self.__arguments)

    @property
    def aspects(self) -> t.Sequence[Aspect]:
        """
        The aspects configured specifically for this site.
        """
        return self.__aspects


class Volume:
    """
    Configuration for one sync volume.

    At runtime, this will be transferred to an instance of :py:class:`parzzley.sync.Volume`.
    """

    def __init__(
        self, name: str, *, sites: t.Iterable[Site], aspects: t.Iterable[Aspect], interval: datetime.timedelta
    ):
        """
        :param name: The volume name.
        :param sites: The sites configured for this volume.
        :param aspects: The aspects configured for all sites.
        :param interval: The configured sync interval.
        """
        if not name:
            raise ValueError("name must not be empty")
        self.__name = name
        self.__sites = tuple(sites)
        self.__aspects = tuple(aspects)
        self.__interval = interval

    @property
    def name(self) -> str:
        """
        The volume name.
        """
        return self.__name

    @property
    def sites(self) -> t.Sequence[Site]:
        """
        The sites configured for this volume.
        """
        return self.__sites

    @property
    def aspects(self) -> t.Sequence[Aspect]:
        """
        The aspects configured for all sites.
        """
        return self.__aspects

    @property
    def interval(self) -> datetime.timedelta:
        """
        The configured sync interval.
        """
        return self.__interval


class Logging:
    """
    Configuration for a logger.

    At runtime, this will be transferred to an instance of an implementation of
    :py:class:`parzzley.sync.logger.Logging`.
    """

    def __init__(
        self,
        *,
        min_severity: str | None,
        max_severity: str | None,
        out: t.Iterable["Logging.Out"],
        formatter: "Logging.Formatter",
        exclude: t.Iterable["Logging.Exclude"]
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

    @property
    def min_severity(self) -> str | None:
        """
        The minimal severity.
        """
        return self.__min_severity

    @property
    def max_severity(self) -> str | None:
        """
        The maximal severity.
        """
        return self.__max_severity

    @property
    def out(self) -> t.Sequence["Logging.Out"]:
        """
        The logger output channels.
        """
        return self.__out

    @property
    def formatter(self) -> "Logging.Formatter":
        """
        The log formatter.
        """
        return self.__formatter

    @property
    def exclude(self) -> t.Sequence["Logging.Exclude"]:
        """
        The logger exclusions.
        """
        return self.__exclude

    class Out:
        """
        Configuration for a logger output channel.

        At runtime, this will be transferred to an instance of an implementation of
        :py:class:`parzzley.sync.logger.Out`.
        """

        def __init__(self, *, kind: str, arguments: dict[str, str] | None = None):
            """
            :param kind: The kind of logger output channel.
            :param arguments: The logger output channel argument.
            """
            self.__kind = kind
            self.__arguments = dict(arguments or ())

        @property
        def kind(self) -> str:
            """
            The kind of logger output channel.
            """
            return self.__kind

        @property
        def arguments(self) -> dict[str, str]:
            """
            The logger output channel argument.
            """
            return dict(self.__arguments)

    class Formatter:
        """
        Configuration for a log formatter.

        At runtime, this will be transferred to an instance of an implementation of
        :py:class:`parzzley.sync.logger.Formatter`.
        """

        def __init__(self, *, kind: str, arguments: dict[str, str] | None = None):
            """
            :param kind: The kind of log formatter.
            :param arguments: The log formatter argument.
            """
            self.__kind = kind
            self.__arguments = dict(arguments or ())

        @property
        def kind(self) -> str:
            """
            The kind of log formatter.
            """
            return self.__kind

        @property
        def arguments(self) -> dict[str, str]:
            """
            The log formatter argument.
            """
            return dict(self.__arguments)

    class Exclude:
        """
        Configuration for a logger exclusion.

        At runtime, this will be transferred to an instance of an implementation of
        :py:class:`parzzley.sync.logger.Exclude`.
        """

        def __init__(self, *, conditions: t.Iterable["Logging.Exclude.BaseCondition"]):
            """
            :param conditions: Exclusion conditions.
            """
            self.__conditions = tuple(conditions)

        @property
        def conditions(self) -> t.Sequence["Logging.Exclude.BaseCondition"]:
            """
            Exclusion conditions. A message will be excluded if any of these conditions are true.
            """
            return self.__conditions

        class BaseCondition:
            """
            Configuration for a logger exclusion condition. Base class of some subclasses.

            At runtime, this will be transferred to an instance of an implementation of
            :py:class:`parzzley.sync.logger.Exclude.Condition`.
            """

        class Condition(BaseCondition):
            """
            Configuration for a simple logger exclusion condition.
            """

            def __init__(self, *, arguments: dict[str, str] | None = None):
                """
                :param arguments: The condition arguments.
                """
                self.__arguments = dict(arguments or ())

            @property
            def arguments(self) -> dict[str, str]:
                """
                The condition arguments.
                """
                return dict(self.__arguments)

        class CombinedCondition(BaseCondition):
            """
            Configuration for a combined logger exclusion condition.
            """

            def __init__(self, *, combination: str, conditions: t.Iterable["Logging.Exclude.BaseCondition"]):
                """
                :param combination: The combination. Either :code:`'AND'` or :code:`'OR'`.
                :param conditions: The conditions to combine.
                """
                self.__combination = combination
                self.__conditions = tuple(conditions)

            @property
            def combination(self) -> str:
                """
                The combination. Either :code:`'AND'` or :code:`'OR'`.
                """
                return self.__combination

            @property
            def conditions(self) -> t.Sequence["Logging.Exclude.BaseCondition"]:
                """
                The conditions to combine.
                """
                return self.__conditions

        class NegateCondition(BaseCondition):
            """
            Configuration for a negating logger exclusion condition.
            """

            def __init__(self, *, condition: "Logging.Exclude.BaseCondition"):
                """
                :param condition: The condition to negate.
                """
                self.__condition = condition

            @property
            def condition(self) -> "Logging.Exclude.BaseCondition":
                """
                The condition to negate.
                """
                return self.__condition


class Configuration:
    """
    Represents one complete Parzzley configuration.
    """

    def __init__(self, *, volumes: t.Iterable[Volume], loggings: t.Iterable[Logging]):
        """
        :param volumes: The sync volumes.
        :param loggings: The loggings.
        """
        self.__volumes = tuple(volumes)
        self.__loggings = tuple(loggings)

    @property
    def volumes(self) -> t.Sequence[Volume]:
        """
        The sync volumes.
        """
        return self.__volumes

    @property
    def loggings(self) -> t.Sequence[Logging]:
        """
        The loggings.
        """
        return self.__loggings
