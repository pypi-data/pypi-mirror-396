#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Directory item events. See also :py:mod:`parzzley.sync.aspect.events`.
"""
import abc
import typing as t

import parzzley.sync.aspect.events.item as _item_events


class _Event(_item_events._EventAfterItemTypeKnown, abc.ABC):
    """
    Base class for an aspect event on an :py:class:`parzzley.fs.Item` which is a directory.

    These extend the stuff from :py:mod:`parzzley.sync.aspect.events.item` by directory specific logic, like directory
    traversal.
    """


class Prepare(_Event, abc.ABC):
    """
    Occurs at the beginning of a directory sync processing,
    after :py:class:`parzzley.sync.aspect.events.item.stream.TransferUpdate` of the main stream, before
    :py:class:`List`.
    """


class List(_Event, abc.ABC):
    """
    Occurs in order to get a list of the directory's children, after :py:class:`Prepare` and before
    :py:class:`Iterated`.

    This event should solely be handled in Parzzley infrastructure aspects, not in custom ones!

    There will be a sequence of per-item (and so also per-stream) events for each determined child item directly after
    this event.

    The typical implementation retrieves that list directly from the site.
    """

    @abc.abstractmethod
    def add_child_names(self, child_names: t.Iterable[str]) -> None:
        """
        Add child names to the list of all children to be processed for this directory.

        :param child_names: The names of the children to be added.
        """


class Iterated(_Event, abc.ABC):
    """
    Occurs at the end of a directory sync, after all children are processed, and before the item updating continues to
    :py:class:`parzzley.sync.aspect.events.item.ApplyUpdate`.
    """
