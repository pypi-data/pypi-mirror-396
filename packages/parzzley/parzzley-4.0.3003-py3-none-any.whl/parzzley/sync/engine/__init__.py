#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
The Parzzley engine. See :py:class:`Engine`. Used internally by other parts of the API (:py:mod:`parzzley.sync`).

Subpackages are used internally by the engine.
"""
import abc
import ast
import asyncio
import contextlib
import dataclasses
import logging
import threading
import traceback
import typing as t

import parzzley.sync.aspect.events
import parzzley.sync.control
import parzzley.sync.engine.event_runner
import parzzley.sync.engine.events_impl
import parzzley.sync.logger
import parzzley.sync.run
import parzzley.sync.utils


_logger = logging.getLogger(__name__)


class Engine:
    """
    The Parzzley engine executes a sync run on a volume.

    At first, it collects all the aspects that are defined for each site or for the entire volume (i.e. for all sites).
    Then it runs the volume synchronization by triggering a sequence of events (see
    :py:mod:`parzzley.sync.aspect.events`). The engine itself has no own logic beyond that. All the actual work is done
    by the event handlers provided by the defined aspects.
    """

    def __init__(
        self,
        *,
        sync_run: "parzzley.sync.run.SyncRun",
        sites: dict[parzzley.fs.Site, parzzley.fs.SiteContextManager],
        loggings: t.Iterable[parzzley.sync.logger.Logging],
    ):
        """
        Do not use directly.

        :param sync_run: The sync run.
        :param sites: The connected sites.
        """
        super().__init__()
        self.__sync_control = Engine._SyncControl(sync_run.id)
        self.__sync_run = sync_run
        self.__items_books = {}
        self.__sites = dict(sites)
        self.__loggings = tuple(loggings)
        self.__had_critical_problems = False
        self.__event_runner = parzzley.sync.engine.event_runner.Runner(
            {site: sync_run.aspects(site.name) for site in sync_run.sites}
        )

    @property
    def sync_control(self) -> "parzzley.sync.control.SyncControl":
        """
        The sync control.
        """
        return self.__sync_control

    def start(self) -> None:
        """
        Start the engine.

        This method must not be called more than once per instance.
        """
        threading.Thread(name=f"parzzley sync {self.__sync_run.id}", target=asyncio.run, args=(self._exec(),)).start()

    async def _exec(self) -> None:
        sync_run_event = parzzley.sync.engine.events_impl.sync_run_event(self.__sync_run, self.__items_books)
        try:
            await self.__sync(sync_run_event)
        finally:
            # the final steps run in a new thread, so they are safe from asyncio.CancelledError.
            parzzley.sync.utils.run_coroutine_in_new_thread(
                self.__exec__post(sync_run_event), thread_name_postfix="post"
            )

    async def __exec__post(self, sync_run_event) -> None:
        try:
            site_shutdown_successful = True
            for site_context_manager in self.__sites.values():
                try:
                    await site_context_manager.__aexit__(None, None, None)
                except Exception:  # pylint: disable=broad-exception-caught
                    _logger.error(traceback.format_exc())
                    site_shutdown_successful = False
            if not site_shutdown_successful:
                raise RuntimeError("there were errors while shutting down sites")

            await self.__sync_run.store_success_info(self.__sites)

        finally:
            all_log_entries = sync_run_event.all_log_entries
            for logging_ in self.__loggings:
                logging_.emit(self.__sync_run, all_log_entries)
            self.__sync_control.set_finished(
                was_successful=not self.__had_critical_problems, was_effective=sync_run_event.was_effective
            )

    async def __sync(self, sync_run_event) -> None:
        with self.__catch_exceptions(sync_run_event, "due to internal engine problems"):
            sync_run_label = f"#{self.__sync_run.sn} for {self.__sync_run.volume_name}"
            _logger.info("Starting sync run %s with sites %s", sync_run_label, ", ".join(_.name for _ in self.__sites))
            await self.__prepare_items_book()

            try:
                with self.__catch_exceptions(sync_run_event, "due to problems"):
                    await self.__event_runner.run_event(parzzley.sync.aspect.events.sync_run.Prepare, sync_run_event)
                    await self.__event_runner.run_event(
                        parzzley.sync.aspect.events.sync_run.DetermineStreamSupport, sync_run_event
                    )
                    await self.__event_runner.run_event(
                        parzzley.sync.aspect.events.sync_run.ValidateStreamSupport, sync_run_event
                    )
                    await self.__sync_item(parzzley.fs.item(b""), sync_run_event)
                    await self.__event_runner.run_event(parzzley.sync.aspect.events.sync_run.Finish, sync_run_event)

            finally:
                # the final steps run in a new thread, so they are safe from asyncio.CancelledError.
                parzzley.sync.utils.run_coroutine_in_new_thread(
                    self.__sync__post(sync_run_event, sync_run_label), thread_name_postfix="post"
                )

    async def __sync__post(self, sync_run_event, sync_run_label):
        with self.__catch_exceptions(sync_run_event, "due to problems while closing"):
            await self.__event_runner.run_event(parzzley.sync.aspect.events.sync_run.Close, sync_run_event)

        if self.__had_critical_problems:
            self.__fall_back_items_book()
        await self.__store_items_book()

        _logger.info("Finished sync run %s", sync_run_label)

    async def __sync_item(self, item: parzzley.fs.Item, sync_run_event) -> None:
        self.__check_canceled()

        while True:
            item_event = sync_run_event.to_item_event(item)

            await self.__event_runner.run_event(parzzley.sync.aspect.events.item.DecideToSkip, item_event)
            if item_event.is_item_marked_to_skip_permanently:
                return

            if not item_event.is_item_marked_to_skip:
                await self.__sync_item__collect_info_and_determine_master_sites_for_streams(item_event)
                await self.__sync_item__source_streamables(item_event)
                await self.__sync_item__conflicts(item_event)
                if item_event.all_conflicts:
                    await self.__sync_item__skipped_by_conflicts(item_event)
                    conflict_str_list = []
                    for conflict in item_event.all_conflicts:
                        conflict_str = (
                            f"{conflict.description}. "
                            f"({conflict.stream_name or "main"}"
                            f"{f"; {conflict.details}" if conflict.details else ""})"
                        )
                        if conflict_str not in conflict_str_list:
                            conflict_str_list.append(conflict_str)
                    item_event.log.warning("Skipped due to conflict: %s", ", ".join(conflict_str_list))
                else:
                    await self.__sync_item__update_streams(item_event)
                    await self.__sync_item__populate_items_book(item_event)
                    if item_event.item_type(item_event.master_site) == parzzley.fs.ItemType.DIRECTORY:
                        await self.__sync_item__directory(item_event)

            if not item_event.is_marked_full_retry_needed:

                # TODO either put that in an aspect, or have more infrastructure-like things in the engine as well?
                if not item_event.is_item_marked_to_skip and not item_event.all_conflicts:
                    self.__items_books[None].mark_successfully_synced(item)
                else:
                    self.__items_books[None].mark_skipped_now(item)

                break

    async def __sync_item__collect_info_and_determine_master_sites_for_streams(
        self, item_event: "parzzley.sync.engine.events_impl.ItemEvent"
    ) -> None:
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.Prepare, item_event)
        for stream_name in item_event.stream_support_info.supported_streams:
            stream_event = item_event.to_stream_event(stream_name)

            await self.__event_runner.run_event(
                parzzley.sync.aspect.events.item.stream.DetermineComparator, stream_event
            )
            await self.__event_runner.run_event(parzzley.sync.aspect.events.item.stream.DetermineCookie, stream_event)
            if stream_name == "":
                await self.__event_runner.run_event(parzzley.sync.aspect.events.item.DetermineType, stream_event)
            await self.__event_runner.run_event(parzzley.sync.aspect.events.item.stream.DetectChanges, stream_event)
            await self.__event_runner.run_event(
                parzzley.sync.aspect.events.item.stream.DetermineMasterSiteTable, stream_event
            )
            await self.__event_runner.run_event(
                parzzley.sync.aspect.events.item.stream.MasterSiteDetermined, stream_event
            )

            self.__check_canceled()

    async def __sync_item__source_streamables(self, item_event: "parzzley.sync.engine.events_impl.ItemEvent") -> None:
        for stream_name in item_event.stream_support_info.supported_streams:
            stream_event = item_event.to_stream_event(stream_name)
            await self.__event_runner.run_event(
                parzzley.sync.aspect.events.item.stream.CollectSourceStreamables, stream_event
            )

    async def __sync_item__conflicts(self, item_event: "parzzley.sync.engine.events_impl.ItemEvent") -> None:
        for stream_name in item_event.stream_support_info.supported_streams:
            stream_event = item_event.to_stream_event(stream_name)

            await self.__event_runner.run_event(
                parzzley.sync.aspect.events.item.stream.DetermineConflicts, stream_event
            )

            if stream_event.conflicts:
                stream_event.log.debug("Found conflicts")
                await self.__event_runner.run_event(
                    parzzley.sync.aspect.events.item.stream.TryResolveConflicts, stream_event
                )
                await self.__event_runner.run_event(
                    parzzley.sync.aspect.events.item.stream.ApplyConflictResolution, stream_event
                )

            self.__check_canceled()

        item_event.set_all_conflicts(
            [
                parzzley.sync.aspect.events.item.SkipDueToConflicts._Conflict(
                    stream_name, conflict.description, conflict.details
                )
                for stream_name in item_event.stream_support_info.supported_streams
                for conflict in item_event.to_stream_event(stream_name).conflicts
            ]
        )

    async def __sync_item__skipped_by_conflicts(self, item_event: "parzzley.sync.engine.events_impl.ItemEvent") -> None:
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.SkipDueToConflicts, item_event)

    async def __sync_item__update_streams(self, item_event: "parzzley.sync.engine.events_impl.ItemEvent") -> None:
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.PrepareUpdating, item_event)
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.SetUpWorkingItems, item_event)

        for stream_name in item_event.stream_support_info.supported_streams:
            stream_event = item_event.to_stream_event(stream_name)
            await self.__event_runner.run_event(
                parzzley.sync.aspect.events.item.stream.CollectDestinationStreamables, stream_event
            )
            await self.__event_runner.run_event(parzzley.sync.aspect.events.item.stream.TransferUpdate, stream_event)

        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.ApplyUpdate, item_event)

    async def __sync_item__directory(self, item_event) -> None:
        dir_event = item_event.to_dir_event()
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.dir.Prepare, dir_event)
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.dir.List, dir_event)
        for child_item in [dir_event.item(child_name) for child_name in sorted(dir_event.child_names)]:
            await self.__sync_item(child_item, item_event)
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.dir.Iterated, dir_event)

    async def __sync_item__populate_items_book(self, item_event: "parzzley.sync.engine.events_impl.ItemEvent") -> None:
        await self.__event_runner.run_event(parzzley.sync.aspect.events.item.RefreshItemsBook, item_event)

    async def __prepare_items_book(self) -> None:
        items_books_variable = self.__items_books_variable()
        for site_name, items_book_data in [
            (site.name, await items_books_variable.value(key=site.name)) for site in self.__sync_run.sites
        ]:
            self.__items_books[site_name] = _PerSiteItemsBook.from_serializable_data(
                items_book_data, self.__sync_run.sn
            )
        self.__items_books[None] = _GlobalItemsBook.from_serializable_data(
            await items_books_variable.value(key=""), self.__sync_run.sn, (_.name for _ in self.__sites)
        )

    def __fall_back_items_book(self) -> None:
        for items_book in self.__items_books.values():
            items_book.take_last_item_book_entries_as_fallback()

    async def __store_items_book(self) -> None:
        items_books_variable = self.__items_books_variable()
        for site in self.__sync_run.sites:
            await items_books_variable.set_value(self.__items_books[site.name].to_serializable_data(), key=site.name)
        await items_books_variable.set_value(self.__items_books[None].to_serializable_data(), key="")

    def __items_books_variable(self):
        return self.__sync_run.volume_state_variable("items_books")

    @contextlib.contextmanager
    def __catch_exceptions(self, sync_run_event, crash_reason: str):
        try:
            yield
        except Exception as ex:  # pylint: disable=broad-exception-caught
            sync_run_event.set_error(ex)
            self.__had_critical_problems = True
            sync_run_event.log.fatal("The sync run has been canceled %s.\n%s", crash_reason, traceback.format_exc())

    def __check_canceled(self) -> None:
        if self.__sync_control.is_cancel_requested:
            self._cancel()

    def _cancel(self) -> None:
        raise self._Canceled()

    class _Canceled(BaseException):
        pass

    class _SyncControl(parzzley.sync.control.SyncControl):

        def __init__(self, sync_run_id: str):
            super().__init__()
            self.__sync_run_id = sync_run_id
            self.__was_successful = None
            self.__was_effective = False
            self.__lock = threading.Lock()
            self.__finished_condition = threading.Condition(self.__lock)

        def set_finished(self, *, was_successful: bool, was_effective: bool):
            """
            Mark the sync run associated to this control as finished.

            :param was_successful: Whether the sync run was successful.
            :param was_effective: Whether the sync run was effective (see :py:attr:`was_effective`).
            """
            with self.__lock:
                self.__was_successful = was_successful
                self.__was_effective = was_effective
                self.__finished_condition.notify_all()

        @property
        def sync_run_id(self):
            return self.__sync_run_id

        @property
        def is_finished(self):
            return self.__was_successful is not None

        @property
        def was_successful(self):
            return self.__was_successful is True

        @property
        def was_effective(self):
            return self.__was_effective

        def wait_finished(self):
            with self.__lock:
                while not self.is_finished:
                    self.__finished_condition.wait()


class _ItemsBookBase[ItemInfoT](abc.ABC):

    def __init__(self, after_last_sync_item_data: dict[bytes, ItemInfoT]):
        self._after_last_sync_item_data = after_last_sync_item_data
        self._latest_item_data: dict[bytes, ItemInfoT] = {}

    @classmethod
    def from_serializable_data(cls, data: t.Iterable | None, *args) -> t.Self:
        """
        Return an items book from serializable data. See also :py:meth:`to_serializable_data`.

        :param data: Serializable items book data.
        :param args: Additional constructor arguments.
        """
        if data is None:
            state_data, per_item_data = None, []
        else:
            state_data, *per_item_data = data

        return cls(
            {
                ast.literal_eval(item_path): cls._item_info_from_serializable_data(data_)
                for item_path, *data_ in per_item_data
            },
            *args,
            *cls._state_args_from_serializable_data(state_data),
        )

    def to_serializable_data(self) -> t.Sequence[t.Any]:
        """
        Return serializable data for this items book. See also :py:meth:`from_serializable_data`.
        """
        data = [self._state_args_to_serializable_data()]
        for item_path, item_info in self._latest_item_data.items():
            data.append((repr(item_path), *self._item_info_to_serializable_data(item_info)))
        return data

    @classmethod
    @abc.abstractmethod
    def _item_info_from_serializable_data(cls, data: t.Sequence[t.Any]) -> ItemInfoT:
        """
        Return an item info for the given serializable data (as returned by :py:meth:`_item_info_to_serializable_data`).

        :param data: Serializable data.
        """

    @classmethod
    @abc.abstractmethod
    def _item_info_to_serializable_data(cls, item_info: ItemInfoT) -> t.Iterable[t.Any]:
        """
        Return serializable data for a given item info (as interpreted by :py:meth:`_item_info_from_serializable_data`).

        :param item_info: The item info.
        """

    @classmethod
    def _state_args_from_serializable_data(cls, data: t.Sequence[t.Any]) -> t.Iterable[t.Any]:
        """
        Return additional state arguments for the given serializable data (as returned by
        :py:meth:`_state_args_to_serializable_data`).

        :param data: Serializable data.
        """
        # pylint: disable=unused-argument
        return ()

    def _state_args_to_serializable_data(self) -> t.Any:
        """
        Return serializable data for additional state arguments (as interpreted by
        :py:meth:`_state_args_from_serializable_data`).
        """
        return None

    def take_last_item_book_entries_as_fallback(self) -> None:
        """
        Take the item book entries from last time for any item that has not got a new info so far.

        This method is to be used when a sync run got aborted for some reason, so we do not lose information for not
        seen items.
        """
        for old_path, old_item_info in self._after_last_sync_item_data.items():
            if old_path not in self._latest_item_data:
                self._latest_item_data[old_path] = old_item_info


class _GlobalItemsBook(_ItemsBookBase["_GlobalItemsBook._ItemInfo"]):

    def __init__(
        self,
        after_last_sync_item_data: dict[str, "_GlobalItemsBook._ItemInfo"],
        sync_run_no: int,
        connected_site_names: t.Iterable[str],
        connected_site_names_by_sync_run_no: dict[int, t.Sequence[str]],
    ):
        super().__init__(after_last_sync_item_data)
        self.__sync_run_no = sync_run_no

        all_used_sync_run_nos = set(_.last_successful_sync_run_no for _ in self._after_last_sync_item_data.values())
        connected_site_names_by_sync_run_no = {
            k: v for k, v in connected_site_names_by_sync_run_no.items() if k in all_used_sync_run_nos
        }

        self.__connected_site_names_by_sync_run_no = {
            **connected_site_names_by_sync_run_no,
            sync_run_no: tuple(connected_site_names),
        }

    def mark_successfully_synced(self, item: parzzley.fs.TItemInput) -> None:
        """
        Mark the given item as successfully synchronized in this sync run.

        :param item: The item to mark.
        """
        item = parzzley.fs.item(item)
        self._latest_item_data[item.path] = _GlobalItemsBook._ItemInfo(self.__sync_run_no)

    def mark_skipped_now(self, item: parzzley.fs.TItemInput) -> None:
        """
        Mark the given item as skipped now.

        :param item: The item to mark.
        """
        item_path = parzzley.fs.item(item).path

        for old_path, old_item_info in self._after_last_sync_item_data.items():
            if item_path == b"" or old_path == item_path or old_path.startswith(item_path + b"/"):
                self._latest_item_data[old_path] = old_item_info

    def last_successful_sync_no(self, item: parzzley.fs.TItemInput) -> int | None:
        """
        Return the serial number of the sync run that has successfully synced the given item last time (or :code:`None`
        if it was not successfully synced yet).

        :param item: The item.
        """
        if item_info := self._after_last_sync_item_data.get(parzzley.fs.item(item).path):
            return item_info.last_successful_sync_run_no
        return None

    def sites_involved_in_sync_no(self, sync_run_no: int) -> t.Sequence[str]:
        """
        Return the names of the sites that were involved in a given sync run.

        This must be one of the serial numbers returned by :py:meth:`last_successful_sync_no`.

        :param sync_run_no: The serial number of the sync run.
        """
        return self.__connected_site_names_by_sync_run_no.get(sync_run_no) or ()

    @classmethod
    def _item_info_to_serializable_data(cls, item_info):
        return (item_info.last_successful_sync_run_no,)

    @classmethod
    def _item_info_from_serializable_data(cls, data):
        (last_successful_sync_run_no,) = data
        return _GlobalItemsBook._ItemInfo(last_successful_sync_run_no)

    def _state_args_to_serializable_data(self):
        return (self.__connected_site_names_by_sync_run_no,)

    @classmethod
    def _state_args_from_serializable_data(cls, data):
        (last_successful_sync_run_no,) = data or ({},)
        last_successful_sync_run_no = {int(k): v for k, v in last_successful_sync_run_no.items()}
        return (last_successful_sync_run_no,)

    @dataclasses.dataclass
    class _ItemInfo:
        last_successful_sync_run_no: int


class _PerSiteItemsBook(_ItemsBookBase["_PerSiteItemsBook._ItemInfo"]):
    """
    A per-site items book stores site-specific state info about each item.

    Data gets stored by means of :py:meth:`store_item_info` as soon as a sync run has finished an item (actual
    persistence will only happen at the end of the sync run, though).

    After that, you can look up an item's last type and last stream cookies for each site (assuming there is one items
    book per site), and also the serial number of the sync run that has done the last successful sync on it.
    """

    def __init__(self, after_last_sync_item_data: dict[str, "_PerSiteItemsBook._ItemInfo"], sync_run_no: int):
        super().__init__(after_last_sync_item_data)
        self.__sync_run_no = sync_run_no

    def item_type_after_last_sync(self, item: parzzley.fs.TItemInput) -> "parzzley.fs.ItemType":
        """
        Return the item type that a given item had lastly.

        :param item: The item location.
        """
        item_data = self._after_last_sync_item_data.get(parzzley.fs.item(item).path)
        return item_data.item_type if item_data else parzzley.fs.ItemType.NONE

    def stream_cookie_after_last_sync(self, item: parzzley.fs.TItemInput, stream_name: str) -> t.Any:
        """
        Return the cookie that a given stream of a given item had lastly.

        :param item: The item location.
        :param stream_name: The stream name.
        """
        item_data = self._after_last_sync_item_data.get(parzzley.fs.item(item).path)
        return item_data.streams.get(stream_name) if item_data else None

    def last_change_run_sn(self, item: parzzley.fs.TItemInput) -> int:
        """
        Return the serial number of the sync run that has seen the last change on this site (or :code:`0` if that never
        happened).

        :param item: The item location.
        """
        item_data = self._after_last_sync_item_data.get(parzzley.fs.item(item).path)
        if item_data:
            return item_data.changed_in_sync_run_no
        return 0

    def store_item_info(
        self, item: parzzley.fs.TItemInput, item_type: parzzley.fs.ItemType, stream_cookies: dict[str, object]
    ) -> None:
        """
        Store item info.

        :param item: The item location.
        :param item_type: The item type.
        :param stream_cookies: The stream cookie for each stream.
        """
        item = parzzley.fs.item(item)
        self._latest_item_data[item.path] = self._ItemInfo(self.__sync_run_no, item_type, stream_cookies)

    @classmethod
    def _item_info_to_serializable_data(cls, item_info):
        streams = {}
        for stream_name, stream_cookie in item_info.streams.items():
            if stream_cookie:
                streams[stream_name] = stream_cookie

        return item_info.changed_in_sync_run_no, item_info.item_type.name, streams

    @classmethod
    def _item_info_from_serializable_data(cls, data):
        changed_in_sync_run_no, item_type_name, streams = data
        return _PerSiteItemsBook._ItemInfo(
            changed_in_sync_run_no,
            parzzley.fs.ItemType[item_type_name],
            {
                stream_name: parzzley.fs.Site.sanitized_cookie(stream_cookie)
                for stream_name, stream_cookie in streams.items()
            },
        )

    @dataclasses.dataclass
    class _ItemInfo:
        changed_in_sync_run_no: int
        item_type: "parzzley.fs.ItemType"
        streams: dict[str, object]
