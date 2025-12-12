#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Aspect event execution conditions.

See :py:class:`Condition`.
"""
import abc
import typing as t

import parzzley.fs


class Condition(abc.ABC):
    """
    Base class for aspect event execution conditions.

    These conditions can be applied to an aspect event handler in order to skip it in some situations (with less code
    than explicit checks in the event handler body).
    """

    @abc.abstractmethod
    def is_met(self, event) -> bool:
        """
        Return whether this condition is met (i.e. the event handler is not to be skipped by this condition) in a given
        situation.

        :param event: The event that carries the given situation.
        """


class _ItemExistsCondition(Condition, abc.ABC):
    """
    Base class for conditions that check whether the item exists on some site.
    """

    def __init__(self, value: bool = True):
        """
        :param value: Whether to apply the check in a positive way. Set to :code:`False` to negate the condition.
        """
        super().__init__()
        self.__value = bool(value)

    def is_met(self, event) -> bool:
        return bool(event.item_type(self._site(event)) != parzzley.fs.ItemType.NONE) == self.__value

    @abc.abstractmethod
    def _site(self, event):
        """
        The site to check by this condition.

        :param event: The event that carries the given situation.
        """


class _ItemIsTypeCondition(Condition, abc.ABC):
    """
    Base class for conditions that check against the item type on some site.
    """

    def __init__(self, *types: parzzley.fs.ItemType, no: t.Iterable[parzzley.fs.ItemType] | None = None):
        """
        :param types: The allowed types.
        :param no: Alternatively to :code:`types`, the non-allowed types.
        """
        super().__init__()
        self.__types = set(types)
        self.__not_types = set(no or ())
        if self.__types and self.__not_types:
            raise ValueError("mixing positive and negative type specification is not allowed")

    def is_met(self, event):
        item_type = event.item_type(self._site(event))
        if self.__not_types and item_type in self.__not_types:
            return False
        if self.__types and item_type not in self.__types:
            return False
        return True

    @abc.abstractmethod
    def _site(self, event):
        """
        The site to check by this condition.

        :param event: The event that carries the given situation.
        """


class _IsItemTypeSupportedByStreamCondition(Condition, abc.ABC):
    """
    Base class for conditions that check whether the item type on some site is supported by the current stream.
    """

    def __init__(self, value: bool = True):
        """
        :param value: Whether to apply the check in a positive way. Set to :code:`False` to negate the condition.
        """
        super().__init__()
        self.__value = bool(value)

    def is_met(self, event):
        return (
            bool(
                event.item_type(self._site(event)) in event.stream_support_info.supported_item_types(event.stream_name)
            )
            == self.__value
        )

    @abc.abstractmethod
    def _site(self, event):
        """
        The site to check by this condition.

        :param event: The event that carries the given situation.
        """


class ItemExistsHere(_ItemExistsCondition):
    """
    Condition that checks whether the item exists on the current site.
    """

    def _site(self, event):
        return event.site


class ItemHereIsType(_ItemIsTypeCondition):
    """
    Condition that checks against the item type on the current site.
    """

    def _site(self, event):
        return event.site


class ItemExistsOnMasterSite(_ItemExistsCondition):
    """
    Condition that check whether the item exists on the master site (of the current stream or another one).
    """

    def __init__(self, value: bool = True, of_stream: str | None = None):
        """
        :param value: Whether to apply the check in a positive way. Set to :code:`False` to negate the condition.
        :param of_stream: Which stream to check (default: the current one).
        """
        super().__init__(value)
        self.__of_stream = of_stream

    def _site(self, event):
        return event._master_site(self.__of_stream)


class ItemOnMasterSiteIsType(_ItemIsTypeCondition):
    """
    Condition that checks against the item type on the master site (of the current stream or another one).
    """

    def __init__(
        self,
        *types: parzzley.fs.ItemType,
        no: t.Iterable[parzzley.fs.ItemType] | None = None,
        of_stream: str | None = None
    ):
        """
        :param types: The allowed types.
        :param no: Alternatively to :code:`types`, the non-allowed types.
        :param of_stream: Which stream to check (default: the current one).
        """
        super().__init__(*types, no=no)
        self.__of_stream = of_stream

    def _site(self, event):
        return event._master_site(self.__of_stream)


class ThisIsMasterSite(Condition):
    """
    Condition that checks whether the current site is the master site (of the current stream or another one).
    """

    def __init__(self, value: bool = True, *, of_stream: str | None = None):
        """
        :param value: Whether to apply the check in a positive way. Set to :code:`False` to negate the condition.
        :param of_stream: Which stream to check (default: the current one).
        """
        super().__init__()
        self.__value = bool(value)
        self.__of_stream = of_stream

    def is_met(self, event):
        return (event._master_site(self.__of_stream) == event.site) == self.__value


class IsStream(Condition):
    """
    Condition that checks against the current stream name.
    """

    def __init__(self, stream_name: str):
        """
        :param stream_name: The stream name.
        """
        super().__init__()
        self.__stream_name = stream_name

    def is_met(self, event):
        return event.stream_name == self.__stream_name


class IsItemTypeHereSupportedByStream(_IsItemTypeSupportedByStreamCondition):
    """
    Condition that checks whether the item type on the current site is supported by the current stream.
    """

    def _site(self, event):
        return event.site


class IsItemTypeOnStreamMasterSiteSupportedByStream(_IsItemTypeSupportedByStreamCondition):
    """
    Condition that checks whether the item type on the master site (of the current stream) is supported by the current
    stream.
    """

    def _site(self, event):
        return event.master_site
