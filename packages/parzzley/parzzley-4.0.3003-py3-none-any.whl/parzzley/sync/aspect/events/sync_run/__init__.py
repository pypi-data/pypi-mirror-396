#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Sync run events. See also :py:mod:`parzzley.sync.aspect.events`.

These events usually occur (at most) once for each sync run.
"""
import abc
import typing as t

import parzzley.sync.aspect.events as _events
import parzzley.sync.logger

if t.TYPE_CHECKING:
    import parzzley.sync.run


class _Event(_events._Event, abc.ABC):
    """
    Base class for an aspect event on an entire :py:class:`parzzley.sync.run.SyncRun`.
    """

    @property
    @abc.abstractmethod
    def log(self) -> parzzley.sync.logger.Logger:
        """
        The logger.
        """

    @property
    @abc.abstractmethod
    def sync_run(self) -> "parzzley.sync.run.SyncRun":
        """
        The current sync run.
        """

    @property
    @abc.abstractmethod
    def all_sites(self) -> t.Iterable["parzzley.fs.Site"]:
        """
        All sites involved in the current sync run.
        """

    @abc.abstractmethod
    def mark_effective(self) -> None:
        """
        Mark the current sync run as effective.

        This should be called whenever it had any (potential) effect.
        The client can e.g. check if it makes sense to sync other sites as well (because they would get these changes
        then as well).
        """


class Prepare(_Event, abc.ABC):
    """
    Occurs at the beginning of a sync run, before :py:class:`DetermineStreamSupport`.

    Aspects can listen to that event in order to do arbitrary initialization steps, e.g. for data structures used in
    later events.
    """

    @abc.abstractmethod
    async def remove_site_from_items_books(self, site: "parzzley.fs.TSiteInput") -> None:
        """
        Remove a site from the items books, so it will be considered as never seen before.

        Do not use. It is typically used by infrastructure.
        """


class DetermineStreamSupport(_Event, abc.ABC):
    """
    Occurs in order to determine which item streams are supported (and for which item types) for the current site.

    See :py:meth:`set_stream_support`.

    It occurs at the beginning of a sync run, after :py:class:`Prepare`. There will be
    :py:class:`ValidateStreamSupport` occurring afterward, in order to turn the per-site stream support info into a
    general one (all later steps will only use the general one).
    """

    @abc.abstractmethod
    def set_stream_support(
        self,
        stream_name: str,
        item_types: t.Iterable["parzzley.fs.ItemType"],
        *,
        for_site: "parzzley.fs.TSiteInput|None" = None,
        cookies_are_move_stable: bool = False
    ) -> None:
        """
        Declare that this site supports the given stream for the given item types.

        :param stream_name: The name of the supported stream.
        :param item_types: The exact list of item types supported for this stream.
        :param for_site: For which site? Default is the event's current site.
        :param cookies_are_move_stable: Whether the cookie stays the same when an item gets moved.
        """


class ValidateStreamSupport(_Event, abc.ABC):
    """
    Occurs in order to check if the stream support determined by :py:class:`DetermineStreamSupport` is valid and to
    derive global stream support info from the per-site stream support info determined there.

    This event should solely be handled in Parzzley infrastructure aspects, not in custom ones!

    Handlers raise an exception if there are problems with the determined stream support, e.g. if there are fatal
    conflicts between the sites.

    See :py:meth:`determined_supported_streams`, :py:meth:`supported_item_types` and
    :py:meth:`set_final_stream_support`.

    It occurs at the beginning of a sync run, after :py:class:`DetermineStreamSupport` and before the (per-item;
    recursive) processing of the root directory.

    :py:class:`parzzley.builtin.aspects.streaming.GlobalStreamSupport` is the typical implementation.
    It checks if all sites have determined the same supported streams (with the same item types). It will then take this
    as the global result or will fail otherwise.
    """

    @abc.abstractmethod
    def determined_supported_streams(self, *, for_site: "parzzley.fs.TSiteInput|None" = None) -> t.Iterable[str]:
        """
        Return the streams supported by the current site, as determined by :py:class:`DetermineStreamSupport`.

        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def supported_item_types(
        self, stream_name: str, *, for_site: "parzzley.fs.TSiteInput|None" = None
    ) -> t.Iterable[parzzley.fs.ItemType]:
        """
        Return the item types supported by the current site for the given stream, as determined by
        :py:class:`DetermineStreamSupport`.

        :param stream_name: The name of the supported stream.
        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def cookies_are_move_stable(self, stream_name: str, *, for_site: "parzzley.fs.TSiteInput|None" = None) -> bool:
        """
        Return whether cookies are move-stable on the current site for the given stream, as determined by
        :py:class:`DetermineStreamSupport`.

        :param stream_name: The name of the supported stream.
        :param for_site: For which site? Default is the event's current site.
        """

    @abc.abstractmethod
    def set_final_stream_support(
        self, stream_name: str, item_types: t.Iterable["parzzley.fs.ItemType"], cookies_are_move_stable: bool
    ) -> None:
        """
        Declare that the current sites support the given stream for the given item types.

        :param stream_name: The name of the supported stream.
        :param item_types: The exact list of item types supported for this stream.
        :param cookies_are_move_stable: Whether the cookie stays the same when an item gets moved.
        """


class _EventAfterStreamSupportDetermined(_Event, abc.ABC):
    """
    Base class for an aspect event after the stream support has been determined.
    """

    class StreamSupportInfo(abc.ABC):
        """
        Information about the stream support.
        """

        @property
        @abc.abstractmethod
        def supported_streams(self) -> t.Sequence[str]:
            """
            Names of all supported streams.
            """

        @abc.abstractmethod
        def supported_item_types(self, stream_name: str) -> t.Sequence[parzzley.fs.ItemType]:
            """
            Return the item types supported by the given stream.

            :param stream_name: The name of the supported stream.
            """

        @abc.abstractmethod
        def cookies_are_move_stable(self, stream_name: str) -> bool:
            """
            Return whether the cookies for the given stream are move-stable.

            :param stream_name: The name of the supported stream.
            """

    @property
    @abc.abstractmethod
    def stream_support_info(self) -> StreamSupportInfo:
        """
        Information about the stream support.

        Determined by :py:class:`ValidateStreamSupport`.
        """


class Finish(_Event, abc.ABC):
    """
    Occurs at the end of a successful sync run, after the processing of the root directory, before :py:class:`Close`.
    """


class Close(_Event, abc.ABC):
    """
    Occurs at the end of a sync run (after :py:class:`Finish`), no matter if successful or not.
    """

    @property
    @abc.abstractmethod
    def error(self) -> Exception | None:
        """
        Critical error that aborted the sync run prematurely (or :code:`None`).
        """
