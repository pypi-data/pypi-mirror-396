#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Item stream events. See also :py:mod:`parzzley.sync.aspect.events`.
"""
# pylint: disable=too-many-ancestors
import abc
import dataclasses
import typing as t

import parzzley.fs
import parzzley.sync.aspect.events.item as _item_events


class _WithStreamCookie(abc.ABC):

    @abc.abstractmethod
    def stream_cookie(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> "parzzley.fs.Site.TCookie":
        """
        Return the stream cookie of the current stream, usually determined in
        :py:class:`parzzley.sync.aspect.events.item.stream.DetermineCookie`.

        Stream cookies are mostly an opaque data structure (beyond the fact that the main stream's cookie must somehow
        carry the item type), but comparing stream cookies from the same item and site and from different times allows
        to detect changes.

        For the main stream (i.e. :code:`""`), this is the same as `stream_cookie` of some item events.
        """


class _WithSourceStreamableGetters(abc.ABC):

    @abc.abstractmethod
    def source_streamable(
        self, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> "parzzley.fs.stream.ReadStreamable|None":
        """
        Return the source streamable for this site. It is used as the source of the stream update step.

        Usually the source streamable is from the stream master site (this is the main reason to determine it before).

        It was determined earlier in :py:class:`CollectSourceStreamables`.

        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def stream_pipes(
        self, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> t.Iterable["CollectDestinationStreamables.Pipe"]:
        """
        Return all stream pipes.

        They are used by the stream update step as a mechanism to apply changes to the stream while it is transferring
        from the source to the destinations.

        :param for_site: For which site? Default is the event's current site.
        """


class _WithDestinationStreamableGetters(abc.ABC):

    @abc.abstractmethod
    def destination_streamables(self) -> t.Sequence["parzzley.fs.stream.WriteStreamable"]:
        """
        Return all destination streamables. They are used as destinations of the stream update step.

        Usually there is one destination streamable for each site that is not the stream master site. There is usually
        no destination streamable for the master site, as that is the streaming source instead.
        """


class _WithMasterSiteTableSetter(abc.ABC):

    @abc.abstractmethod
    def set_master_site(self, master_site: "parzzley.fs.TSiteInput|None" = None) -> None:
        """
        Set the master site for the current item stream.

        This is usually the site where the other sites will get updated from (regarding the current stream).

        :param master_site: The master site.
        """

    @abc.abstractmethod
    def set_sync_run_sn_of_last_change(self, sn: int, *, for_site: "parzzley.fs.TSiteInput|None" = None) -> None:
        """
        Set the serial number of the sync run that has seen the last change (for this site or any other).

        :param sn: The sync run's serial number.
        :param for_site: For which site? Default is the event's current site.
        """


class _Event(_item_events._EventAfterItemTypeKnown, abc.ABC):
    """
    Base class for an aspect event on a stream of a :py:class:`parzzley.fs.Item`.
    """

    @property
    @abc.abstractmethod
    def stream_name(self) -> str:
        """
        The current stream name.
        """

    @abc.abstractmethod
    def _master_site(self, of_stream: str | None = None) -> "parzzley.fs.Site":
        """
        Return the master site for the given stream (or the current stream).
        """


class _EventAfterItemInfoCollected(_Event, abc.ABC):
    """
    Base class for stream events that occur after information about the stream was collected.
    """


class _EventAfterMasterSiteDetermined(_EventAfterItemInfoCollected, abc.ABC):
    """
    Base class for stream events that occur after the master site for this stream was determined.
    """

    @property
    def master_site(self) -> "parzzley.fs.Site":
        """
        The stream master site (for a particular stream on a particular filesystem item) is the site that is determined
        to contain the 'right' data for this stream, i.e. usually the most recently modified one.

        It is determined after the change detection phase, i.e. mostly during
        :py:class:`parzzley.sync.aspect.events.item.stream.DetermineMasterSiteTable`.

        For the main stream (i.e. :code:`""`), this is the same as `master_site` of some item events.
        """
        return self._master_site()

    @abc.abstractmethod
    def content_version(self, for_site: "parzzley.fs.TSiteInput|None" = None, *, only_past: bool) -> int:
        """
        Return the version number of the current item stream, for this site or any other one.

        This number always refers to a particular sync run. So, it can be the serial number of an earlier sync run,
        meaning that the site has successfully synchronized this item last time in that sync run. Note: This does not
        include sync runs that skipped this file from the beginning or due to conflicts.

        If this item was marked as needing to get refreshed, this will return :code:`0` (meaning: it hast the lowest
        possible version number and so definitely needs to get updated).

        If :code:`only_past` is :code:`False` and there were changes detected, this will return the serial number of the
        current sync run.

        For the main stream (i.e. :code:`""`), this is the same as `content_version` of some item events.

        :param for_site: For which site? Default is the event's current site.
        :param only_past: Whether to exclude the current sync run and only look into the past.
        """


class DetermineComparator(_Event, abc.ABC):
    """
    Occurs in order to determine the comparator for the current item stream.

    This is the first step of stream preparation. It happens before :py:class:`DetermineCookie`.

    Without any changes to the comparator, it will do byte-wise comparison. Aspects can override it for particular
    streams if the comparison is more complicated than that.
    """

    @property
    @abc.abstractmethod
    def comparator(
        self,
    ) -> t.Callable[[parzzley.fs.stream.ReadStreamable, parzzley.fs.stream.ReadStreamable], bool] | None:
        """
        The current comparator (or :code:`None` for the default, byte-wise one). See also :py:meth:`set_comparator`.
        """

    @abc.abstractmethod
    def set_comparator(self, comparator):
        """
        Set the comparator.

        :param comparator: The new comparator.
        """


class DetermineCookie(_Event, abc.ABC):
    """
    Occurs in order to determine the cookie for the current item stream.

    This event should solely be handled in Parzzley infrastructure aspects, not in custom ones!

    This is an early step of stream preparation, after :py:class:`DetermineComparator`. If the current stream is the
    main stream, :py:class:`parzzley.sync.aspect.events.item.DetermineType` happens afterward. Then the stream
    preparation continues to the change detection phase (:py:class:`DetectChanges`).

    The typical implementation just queries the cookie from the site.
    """

    @abc.abstractmethod
    def set_stream_cookie(self, stream_cookie, *, for_site: "parzzley.fs.TSiteInput|None" = None):
        """
        Set the stream cookie for the current item stream.

        :param stream_cookie: The stream cookie.
        :param for_site: For which site? Default is the event's current site.
        """


class DetectChanges(_EventAfterItemInfoCollected, _WithStreamCookie, abc.ABC):
    """
    Occurs in order to detect changes of the current item stream at the current site.

    The detection (as it is implemented by Parzzley builtin aspects) basically works by comparing the recent stream
    cookie with the last one (but the full solution is more complex, e.g. for directories, removed items, ...).

    See :py:meth:`mark_changed`.

    It happens after the stream cookie (and the item type) is known and before :py:class:`DetermineMasterSiteTable`.
    This is all part of the stream preparation.
    """

    @abc.abstractmethod
    def stream_cookie_after_last_sync(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> tuple:
        """
        Return the cookie this item stream had after last sync.

        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def item_type_after_last_sync(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> parzzley.fs.ItemType:
        """
        Return the type this item had after last sync.

        This is only useful for the main stream (i.e. :code:`""`).

        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def mark_changed(self, site: "parzzley.fs.TSiteInput|None" = None) -> None:
        """
        Mark this site as having changed. This might make this site the stream master site later, so the other sites get
        updated from it.

        :param site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def mark_all_last_involved_sites_changed_if_this_is_not_one_of_them(
        self, site: "parzzley.fs.TSiteInput|None" = None
    ) -> None:
        """
        Mark all lastly involved sites as having changed (see :py:meth:`mark_changed`) if the given site is not one of
        them.

        This prevents data loss in some situations and will eventually lead to conflicts instead.

        :param site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def mark_refresh_needed(self, site: "parzzley.fs.TSiteInput|None" = None) -> None:
        """
        Mark this site as definitely outdated. In some way this is the opposite to :py:meth:`mark_changed`. This is only
        used in some special contexts and not part of the basic mechanism.

        :param site: For which site? Default is the event's current site.
        """


class DetermineMasterSiteTable(_EventAfterMasterSiteDetermined, _WithMasterSiteTableSetter, abc.ABC):
    """
    Occurs after changes were detected, in order to determine the master site for the current item stream. This is the
    site where the other sites will get updated from (regarding the current stream).

    This event should solely be handled in Parzzley infrastructure aspects, not in custom ones!

    It happens after :py:class:`DetectChanges` and before :py:class:`MasterSiteDetermined`. This is all part of the
    stream preparation.

    The typical implementation determines that based on the information gathered in :py:class:`DetectChanges`.
    """

    @abc.abstractmethod
    def is_site_marked_as_changed(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> bool:
        """
        Return whether this site was marked as changed (usually by :py:meth:`DetectChanges.mark_changed`).

        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def is_site_marked_as_needing_refreshed(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> bool:
        """
        Return whether this site was marked as needing to get refreshed (usually by
        :py:meth:`DetectChanges.mark_refresh_needed`).

        :param for_site: For which site? Default is the event's current site.
        """


class MasterSiteDetermined(_EventAfterMasterSiteDetermined, _item_events._WithSetItemInfo, abc.ABC):
    """
    Occurs after the master site for the current item stream was determined.

    It happens after :py:class:`DetermineMasterSiteTable` and before stream conflict handling. This is all part of the
    stream preparation.

    A handler may apply local changes to the item. If it does, :py:meth:`set_item_info` must be called afterward.
    """


class CollectSourceStreamables(
    _EventAfterMasterSiteDetermined,
    _WithStreamCookie,
    _WithSourceStreamableGetters,
    _item_events._WithWorkingItems,
    abc.ABC,
):
    """
    Occurs in order to collect read-streamable objects for the current item stream.

    See :py:meth:`set_source_streamable`.

    It occurs as a step of the stream preparation, after :py:class:`MasterSiteDetermined` and before conflict
    handling.

    The typical implementation directly gets the source streamable from the site. For some streams, there may be
    additional aspects that do further things, e.g. adding stream pipes for some arbitrary stream translations.
    """

    class Pipe(parzzley.fs.stream.ReadStreamable, abc.ABC):
        """
        An abstract pipe.

        Pipes are used by the stream update process as a mechanism to apply changes to the stream while it is
        transferring from the source to the destinations.

        In order to implement a new pipe, see also :py:class:`CollectSourceStreamables.FullContentPipe`.
        """

        class _ReadStream(parzzley.fs.stream.ReadStream):

            def __init__(self, inner_streamable: "parzzley.fs.stream.ReadStreamable", pipe_func):
                self.__inner_streamable = inner_streamable
                self.__inner_stream = None
                self.__inner_stream_context = None
                self.__pipe_func = pipe_func
                self.__ended = False

            async def __aenter__(self):
                self.__inner_stream_context = self.__inner_streamable.stream()
                self.__inner_stream = await self.__inner_stream_context.__aenter__()

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await self.__inner_stream_context.__aexit__(exc_type, exc_val, exc_tb)
                self.__inner_stream = None
                self.__inner_stream_context = None

            async def read(self, max_len):
                if self.__ended:
                    return None
                data = await self.__inner_stream.read(max_len)
                if data is None:
                    self.__ended = True
                data = await self.__pipe_func(data)
                if data is None:
                    self.__ended = True
                return data

        def __init__(self, inner_streamable: "parzzley.fs.stream.ReadStreamable"):
            self.__inner_streamable = inner_streamable

        @abc.abstractmethod
        async def pipe(self, data: bytes | None) -> bytes | None:
            """
            Receive and process a chunk of data and return a processed chunk of data (return :code:`None` to signal the
            end).

            If a pipe just returns the original data (:code:`return data`), this pipe would be a no-op.

            :param data: The chunk of source data. This is :code:`None` at the end of the stream.
            """

        async def _stream(self):
            return self._ReadStream(self.__inner_streamable, self.pipe)

    class FullContentPipe(Pipe, abc.ABC):
        """
        An abstract pipe that operates on the full content of a stream as a single chunk of data.

        This makes some transformation tasks a lot easier, but it requires to keep the full content in memory. It can
        only be used for streams that never exceed reasonable length limits.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__content = b""

        async def pipe(self, data):
            if self.__content is None:
                return None
            if data is not None:
                self.__content += data
                return b""
            content = self.__content
            self.__content = None
            return await self.pipe_content(content)

        @abc.abstractmethod
        async def pipe_content(self, data: bytes) -> bytes:
            """
            Receive and process the full content of a stream and return the processed content.

            :param data: The stream's entire content.
            """

    @abc.abstractmethod
    def set_source_streamable(
        self, source_streamable: "parzzley.fs.stream.ReadStreamable", *, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> None:
        """
        Set the source streamable. This usually happens for the stream master site.

        :param source_streamable: The source streamable.
        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def add_stream_pipe(self, pipe: type[Pipe], *, for_site: "parzzley.fs.TSiteInput|None" = None) -> None:
        """
        Add a pipe. Each pipe can apply changes to the stream while it is transferring from the source to the
        destinations.

        :param pipe: The pipe to add.
        :param for_site: For which site? Default is the event's current site.
        """


class DetermineConflicts(_EventAfterMasterSiteDetermined, _WithStreamCookie, _WithSourceStreamableGetters, abc.ABC):
    """
    Occurs in order to find conflicts for the current item stream.

    See :py:meth:`add_conflict` and :py:meth:`changed_dangerously_late`.

    This is part of the stream preparation, after the stream's master site is determined and source streamables are
    collected. If it detects any conflicts, there will be a chance to get them resolved by
    :py:class:`TryResolveConflicts` and :py:class:`ApplyConflictResolution`. If there will be unresolved conflicts
    afterward, most of the further item processing gets skipped, and the next event will be
    :py:class:`parzzley.sync.aspect.events.item.SkipDueToConflicts`. Otherwise, the actual stream update will begin.
    """

    @dataclasses.dataclass
    class _Conflict:
        description: str
        details: str | None

    @property
    @abc.abstractmethod
    def conflicts(self) -> t.Iterable[_Conflict]:
        """
        All conflicts found by this event so far.
        """

    @abc.abstractmethod
    def changed_dangerously_late(self, for_site: "parzzley.fs.TSiteInput|None" = None) -> bool:
        """
        Returns whether this site has seen changes late enough to be potentially in conflict with something.

        Precisely, it returns whether the content version number (see :py:meth:`content_version`) of this site is at
        least as larget as the one from the elected master site.

        This always indicates a potential conflict, because there might be a change on the given site as well, which
        would be lost once the master site actually updates all the other sites.

        :param for_site: For which site? Default is the event's current site. For the master site, it will by nature
                         always return :code:`True`.
        """

    @abc.abstractmethod
    def add_conflict(self, description: str, details: str | None = None) -> None:
        """
        Add a conflict.

        :param description: The conflict description.
        :param details: Conflict details.
        """


class TryResolveConflicts(_EventAfterMasterSiteDetermined, abc.ABC):
    """
    Occurs in order to try to resolve conflicts found by :py:class:`DetermineConflicts`.

    See :py:meth:`conflicts` and :py:meth:`resolve_conflicts`.
    """

    @abc.abstractmethod
    def resolve_conflicts(self, master_site: "parzzley.fs.TSiteInput") -> None:
        """
        Resolve all conflicts.

        :param master_site: The new stream master site.
        """

    @property
    @abc.abstractmethod
    def conflicts(self) -> t.Iterable[DetermineConflicts._Conflict]:
        """
        All conflicts.
        """


class ApplyConflictResolution(_EventAfterMasterSiteDetermined, _WithMasterSiteTableSetter, abc.ABC):
    """
    Occurs in order to apply the resolution determined by :py:class:`TryResolveConflicts`.

    This event should solely be handled in Parzzley infrastructure aspects, not in custom ones!

    See :py:meth:`conflicts` and :py:meth:`resolve_conflicts`.

    The typical implementation applies the resolution from :py:class:`TryResolveConflicts`.
    """

    @property
    @abc.abstractmethod
    def conflict_resolution(self) -> str | None:
        """
        The name of the new stream master site if the conflicts were resolved successfully, otherwise :code:`None`.
        """

    @property
    @abc.abstractmethod
    def conflicts(self) -> t.Iterable[DetermineConflicts._Conflict]:
        """
        All conflicts.
        """

    @abc.abstractmethod
    def remove_conflict(self, conflict: DetermineConflicts._Conflict) -> None:
        """
        Remove a conflict.

        :param conflict: The conflict to remove.
        """


class CollectDestinationStreamables(
    _EventAfterMasterSiteDetermined,
    _WithStreamCookie,
    _WithDestinationStreamableGetters,
    _item_events._WithWorkingItems,
    abc.ABC,
):
    """
    Occurs in order to collect write-streamable objects for the current item stream.

    See :py:meth:`add_destination_streamable` and :py:meth:`working_items`.

    It occurs as step of the stream update procedure, after
    :py:class:`parzzley.sync.aspect.events.item.SetUpWorkingItems` was triggered and before :py:class:`TransferUpdate`.

    A typical implementation would, for the main stream, check if the current site would actually need an update from
    the master site (i.e. its main stream has actually been changed). If not, it would do nothing. If so, it would at
    first make sure that either a temporary working item is in place for this item on this site (see
    :py:class:`parzzley.sync.aspect.events.item.SetUpWorkingItems`), or the original location is at least part of all
    working items. Then it just adds one destination streamable per working items. For the other streams, it would do
    nearly the same, but if there is a temporary working item, it will definitely pass its check and do its setup,
    even if the stream content did not change (the temporary working item will later replace the original, so every
    stream must be transferred to it).
    """

    @abc.abstractmethod
    def add_destination_streamable(self, destination_streamable: "parzzley.fs.stream.WriteStreamable") -> None:
        """
        Add a destination streamable. This usually happens for each site but the stream master site.

        :param destination_streamable: The destination streamable to add.
        """

    @abc.abstractmethod
    def disable_change_detection(self) -> None:
        """
        Disable the change detection (that would do a retry if the source changes during transfer).
        """


class TransferUpdate(
    _EventAfterMasterSiteDetermined,
    _WithStreamCookie,
    _WithSourceStreamableGetters,
    _WithDestinationStreamableGetters,
    abc.ABC,
):
    """
    Occurs in order to update the current item stream.

    Event handlers should not make visible changes here but keep it back until
    :py:class:`parzzley.sync.aspect.events.item.ApplyUpdate`. You also have to set the new item info there!

    It is the main part of the stream update routine, happening after :py:class:`CollectDestinationStreamables` and
    before :py:class:`parzzley.sync.aspect.events.item.ApplyUpdate` (and before per-directory processing happens if the
    current item is a directory).
    """

    @abc.abstractmethod
    def is_change_detection_disabled(self) -> bool:
        """
        Return whether the change detection (that would do a retry if the source changes during transfer) was disabled.
        """
