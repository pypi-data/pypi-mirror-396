#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Sync logger exclusion conditions. See :py:class:`SimpleCondition`.
"""
import re
import typing as t

import parzzley.sync.logger


class SimpleCondition(parzzley.sync.logger.Exclude.Condition):
    """
    Represents a simple condition.
    """

    def __init__(
        self,
        *,
        message: str | None = None,
        message_re: str | None = None,
        item: str | None = None,
        item_re: str | None = None,
        severity_below: parzzley.sync.logger.Severity | None = None,
        stream: str | None = None,
    ):
        super().__init__()
        self.__message = message
        self.__message_re = None if message_re is None else re.compile(message_re)
        self.__item = item
        self.__item_re = None if item_re is None else re.compile(item_re)
        self.__severity_below = severity_below
        self.__stream = stream

    def is_met(self, entry):  # pylint: disable=too-many-return-statements
        item_str = "" if entry.item is None else f"/{repr(entry.item.path)[2:-1]}"

        if self.__item is not None and (item_str == self.__item):
            return True
        if self.__severity_below is not None and (entry.severity < self.__severity_below):
            return True
        if self.__stream is not None and ((entry.stream or "") == self.__stream):
            return True
        if self.__message is not None and (entry.message == self.__message):
            return True
        if self.__message_re is not None and self.__message_re.fullmatch(entry.message):
            return True
        if self.__item_re is not None and self.__item_re.fullmatch(item_str):
            return True

        return False


class ConditionAllOf(parzzley.sync.logger.Exclude.Condition):
    """
    Represents the AND-combination of its inner conditions.
    """

    def __init__(self, *, conditions: t.Iterable[parzzley.sync.logger.Exclude.Condition]):
        super().__init__()
        self.__conditions = tuple(conditions)

    def is_met(self, entry):
        for condition in self.__conditions:
            if not condition.is_met(entry):
                return False
        return True


class ConditionAnyOf(parzzley.sync.logger.Exclude.Condition):
    """
    Represents the OR-combination of its inner conditions.
    """

    def __init__(self, *, conditions: t.Iterable[parzzley.sync.logger.Exclude.Condition]):
        super().__init__()
        self.__conditions = tuple(conditions)

    def is_met(self, entry):
        for condition in self.__conditions:
            if condition.is_met(entry):
                return True
        return False


class ConditionNegate(parzzley.sync.logger.Exclude.Condition):
    """
    Represents the negation of its inner condition.
    """

    def __init__(self, *, condition: parzzley.sync.logger.Exclude.Condition):
        super().__init__()
        self.__condition = condition

    def is_met(self, entry):
        return not self.__condition.is_met(entry)
