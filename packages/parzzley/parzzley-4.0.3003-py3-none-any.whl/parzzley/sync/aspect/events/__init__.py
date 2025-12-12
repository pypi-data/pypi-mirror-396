#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Aspect events are part of the plug-in mechanism that encapsulates its behavior in aspects.

In the course of a sync run, the Parzzley engine will trigger those events in a particular order. Aspects implement
various parts of Parzzley functionality by handling some of those events (while the engine itself does not much more
than triggering these events).

The Parzzley documentation also contains an overview of aspect events and how they actually perform their duty of
filesystem synchronization.
"""
import abc
import typing as t

if t.TYPE_CHECKING:
    import parzzley


class _Event(abc.ABC):
    """
    Base class for all events that can be handled by aspects. They are fired by the sync engine in order to execute the
    actual sync logic that is configured. See also :py:mod:`parzzley.sync.aspect` for the basic idea.
    """

    @property
    @abc.abstractmethod
    def site(self) -> "parzzley.fs.Site":
        """
        The current site.

        This is the site which this aspect is associated with, so it usually operates on this site.
        """


class Data:
    """
    Event data variable for storage of arbitrary information during a sync run (or smaller scopes).
    """

    def __init__(self, initial_value=None, *, per_site: bool = False, per_item: bool = False, per_stream: bool = False):
        """
        :param initial_value: The initial value.
        :param per_site: Whether this data is stored separately per site (giving it a smaller scope).
        :param per_item: Whether this data is stored separately per item (giving it a smaller scope).
        :param per_stream: Whether this data is stored separately per stream (giving it a smaller scope).
        """
        self.__initial_value = initial_value
        self.__per_site = per_site
        self.__per_item = per_item
        self.__per_stream = per_stream

    def get(self, event: _Event, *, key_data: dict | None = None):
        """
        Return the current value.

        :param event: The event that carries the given situation.
        :param key_data: Additional selector key. Do not use.
        """
        return event._get_data(
            self, self.__per_site, self.__per_item, self.__per_stream, key_data, self.__initial_value
        )

    def set(self, event: _Event, value: object, key_data: dict | None = None) -> None:
        """
        Set the value.

        :param event: The event that carries the given situation.
        :param value: The new value.
        :param key_data: Additional selector key. Do not use.
        """
        event._set_data(self, self.__per_site, self.__per_item, self.__per_stream, key_data, value)
