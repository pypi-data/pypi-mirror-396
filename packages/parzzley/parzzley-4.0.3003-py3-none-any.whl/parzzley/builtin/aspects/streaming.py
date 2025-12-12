#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Streaming.
"""
import asyncio
import contextlib

import parzzley.builtin.aspects.conflicts
import parzzley.builtin.aspects.exclude_paths


class SkipItemIfNoUpToDateSitesAreConnected(parzzley.sync.aspect.Aspect):
    """
    Skip an item if no up-to-date sites are connected (in order to prevent data loss in some situations).
    """

    _DATA__CHECK_DONE = parzzley.sync.aspect.events.Data(False, per_item=True)

    @parzzley.sync.aspect.event_handler(
        beforehand_optional=[parzzley.builtin.aspects.exclude_paths.ExcludePaths.decide_to_skip]
    )
    async def decide_to_skip(self, event: parzzley.sync.aspect.events.item.DecideToSkip):
        """
        Skip for now if no up-to-date sites are connected.
        """
        if SkipItemIfNoUpToDateSitesAreConnected._DATA__CHECK_DONE.get(event):
            return  # otherwise we do the check for each site again
        SkipItemIfNoUpToDateSitesAreConnected._DATA__CHECK_DONE.set(event, True)

        last_successful_sync_site_names = set(event.sites_involved_in_current_item_last_successful_sync() or ())
        if not last_successful_sync_site_names:
            return

        if not any(_.name in last_successful_sync_site_names for _ in event.all_sites):
            event.log.warning("Skipped now because no recent enough site is connected")
            event.skip_item(only_now=True)


class GlobalStreamSupport(parzzley.sync.aspect.Aspect):
    """
    Derives global stream support information.

    It checks if all sites have determined the same supported streams (with the same item types) in
    :py:class:`parzzley.sync.aspect.events.sync_run.DetermineStreamSupport`. It will then take this as the global result
    or will fail otherwise.
    """

    _DATA__STREAM_SUPPORT_DICT = parzzley.sync.aspect.events.Data()

    @parzzley.sync.aspect.event_handler()
    async def validate_stream_support(self, event: parzzley.sync.aspect.events.sync_run.ValidateStreamSupport):
        """
        Validate the determined stream support.
        """
        stream_support = {
            stream_name: (
                tuple(event.supported_item_types(stream_name, for_site=event.site)),
                event.cookies_are_move_stable(stream_name, for_site=event.site),
            )
            for stream_name in event.determined_supported_streams(for_site=event.site)
        }

        stored_stream_support_dict = self._DATA__STREAM_SUPPORT_DICT.get(event)
        if stored_stream_support_dict is None:
            self._DATA__STREAM_SUPPORT_DICT.set(event, stream_support)

            for stream_name, (supported_item_types, cookies_are_move_stable) in stream_support.items():
                event.set_final_stream_support(stream_name, supported_item_types, cookies_are_move_stable)

        elif stored_stream_support_dict != stream_support:
            raise RuntimeError("different stream support")


class SetItemsBookEntry(parzzley.sync.aspect.Aspect):
    """
    Primarily stores the "updated cookie", so it can be used for decisions in the next sync run; e.g. in
    :py:class:`parzzley.sync.aspect.events.item.stream.DetectChanges`.
    """

    @parzzley.sync.aspect.event_handler()
    async def refresh_items_book(self, event: parzzley.sync.aspect.events.item.RefreshItemsBook):
        """
        Refresh items book.
        """
        cookies = {
            stream_name: event.updated_cookie(stream_name)
            for stream_name in event.stream_support_info.supported_streams
        }
        event.set_item_book_entry(event.site.item_type_by_cookie(cookies[""]), cookies)


class SourceStreamable(parzzley.sync.aspect.Aspect):
    """
    Sets the source streamable from the site.
    """

    @parzzley.sync.aspect.event_handler(parzzley.sync.aspect.only_if.IsItemTypeHereSupportedByStream())
    async def source_streamable(self, event: parzzley.sync.aspect.events.item.stream.CollectSourceStreamables):
        """
        Collect the source streamable.
        """
        event.set_source_streamable(await event.site.read_streamable(event.item, event.stream_name))


class GetCookie(parzzley.sync.aspect.Aspect):
    """
    Queries the cookie from the site.
    """

    @parzzley.sync.aspect.event_handler()
    async def determine_cookie(self, event: parzzley.sync.aspect.events.item.stream.DetermineCookie):
        """
        Determine the cookie.
        """
        event.set_stream_cookie(await event.site.cookie(event.item, event.stream_name))


class ComputeMasterSiteTable(parzzley.sync.aspect.Aspect):
    """
    Determines the master site for this stream (and the score table) based on the information gathered in
    :py:class:`parzzley.sync.aspect.events.item.stream.DetectChanges`.
    """

    _DATA__MASTER_SITE_TUPLE = parzzley.sync.aspect.events.Data(per_stream=True)

    @parzzley.sync.aspect.event_handler()
    async def master_site_table(self, event: parzzley.sync.aspect.events.item.stream.DetermineMasterSiteTable):
        """
        Determine the master site table.
        """
        site_version = event.content_version(only_past=True)
        if event.is_site_marked_as_needing_refreshed():
            site_version = 0
        elif event.is_site_marked_as_changed():
            site_version = event.sync_run.sn

        event.set_sync_run_sn_of_last_change(site_version)

        master_site_tuple = self._DATA__MASTER_SITE_TUPLE.get(event)
        if (master_site_tuple is None) or (master_site_tuple[1] < site_version):
            self._DATA__MASTER_SITE_TUPLE.set(event, (event.site, site_version))
            event.set_master_site(event.site)


class UpdateTransfer(parzzley.sync.aspect.Aspect):
    """
    Runs a loop that reads from the source streamable and writes to the destination streamables. If the source has been
    changed during transfer, it marks this item to need full retry (and stores some data for it).
    """

    _DATA__UPDATE_LOG_INFO = parzzley.sync.aspect.events.Data([], per_item=True)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(of_stream=""),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(),
    )
    async def transfer_update(self, event: parzzley.sync.aspect.events.item.stream.TransferUpdate):
        """
        Transfer the update from the source stream to the destination streams.
        """
        if event.is_marked_full_retry_needed:
            return

        destination_streamables = event.destination_streamables()
        source_streamable = event.source_streamable()

        if source_streamable and destination_streamables:
            for pipe in event.stream_pipes():
                source_streamable = pipe(source_streamable)

            async with contextlib.AsyncExitStack() as stack:
                destination_streams = [
                    await stack.enter_async_context(destination_streamable.stream())
                    for destination_streamable in destination_streamables
                ]

                async with source_streamable.stream() as source_stream:
                    while True:
                        data = await source_stream.read(32 * 1024**2)
                        if data:
                            await asyncio.gather(*[dest_stream.write(data) for dest_stream in destination_streams])
                        if data is None:
                            break

                if event.is_change_detection_disabled() or event.stream_cookie() == await event.site.cookie(
                    event.item, event.stream_name
                ):
                    for dest_stream in destination_streams:
                        await dest_stream.commit()
                    self._DATA__UPDATE_LOG_INFO.get(event).append((event.stream_name, event.master_site.name))
                    event.mark_effective()

                else:
                    event.log.info("Skipped due to ongoing changes")
                    StickToOldMasterSitesOnItemRetry._DATA__RETRY.get(event).append((event.item, (event.stream_name,)))
                    event.mark_full_retry_needed()

    @parzzley.sync.aspect.event_handler()
    async def log_update(self, event: parzzley.sync.aspect.events.item.RefreshItemsBook):  # TODO odd event
        """
        Log updates.
        """
        if update_log_info := self._DATA__UPDATE_LOG_INFO.get(event):

            updates_per_site = {}
            for updated_stream, updated_from_site in update_log_info:
                updates_per_site[updated_from_site] = (*(updates_per_site.get(updated_from_site) or ()), updated_stream)

            event.log.info(
                "Updated %s",
                ", ".join(
                    f"{", ".join(_ or "main" for _ in stream_names)} from {site_name}"
                    for site_name, stream_names in updates_per_site.items()
                ),
            )
            update_log_info.clear()


class StickToOldMasterSitesOnItemRetry(parzzley.sync.aspect.Aspect):
    """
    Stick to old master sites on item retry, so some residuals from our last attempt do not get preferred now.

    This is the right things to do in general, but leads to a dangerous timing effect: If the user applies a change
    on a non-master site while the retry is happening, this change will get lost.
    """

    _DATA__RETRY = parzzley.sync.aspect.events.Data([], per_site=True)

    @parzzley.sync.aspect.event_handler()
    async def prepare_item(self, event: parzzley.sync.aspect.events.item.Prepare):
        """
        Prepare item sync.
        """
        retry_tuples = self._DATA__RETRY.get(event)
        retry_streams = []
        for i_retry_item, (retry_item, retry_item_streams) in reversed(tuple(enumerate(retry_tuples))):
            if retry_item == event.item:
                retry_streams += retry_item_streams
                retry_tuples.pop(i_retry_item)
        for retry_stream in retry_streams:
            event.to_stream_event(retry_stream).mark_changed()
            for non_master_site in event.all_sites:
                if non_master_site != event.site:
                    event.to_stream_event(retry_stream).mark_refresh_needed(non_master_site)


class WorkingItem(parzzley.sync.aspect.Aspect):
    """
    Manage working items and use them as destination streamables.
    """

    _DATA__TEMP_ITEM = parzzley.sync.aspect.events.Data(per_item=True, per_site=True)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(),
        parzzley.sync.aspect.only_if.ItemOnMasterSiteIsType(
            no=[parzzley.fs.ItemType.DIRECTORY, parzzley.fs.ItemType.ALIEN]
        ),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
    )
    async def temp_working_item(self, event: parzzley.sync.aspect.events.item.SetUpWorkingItems):
        """
        Create temporary working item if on this site the main stream needs an update from the master site.
        """
        if self.__master_site_is_more_recent(event.to_stream_event("")):  # TODO little odd
            temp_item = await event.site.create_temp_item(event.item_type(event.master_site))
            self._DATA__TEMP_ITEM.set(event, temp_item)
            event.add_working_item(temp_item)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsItemTypeOnStreamMasterSiteSupportedByStream(),
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(),
    )
    async def collect_destination(self, event: parzzley.sync.aspect.events.item.stream.CollectDestinationStreamables):
        """
        Collect the destination streamable.
        """
        if self.__master_site_is_more_recent(event) or self._DATA__TEMP_ITEM.get(event):
            working_items = list(event.working_items())

            if (self._DATA__TEMP_ITEM.get(event) is None) and (event.site != event.master_site):
                working_items.append(event.item)

            for working_item in working_items:
                if event.item_type(
                    event.to_stream_event("").master_site
                ) in event.stream_support_info.supported_item_types(event.stream_name):
                    event.add_destination_streamable(await event.site.write_streamable(working_item, event.stream_name))

    @parzzley.sync.aspect.event_handler()
    async def commit_update(self, event: parzzley.sync.aspect.events.item.ApplyUpdate):
        """
        Commit the update.
        """
        if event.is_marked_full_retry_needed:
            return
        if event.item_type(event.master_site) == parzzley.fs.ItemType.NONE:
            return

        streams_with_destination_streamables = event.streams_with_destination_streamables()
        if event.item_type() != event.item_type(event.master_site):
            streams_with_destination_streamables = tuple(("", *event.stream_support_info.supported_streams))

        if not len(streams_with_destination_streamables) > 0:
            return

        temp_item = self._DATA__TEMP_ITEM.get(event)

        cookies = {
            stream_name: await event.site.cookie(temp_item or event.item, stream_name)
            for stream_name in streams_with_destination_streamables
            if event.stream_support_info.cookies_are_move_stable(stream_name)
        }

        if temp_item:
            if event.item_type() == event.item_type(event.master_site):
                for stream_name in event.stream_support_info.supported_streams:
                    if event.stream_support_info.cookies_are_move_stable(stream_name):
                        stream_cookie = await event.site.cookie(event.item, stream_name)
                        if stream_cookie != event.stream_cookie(stream_name):
                            raise RuntimeError("destination site has been changed meanwhile")

            await event.site.move_item(temp_item, event.item)

        cookies.update(
            {
                stream_name: await event.site.cookie(event.item, stream_name)
                for stream_name in streams_with_destination_streamables
                if stream_name not in cookies
            }
        )

        event.update_cookies(cookies)

    @parzzley.sync.aspect.event_handler()
    async def revert_content_equal_to_master_flag(
        self, event: parzzley.sync.aspect.events.item.stream.ApplyConflictResolution
    ):
        """
        Revert 'content equal to master' flag during conflict resolution (since that might change the master!).
        """
        parzzley.builtin.aspects.conflicts.DetectContentConflicts._DATA__CONTENT_EQUAL_TO_MASTER.set(event, False)

    def __master_site_is_more_recent(self, event) -> bool:
        if parzzley.builtin.aspects.conflicts.DetectContentConflicts._DATA__CONTENT_EQUAL_TO_MASTER.get(event):
            return False

        return event.content_version(only_past=True) < event.content_version(
            only_past=False, for_site=event.master_site
        )
