#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Item events. See also :py:mod:`parzzley.sync.aspect.events`.
"""
# pylint: disable=too-many-ancestors
import abc
import dataclasses
import typing as t

import parzzley.sync.aspect.events.sync_run as _sync_run_events

if t.TYPE_CHECKING:
    import parzzley


class _WithSetItemInfo(abc.ABC):

    @abc.abstractmethod
    def set_item_info(
        self, item_type: "parzzley.fs.ItemType", stream_cookie, *, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> None:
        """
        Set item info for this site or another.

        :param item_type: The item type.
        :param stream_cookie: The stream cookie.
        :param for_site: The site to store the item info for (default: the current site).
        """


class _WithStreamCookie(abc.ABC):

    @abc.abstractmethod
    def stream_cookie(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> "parzzley.fs.Site.TCookie":
        """
        Return the stream cookie of the main stream, usually determined in
        :py:class:`parzzley.sync.aspect.events.item.stream.DetermineCookie`.

        For details about cookies, see :py:meth:`parzzley.fs.Site.cookie`.

        This is the same as `stream_cookie` of stream events related to the main stream (i.e. :code:`""`).

        :param for_site: For which site? Default is the event's current site.
        """


class _WithWorkingItems(abc.ABC):

    @abc.abstractmethod
    def working_items(self, *, for_site: "parzzley.fs.TSiteInput|None" = None) -> t.Iterable["parzzley.fs.Item"]:
        """
        Return all working items. Those are either the ones added by :py:meth:`add_working_item` earlier, or, if none
        are added, it is a list containing only :py:attr:`item` (if it exists on item master and is not a directory).

        :param for_site: For which site? Default is the event's current site.
        """


class _Event(_sync_run_events._EventAfterStreamSupportDetermined, abc.ABC):
    """
    Base class for an aspect event on an :py:class:`parzzley.fs.Item`.

    Such events potentially happen once for each visited file, directory, etc.
    """

    @property
    @abc.abstractmethod
    def item(self) -> "parzzley.fs.Item":
        """
        The current item.
        """

    @abc.abstractmethod
    def mark_full_retry_needed(self) -> None:
        """
        Mark the current item for a full retry (e.g. because ongoing changes were detected during update).
        """

    @property
    @abc.abstractmethod
    def is_marked_full_retry_needed(self) -> bool:
        """
        Whether the current item is marked for a full retry (see :py:meth:`mark_full_retry_needed`).
        """


class DecideToSkip(_Event, abc.ABC):
    """
    Occurs in order to decide if to skip an item according to criteria like path exclusions.

    See :py:meth:`skip_item`.

    It is the earliest item event, happening before :py:class:`Prepare` and various preparation steps for each of the
    supported streams.

    These and all other following item events will only occur if this event does not decide to skip the current item.
    """

    @property
    @abc.abstractmethod
    def is_item_marked_to_skip(self) -> bool:
        """
        Whether the current item is marked for being skipped at least this time (i.e. by :py:meth:`skip_item`).
        """

    @property
    @abc.abstractmethod
    def is_item_marked_to_skip_permanently(self) -> bool:
        """
        Whether the current item is marked for being skipped permanently (i.e. by :py:meth:`skip_item`).
        """

    @abc.abstractmethod
    def skip_item(self, *, only_now: bool = False) -> None:
        """
        Mark the current item for being skipped.

        :param only_now: Whether to skip this item now, but keep its internal state data for later sync runs.
        """

    def sites_involved_in_current_item_last_successful_sync(self) -> t.Sequence[str] | None:
        """
        Return the name of the sites that were involved in the last sync run which has successfully synced the current
        item (this is the last sync run if was successful and has not skipped the current item), or :code:`None` if it
        was not synced yet.
        """


class Prepare(_Event, abc.ABC):
    """
    Occurs in order to prepare item sync.

    It is a very early item event, happening after :py:class:`DecideToSkip` and before various preparation steps for
    each of the supported streams.

    Typical implementations use this event e.g. for handling (parts of) the item-retry logic.
    """


class _EventAfterItemTypeKnown(_Event, abc.ABC):
    """
    Base class for item events that occur after the item type was determined.
    """

    @abc.abstractmethod
    def item_type(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> "parzzley.fs.ItemType":
        """
        Return the just determined type for the current item.

        :param for_site: For which site? Default is the event's current site.
        """


class DetermineType(_Event, _WithStreamCookie, abc.ABC):
    """
    Occurs in order to determine the item type (usually derived from the main stream cookie).

    This event should solely be handled in Parzzley infrastructure aspects, not in custom ones!

    See :py:meth:`set_item_type` and :py:meth:`stream_cookie`.

    It happens during the preparation steps of the main stream, after
    :py:class:`parzzley.sync.aspect.events.item.stream.DetermineCookie` and before
    :py:class:`parzzley.sync.aspect.events.item.stream.DetectChanges` of the main stream.

    The typical implementation just queries :code:`parzzley.fs.Size.item_type_by_cookie` using the cookie from
    :py:class:`parzzley.sync.aspect.events.item.stream.DetermineCookie`.
    """

    @abc.abstractmethod
    def set_item_type(
        self, item_type: "parzzley.fs.ItemType", *, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> None:
        """
        Declare the item type of the current item on this site.

        :param item_type: The item type.
        :param for_site: For which site? Default is the event's current site.
        """


class SkipDueToConflicts(_Event, abc.ABC):
    """
    Occurs when an item was skipped due to conflicts.

    It happens after the stream preparation is done, before :py:class:`RefreshItemsBook`.
    """

    @dataclasses.dataclass
    class _Conflict:
        stream_name: str
        description: str
        details: str | None

    @property
    @abc.abstractmethod
    def all_conflicts(self) -> t.Iterable[_Conflict]:
        """
        Conflicts.
        """


class _EventAfterMainStreamMasterSiteDetermined(_EventAfterItemTypeKnown, abc.ABC):

    @property
    def master_site(self) -> "parzzley.fs.Site":
        """
        The site that was determined to keep the 'right' (usually: most recent) data for the main stream.

        This is the same as `master_site` of stream events related to the main stream (i.e. :code:`""`).
        """
        return self._master_site()

    @abc.abstractmethod
    def content_version(self, for_site: "parzzley.fs.TSiteInput|None" = None, *, only_past: bool) -> int:
        """
        Return the version number of the current item's main stream, for this site or any other one.

        This is the same as `content_version` of stream events related to the main stream (i.e. :code:`""`).
        See there for more details.

        :param for_site: For which site? Default is the event's current site.
        :param only_past: Depending on this flag, this will either always be the sn of a sync run from the past, i.e. it
                          will always be less than the current sync run's sn, or it returns the current sync run's sn if
                          there were changes detected since the last sync run.
        """

    @abc.abstractmethod
    def _master_site(self, of_stream: str | None = None) -> "parzzley.fs.Site":
        """
        Return the master site for the given stream (or the item's main stream).
        """


class PrepareUpdating(_EventAfterMainStreamMasterSiteDetermined, _WithSetItemInfo, abc.ABC):
    """
    Occurs in order to prepare item updates.

    A handler may apply local changes to the item. If it does, :py:meth:`set_item_info` must be called afterward.

    It happens as first step after the stream preparation is done and no conflicts occurred, before
    :py:class:`SetUpWorkingItems`.
    """


class SetUpWorkingItems(_EventAfterMainStreamMasterSiteDetermined, _WithStreamCookie, _WithWorkingItems, abc.ABC):
    """
    Occurs in order to maybe create working items in non-master sites that can receive the main content and secondary
    streams for an item and can be committed (ideally atomically) later.

    See :py:meth:`add_working_item`.

    It happens as early after the stream preparation is done and no conflicts occurred, after
    :py:class:`PrepareUpdating` and before the per-stream update events.

    A typical implementation would create a temporary working item if on this site the main stream needs an update from
    the master site. In other situations, i.e. if this site's main stream is already up-to-date, there will be no
    temporary working item. In later events, other streams will directly apply their updates in place instead.
    """

    @abc.abstractmethod
    def working_items(self, *, for_site: "parzzley.fs.TSiteInput|None" = None) -> t.Iterable["parzzley.fs.Item"]:
        """
        Return all working items. Those are either the ones added by :py:meth:`add_working_item` earlier, or, if none
        are added, it is a list containing only :py:attr:`item` (if it exists on item master and is not a directory).

        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def add_working_item(
        self, working_item: "parzzley.fs.TItemInput", *, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> None:
        """
        Add a working item.

        :param working_item: The working item.
        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def remove_working_item(
        self, working_item: "parzzley.fs.TItemInput", *, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> None:
        """
        Remove a working item.

        :param working_item: The working item.
        :param for_site: For which site? Default is the event's current site.
        """


class ApplyUpdate(_EventAfterMainStreamMasterSiteDetermined, abc.ABC):
    """
    Occurs in order to finish/apply stream updates (particularly these that were not in-place updates).
    All apply implementations should be atomic, i.e. whenever they actually apply an update, they should either fail,
    leaving the destination untouched, or succeed completely. They should never e.g. cleanup the destination but then
    maybe fail to bring the new copy in place!

    If the item was touched by the update, :py:meth:`update_cookies` must be called.

    It happens after the stream update events occurred and is one of the latest events of item processing, before
    :py:class:`RefreshItemsBook`.
    """

    @abc.abstractmethod
    def update_cookies(self, stream_cookies, *, for_site: "parzzley.fs.TSiteInput|None" = None) -> None:
        """
        Set new cookies as they are after the update for this site.

        If the given dictionary contains only some of the supported stream names, the other stream cookies will stay
        untouched (like :code:`dict.update()`)!

        :param stream_cookies: The new stream cookies.
        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def streams_with_destination_streamables(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> t.Sequence[str]:
        """
        Return the list of stream names for which there are any destination streamables on this site or any other one.

        :param for_site: For which site? Default is the event's current site.
        """


class RefreshItemsBook(_EventAfterItemTypeKnown, abc.ABC):
    """
    Occurs in order to refresh item books after item stream updates.

    This event should solely be handled in Parzzley infrastructure aspects, not in custom ones!

    See :py:meth:`updated_cookie` and :py:meth:`set_item_book_entry`.

    It happens after the stream update, i.e. after :py:class:`ApplyUpdate` (or after a conflict was detected).

    The typical implementation primarily stores the "updated cookie" (determined in :py:class:`ApplyUpdate`), so it can
    be used for decisions in the next sync run.
    """

    @abc.abstractmethod
    def updated_cookie(
        self, stream_name: str, *, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> "parzzley.fs.TCookie":
        """
        The updated cookie for a given stream that needs to be stored.

        :param stream_name: The stream name.
        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def set_item_book_entry(
        self,
        item_type: "parzzley.fs.ItemType",
        cookies: dict[str, object],
        *,
        for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> None:
        """
        Write an entry to the item book. This info can be used in later sync runs.

        :param item_type: The new item type to store.
        :param cookies: The new stream cookies to store.
        :param for_site: For which site? Default is the event's current site.
        """
