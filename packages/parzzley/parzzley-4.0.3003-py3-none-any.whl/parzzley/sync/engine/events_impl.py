#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Implementation of :py:mod:`parzzley.sync.aspect.events` events, used by the engine.

Note: Instead of creating new event instances for each event type (and constantly moving data around), the engine works
with one instance for the entire sync run, and only sometimes derives specific event objects from that, in a much
coarser way than the events are originally defined. This simplifies engine implementation to a large degree.
"""
# pylint: disable=missing-function-docstring,too-many-ancestors,too-many-positional-arguments,too-many-public-methods
import copy
import json
import logging
import typing as t

import parzzley.sync.aspect.events
import parzzley.sync.logger
import parzzley.sync.run


_parzzley_sync_logger = logging.getLogger(parzzley.sync.__name__)


def sync_run_event(sync_run, items_books):
    """
    Create and return a new sync run event for a sync run.

    :param sync_run: The sync run to associate to this event.
    :param items_books: The items books used in this sync run.
    """
    return SyncRunEvent(None, sync_run, {}, items_books)


class SyncRunEvent(
    parzzley.sync.aspect.events.sync_run.DetermineStreamSupport,
    parzzley.sync.aspect.events.sync_run.ValidateStreamSupport,
    parzzley.sync.aspect.events.sync_run.Close,
    parzzley.sync.aspect.events.sync_run.Finish,
    parzzley.sync.aspect.events.sync_run.Prepare,
):
    """
    Implementation of all sync run events.
    """

    _DATA__STREAM_SUPPORT_PER_SITE = parzzley.sync.aspect.events.Data({}, per_site=True)
    _DATA__STREAM_SUPPORT = parzzley.sync.aspect.events.Data({})
    _DATA__LOG_ENTRIES = parzzley.sync.aspect.events.Data([])
    _DATA__EFFECTIVE = parzzley.sync.aspect.events.Data(False)

    def __init__(
        self,
        site: "parzzley.fs.Site|None",
        sync_run: "parzzley.sync.run.SyncRun",
        per_sync_run_data,
        items_books,
        logger: "_Logger|None" = None,
    ):
        super().__init__()
        self.__site = site
        self.__sync_run = sync_run
        self.__per_sync_run_data = per_sync_run_data
        self.__items_books = items_books
        self.__logger = logger or _Logger(self, None, None)

    @property
    def all_log_entries(self):
        return self._DATA__LOG_ENTRIES.get(self)

    @property
    def log(self):
        return self.__logger

    def to_item_event(self, item):
        return ItemEvent(self.site, self.sync_run, self._per_sync_run_data, self.__items_books, item, {})

    def to_event_for_site(self, site: "parzzley.fs.Site") -> "t.Self":
        new_event = copy.copy(self)
        new_event.__site = site  # pylint: disable=unused-private-member
        return new_event

    @property
    def site(self):
        return self.__site

    @property
    def sync_run(self):
        return self.__sync_run

    def _get_data(self, data_obj, per_site, per_item, per_stream, key_data, initial_value):
        event_data = self.__event_data_wrapper(
            data_obj, initial_value, per_site=per_site, per_item=per_item, per_stream=per_stream
        )
        return event_data.get(self, self.__data_key_data(key_data))

    def _set_data(self, data_obj, per_site, per_item, per_stream, key_data, value):
        event_data = self.__event_data_wrapper(data_obj, per_site=per_site, per_item=per_item, per_stream=per_stream)
        event_data.set(self, self.__data_key_data(key_data), value)

    def __event_data_wrapper(self, key, initial_value=None, *, per_site=False, per_item=False, per_stream=False):
        if per_stream:
            native_data_name = "_per_stream_data"
        elif per_item:
            native_data_name = "_per_item_data"
        else:
            native_data_name = "_per_sync_run_data"

        return self._EventData(key, initial_value, native_data_name, [*(["site"] if per_site else [])])

    def __data_key_data(self, key_data):
        result = self._data_key_data()
        if key_data:
            result.update(key_data)
        return result

    def _data_key_data(self):
        return {**({"site": self.site.name} if self.site else {})}

    def _data__for_site(self, for_site):
        return {"key_data": {"site": parzzley.fs.site_name(for_site or self.site)}}

    @property
    def _per_sync_run_data(self):
        return self.__per_sync_run_data

    @property
    def _items_books(self):
        return self.__items_books

    @property
    def all_sites(self):
        return self.__sync_run.sites

    def mark_effective(self):
        self._DATA__EFFECTIVE.set(self, True)

    @property
    def was_effective(self) -> bool:
        return self._DATA__EFFECTIVE.get(self)

    @property
    def error(self):
        return self.__per_sync_run_data.get("error")

    def set_error(self, error: Exception):
        self.__per_sync_run_data["error"] = error

    async def remove_site_from_items_books(self, site):
        # TODO weg  # pylint: disable=disallowed-name
        # TODO oddly low-level
        items_books_variable = self.__sync_run.volume_state_variable("items_books")
        site_name = parzzley.fs.site_name(site)
        self.__items_books[site_name] = parzzley.sync.engine._PerSiteItemsBook.from_serializable_data(
            None, self.__sync_run.sn
        )
        await items_books_variable.set_value(None, key=site_name)
        foo = await items_books_variable.value(key="")
        if foo:
            bar = foo[0][0]
            for site_list in bar.values():
                while site_name in site_list:
                    site_list.remove(site_name)
            await items_books_variable.set_value(foo, key="")
            self.__items_books[None] = parzzley.sync.engine._GlobalItemsBook.from_serializable_data(
                foo, self.__sync_run.sn, (_.name for _ in self.all_sites)
            )

    def set_stream_support(self, stream_name, item_types, *, for_site=None, cookies_are_move_stable=False):
        item_types = tuple(item_types)
        if item_types:
            self.__stream_support_per_site(for_site)[stream_name] = tuple(item_types), cookies_are_move_stable
        else:
            try:
                self.__stream_support_per_site(for_site).pop(stream_name)
            except KeyError:
                pass

    def __stream_support_per_site(self, for_site):
        return self._DATA__STREAM_SUPPORT_PER_SITE.get(self, **self._data__for_site(for_site))

    def _stream_support(self):
        return self._DATA__STREAM_SUPPORT.get(self)

    @property
    def stream_support_info(self):
        return self._StreamSupportInfo(self._stream_support())

    def determined_supported_streams(self, *, for_site=None):
        return tuple(self.__stream_support_per_site(for_site).keys())

    def supported_item_types(self, stream_name, *, for_site=None):
        return self.__stream_support_per_site(for_site).get(stream_name, ((),))[0]

    def cookies_are_move_stable(self, stream_name, *, for_site=None):
        return self.__stream_support_per_site(for_site).get(stream_name, ((), False))[1]

    def set_final_stream_support(self, stream_name, item_types, cookies_are_move_stable):
        item_types = tuple(item_types)
        if item_types:
            self._stream_support()[stream_name] = tuple(item_types), cookies_are_move_stable
        else:
            try:
                self._stream_support().pop(stream_name)
            except KeyError:
                pass

    class _EventData:

        def __init__(self, name, initial_value, native_data_name, scope):
            self.__name = name
            self.__initial_value_json = json.dumps(initial_value)
            self.__native_data_name = native_data_name
            self.__scope = scope

        def get(self, event, key_data):
            key = self.__key(key_data)
            native_data = self.__native_data(event)
            result = native_data.get(key, self)
            if result is self:
                result = native_data[key] = json.loads(self.__initial_value_json)
            return result

        def set(self, event, key_data, value):
            self.__native_data(event)[self.__key(key_data)] = value

        def __native_data(self, event):
            return getattr(event, self.__native_data_name)

        def __key(self, key_data):
            return self.__name, *(key_data[scope_key] for scope_key in self.__scope)

    class _StreamSupportInfo(parzzley.sync.aspect.events.sync_run._EventAfterStreamSupportDetermined.StreamSupportInfo):

        def __init__(self, info_dict):
            self.__info_dict = info_dict

        @property
        def supported_streams(self):
            return self.__info_dict.keys()

        def cookies_are_move_stable(self, stream_name):
            return (self.__info_dict.get(stream_name) or ((), False))[1]

        def supported_item_types(self, stream_name):
            return (self.__info_dict.get(stream_name) or ((), False))[0]


class ItemEvent(
    SyncRunEvent,
    parzzley.sync.aspect.events.item.DecideToSkip,
    parzzley.sync.aspect.events.item.Prepare,
    parzzley.sync.aspect.events.item.DetermineType,
    parzzley.sync.aspect.events.item.RefreshItemsBook,
    parzzley.sync.aspect.events.item.ApplyUpdate,
    parzzley.sync.aspect.events.item.PrepareUpdating,
    parzzley.sync.aspect.events.item.SetUpWorkingItems,
    parzzley.sync.aspect.events.item.SkipDueToConflicts,
):
    """
    Implementation of all item events.
    """

    _DATA__ALL_CONFLICTS = parzzley.sync.aspect.events.Data([], per_item=True)
    _DATA__IS_MARKED_FOR_SKIP = parzzley.sync.aspect.events.Data(False, per_item=True)
    _DATA__IS_MARKED_FOR_FULL_RETRY = parzzley.sync.aspect.events.Data(False, per_item=True)
    _DATA__ITEM_TYPE = parzzley.sync.aspect.events.Data(None, per_item=True, per_site=True)
    _DATA__NEW_ITEM_INFO = parzzley.sync.aspect.events.Data(per_item=True, per_site=True)
    _DATA__PER_STREAM_DATAS = parzzley.sync.aspect.events.Data({}, per_item=True)
    _DATA__WORKING_ITEMS = parzzley.sync.aspect.events.Data([], per_item=True, per_site=True)

    def __init__(
        self,
        site,
        sync_run,
        per_sync_run_data,
        items_books,
        item: "parzzley.fs.Item",
        per_item_data,
        logger: "_Logger|None" = None,
    ):
        super().__init__(site, sync_run, per_sync_run_data, items_books, logger or _Logger(self, item, None))
        self.__item = item
        self.__per_item_data = per_item_data

    def to_dir_event(self):
        return DirEvent(
            self.site, self.sync_run, self._per_sync_run_data, self._items_books, self.__item, self.__per_item_data
        )

    def to_stream_event(self, stream_name):
        per_stream_datas = self._DATA__PER_STREAM_DATAS.get(self)
        per_stream_data = per_stream_datas[stream_name] = per_stream_datas.get(stream_name, {})
        return StreamEvent(
            self.site,
            self.sync_run,
            self._per_sync_run_data,
            self._items_books,
            self.__item,
            self.__per_item_data,
            stream_name,
            per_stream_data,
        )

    @property
    def item(self):
        return self.__item

    @property
    def _per_item_data(self):
        return self.__per_item_data

    def stream_cookie(self, for_site=None):
        return self.to_stream_event("").stream_cookie(for_site)

    @property
    def all_conflicts(self):
        return self._DATA__ALL_CONFLICTS.get(self)

    def set_all_conflicts(self, all_conflicts):
        self._DATA__ALL_CONFLICTS.set(self, all_conflicts)

    def update_cookies(self, stream_cookies, *, for_site=None):
        self._DATA__NEW_ITEM_INFO.set(self, stream_cookies, **self._data__for_site(for_site))

    def streams_with_destination_streamables(self, for_site=None):
        site_name = parzzley.fs.site_name(for_site or self.site)
        result = []
        for stream_name in self.stream_support_info.supported_streams:
            stream_event = self.to_stream_event(stream_name)
            if any(
                True for _ in stream_event._DATA__DESTINATION_STREAMABLES.get(stream_event) if _[1].name == site_name
            ):
                result.append(stream_name)
        return tuple(result)

    def add_working_item(self, working_item, *, for_site=None):
        self.__working_items__list(for_site).append(parzzley.fs.item(working_item))

    def remove_working_item(self, working_item, *, for_site=None):
        self.__working_items__list(for_site).remove(parzzley.fs.item(working_item))

    def working_items(self, *, for_site=None):
        return tuple(self.__working_items__list(for_site))

    def set_item_type(self, item_type, *, for_site: "parzzley.fs.TSiteInput|None" = None):
        self._DATA__ITEM_TYPE.set(self, item_type, **self._data__for_site(for_site))

    @property
    def is_marked_full_retry_needed(self):
        return self._DATA__IS_MARKED_FOR_FULL_RETRY.get(self)

    def mark_full_retry_needed(self):
        self._DATA__IS_MARKED_FOR_FULL_RETRY.set(self, True)

    @property
    def is_item_marked_to_skip(self):
        return bool(self._DATA__IS_MARKED_FOR_SKIP.get(self))

    @property
    def is_item_marked_to_skip_permanently(self):
        if skip_tuple := self._DATA__IS_MARKED_FOR_SKIP.get(self):
            return skip_tuple[0]
        return False

    def skip_item(self, *, only_now=False):
        self._DATA__IS_MARKED_FOR_SKIP.set(self, (not only_now or self.is_item_marked_to_skip_permanently,))

    def sites_involved_in_current_item_last_successful_sync(self):
        sync_no = self._items_books[None].last_successful_sync_no(self.item)
        return None if sync_no is None else self._items_books[None].sites_involved_in_sync_no(sync_no)

    def item_type_after_last_sync(self, for_site=None):
        return self._items_books[parzzley.fs.site_name(for_site or self.site)].item_type_after_last_sync(self.item)

    def item_type(self, for_site=None):
        return self._DATA__ITEM_TYPE.get(self, **self._data__for_site(for_site)) or parzzley.fs.ItemType.NONE

    def _master_site(self, of_stream=None):
        return self.to_stream_event(of_stream or "")._master_site()

    def content_version(self, for_site=None, *, only_past):
        return self.to_stream_event("").content_version(for_site, only_past=only_past)

    def set_item_info(self, item_type, stream_cookie, *, for_site=None):
        stream_cookies = self.to_stream_event("").stream_cookies
        site_name = parzzley.fs.site_name(for_site or self.site)
        if item_type != parzzley.fs.ItemType.NONE:
            self._DATA__ITEM_TYPE.set(self, item_type, **self._data__for_site(for_site))
            stream_cookies[site_name] = stream_cookie
        else:
            self._DATA__ITEM_TYPE.set(self, None, **self._data__for_site(for_site))
            stream_cookies.pop(site_name)

    def updated_cookie(self, stream_name, *, for_site=None):
        return self.to_stream_event(stream_name)._updated_cookie(for_site=for_site)

    def set_item_book_entry(self, item_type, cookies, *, for_site=None):
        self._items_books[parzzley.fs.site_name(for_site or self.site)].store_item_info(
            self.item, item_type or parzzley.fs.ItemType.NONE, cookies
        )

    def __working_items__list(self, for_site):
        return self._DATA__WORKING_ITEMS.get(self, **self._data__for_site(for_site))


class DirEvent(
    ItemEvent,
    parzzley.sync.aspect.events.item.dir.Iterated,
    parzzley.sync.aspect.events.item.dir.List,
    parzzley.sync.aspect.events.item.dir.Prepare,
):
    """
    Implementation of all directory events.
    """

    _DATA__CHILD_NAMES = parzzley.sync.aspect.events.Data([], per_item=True)

    @property
    def child_names(self) -> set[str]:
        return set(self._DATA__CHILD_NAMES.get(self))

    def add_child_names(self, child_names):
        self._DATA__CHILD_NAMES.get(self).extend(child_names)


class StreamEvent(
    ItemEvent,
    parzzley.sync.aspect.events.item.stream.DetermineComparator,
    parzzley.sync.aspect.events.item.stream.DetermineCookie,
    parzzley.sync.aspect.events.item.stream.DetermineConflicts,
    parzzley.sync.aspect.events.item.stream.TryResolveConflicts,
    parzzley.sync.aspect.events.item.stream.ApplyConflictResolution,
    parzzley.sync.aspect.events.item.stream.DetectChanges,
    parzzley.sync.aspect.events.item.stream.DetermineMasterSiteTable,
    parzzley.sync.aspect.events.item.stream.MasterSiteDetermined,
    parzzley.sync.aspect.events.item.stream.CollectDestinationStreamables,
    parzzley.sync.aspect.events.item.stream.CollectSourceStreamables,
    parzzley.sync.aspect.events.item.stream.TransferUpdate,
):
    """
    Implementation of all stream events.
    """

    _DATA__CHANGED_SITES = parzzley.sync.aspect.events.Data([], per_stream=True)
    _DATA__CONFLICTS = parzzley.sync.aspect.events.Data([], per_stream=True)
    _DATA__CONFLICT_RESOLUTION = parzzley.sync.aspect.events.Data(per_stream=True)
    _DATA__DESTINATION_STREAMABLES = parzzley.sync.aspect.events.Data([], per_stream=True)
    _DATA__DISABLE_CHANGE_DETECTION = parzzley.sync.aspect.events.Data(False, per_stream=True)
    _DATA__REFRESH_NEEDED_SITES = parzzley.sync.aspect.events.Data([], per_stream=True)
    _DATA__SOURCE_STREAMABLE = parzzley.sync.aspect.events.Data(per_stream=True, per_site=True)
    _DATA__STREAM_COOKIES = parzzley.sync.aspect.events.Data({}, per_stream=True)
    _DATA__STREAM_COMPARATOR = parzzley.sync.aspect.events.Data(per_stream=True)
    _DATA__STREAM_MASTER_SITE = parzzley.sync.aspect.events.Data(per_stream=True)
    _DATA__STREAM_MASTER_TABLE = parzzley.sync.aspect.events.Data({}, per_stream=True)
    _DATA__STREAM_PIPES = parzzley.sync.aspect.events.Data([], per_stream=True, per_site=True)

    def __init__(
        self,
        site,
        sync_run,
        per_sync_run_data,
        items_books,
        item: "parzzley.fs.Item",
        per_item_data,
        stream_name: str,
        per_stream_data,
        logger: "_Logger|None" = None,
    ):
        super().__init__(
            site,
            sync_run,
            per_sync_run_data,
            items_books,
            item,
            per_item_data,
            logger or _Logger(self, item, stream_name),
        )
        self.__stream_name = stream_name
        self.__per_stream_data = per_stream_data

    @property
    def stream_name(self):
        return self.__stream_name

    @property
    def _per_stream_data(self):
        return self.__per_stream_data

    def is_site_marked_as_changed(self, for_site=None):
        return parzzley.fs.site_name(for_site or self.site) in self._DATA__CHANGED_SITES.get(self)

    def is_site_marked_as_needing_refreshed(self, for_site=None):
        return parzzley.fs.site_name(for_site or self.site) in self._DATA__REFRESH_NEEDED_SITES.get(self)

    def source_streamable(self, for_site=None):
        return self._DATA__SOURCE_STREAMABLE.get(self, **self._data__for_site(for_site))

    def set_source_streamable(self, source_streamable, *, for_site=None):
        self._DATA__SOURCE_STREAMABLE.set(self, source_streamable, **self._data__for_site(for_site))

    def destination_streamables(self):
        return tuple(_[0] for _ in self._DATA__DESTINATION_STREAMABLES.get(self))

    def add_destination_streamable(self, destination_streamable):
        self._DATA__DESTINATION_STREAMABLES.get(self).append((destination_streamable, self.site))

    def disable_change_detection(self):
        self._DATA__DISABLE_CHANGE_DETECTION.set(self, True)

    def is_change_detection_disabled(self):
        return self._DATA__DISABLE_CHANGE_DETECTION.get(self)

    def stream_pipes(self, for_site=None):
        return tuple(self._DATA__STREAM_PIPES.get(self, **self._data__for_site(for_site)))

    def add_stream_pipe(self, pipe, *, for_site=None):
        self._DATA__STREAM_PIPES.get(self, **self._data__for_site(for_site)).append(pipe)

    def mark_changed(self, site=None):
        self._DATA__CHANGED_SITES.get(self).append(parzzley.fs.site_name(site or self.site))

    def mark_all_last_involved_sites_changed_if_this_is_not_one_of_them(self, site=None):
        site_name = parzzley.fs.site_name(site or self.site)

        if last_successful_sync_site_names := self.sites_involved_in_current_item_last_successful_sync():
            last_successful_sync_site_names = set(last_successful_sync_site_names)
            if site_name not in last_successful_sync_site_names:
                for site_ in (_ for _ in self.all_sites if _.name in last_successful_sync_site_names):
                    self.mark_changed(site_)

    def mark_refresh_needed(self, site=None):
        site_name = parzzley.fs.site_name(site or self.site)
        self._DATA__REFRESH_NEEDED_SITES.get(self).append(site_name)

    def resolve_conflicts(self, master_site):
        self._DATA__CONFLICT_RESOLUTION.set(self, parzzley.fs.site_name(master_site))

    @property
    def conflict_resolution(self):
        return self._DATA__CONFLICT_RESOLUTION.get(self)

    @property
    def conflicts(self):
        return tuple(self._DATA__CONFLICTS.get(self))

    def changed_dangerously_late(self, for_site=None):
        return (
            self.content_version(self.master_site, only_past=True)
            < self.content_version(self.master_site, only_past=False)
            <= self.content_version(for_site, only_past=False)
        )

    def add_conflict(self, description, details=None):
        self._DATA__CONFLICTS.get(self).append(
            parzzley.sync.aspect.events.item.stream.DetermineConflicts._Conflict(description, details)
        )

    def remove_conflict(self, conflict):
        self._DATA__CONFLICTS.get(self).remove(conflict)

    def set_master_site(self, master_site=None):
        if isinstance(master_site, str):
            master_site = [site for site in self.all_sites if site.name == master_site][0]
        elif master_site is None:
            master_site = self.site
        self._DATA__STREAM_MASTER_SITE.set(self, master_site)

    def set_sync_run_sn_of_last_change(self, sn, *, for_site=None):
        self._DATA__STREAM_MASTER_TABLE.get(self)[parzzley.fs.site_name(for_site or self.site)] = sn

    def _master_site(self, of_stream=None):
        if of_stream is not None:
            return self.to_stream_event(of_stream)._master_site()
        return self._DATA__STREAM_MASTER_SITE.get(self)

    def content_version(self, for_site=None, *, only_past):
        for_site = parzzley.fs.site_name(for_site or self.site)

        if only_past:
            if for_site in self._DATA__REFRESH_NEEDED_SITES.get(self):
                return 0
            return self._items_books[for_site].last_change_run_sn(self.item.path)

        return self._DATA__STREAM_MASTER_TABLE.get(self)[for_site]

    def stream_cookie(self, for_site=None):
        return self.stream_cookies.get(parzzley.fs.site_name(for_site or self.site))

    @property
    def stream_cookies(self) -> dict[str, tuple]:
        return self._DATA__STREAM_COOKIES.get(self)

    def set_stream_cookie(self, stream_cookie, *, for_site=None):
        self.stream_cookies[parzzley.fs.site_name(for_site or self.site)] = stream_cookie

    def stream_cookie_after_last_sync(self, for_site=None):
        return self._items_books[parzzley.fs.site_name(for_site or self.site)].stream_cookie_after_last_sync(
            self.item.path, self.stream_name
        )

    def _updated_cookie(self, for_site=None):
        if new_cookies := self._DATA__NEW_ITEM_INFO.get(self, **self._data__for_site(for_site)):
            if (new_cookie := new_cookies.get(self.stream_name, self)) is not self:
                return new_cookie
        return self.stream_cookie(for_site)

    @property
    def comparator(self):
        return self._DATA__STREAM_COMPARATOR.get(self)

    def set_comparator(self, comparator):
        self._DATA__STREAM_COMPARATOR.set(self, comparator)


class _Logger(parzzley.sync.logger.Logger):

    _PYTHON_LOGGER_FUNC_BY_SEVERITY = {
        parzzley.sync.logger.Severity.DEBUG: _parzzley_sync_logger.debug,
        parzzley.sync.logger.Severity.INFO: _parzzley_sync_logger.info,
        parzzley.sync.logger.Severity.WARNING: _parzzley_sync_logger.warning,
        parzzley.sync.logger.Severity.FATAL: _parzzley_sync_logger.error,
    }

    def __init__(self, event: SyncRunEvent, item: "parzzley.fs.Item|None", stream_name: str | None):
        self.__event = event
        self.__item = item
        self.__stream_name = stream_name

    def _log(self, severity, message, message_args):
        python_logging_message = ""
        if self.__item:
            python_logging_message += f"/{self.__item.path.decode(errors="replace")}"
        if self.__stream_name is not None:
            python_logging_message += f" ({self.__stream_name or "main"})"
        if python_logging_message:
            python_logging_message += ": "
        python_logging_message += message.replace("\n", "\n" + len(python_logging_message) * " ")
        _Logger._PYTHON_LOGGER_FUNC_BY_SEVERITY.get(severity, _parzzley_sync_logger.error)(
            python_logging_message, *message_args
        )

        self.__event.all_log_entries.append(
            parzzley.sync.logger.Entry(
                severity=severity,
                message=message,
                message_args=message_args,
                item=self.__item,
                stream=self.__stream_name,
            )
        )
