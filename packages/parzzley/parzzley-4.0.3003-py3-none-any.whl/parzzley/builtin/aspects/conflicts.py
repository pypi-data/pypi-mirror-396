#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Aspects for conflict detection and handling.
"""
import asyncio
import contextlib
import dataclasses

import parzzley


class DetectItemTypeConflicts(parzzley.sync.aspect.Aspect):
    """
    Detect item type conflicts (e.g. file vs. directory, file vs. symlink, ...).
    """

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsStream(""),
        parzzley.sync.aspect.only_if.ItemExistsHere(),
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
    )
    async def determine_conflicts(self, event: parzzley.sync.aspect.events.item.stream.DetermineConflicts):
        """
        Detect type conflicts.
        """
        if not event.changed_dangerously_late():
            return

        if (master_item_type := event.item_type(event.master_site)) != (this_item_type := event.item_type()):
            event.add_conflict(
                "by item type",
                f"{master_item_type.name} on {event.master_site.name!r}"
                f" / {this_item_type.name} on {event.site.name!r}",
            )


class DetectContentConflicts(parzzley.sync.aspect.Aspect):
    """
    Detect content conflicts (i.e. the stream content differs).
    """

    _DATA__CONTENT_EQUAL_TO_MASTER = parzzley.sync.aspect.events.Data(per_site=True, per_item=True, per_stream=True)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsItemTypeHereSupportedByStream(),
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(),
        parzzley.sync.aspect.only_if.ItemExistsHere(),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
    )
    async def determine_conflicts(self, event: parzzley.sync.aspect.events.item.stream.DetermineConflicts):
        """
        Detect stream content conflicts.
        """
        if not event.changed_dangerously_late():
            return

        if event.item_type() == event.item_type(event.master_site):

            if await (event.comparator or self.__are_streams_equal)(
                self.__source_streamable(event, event.site), self.__source_streamable(event, event.master_site)
            ):
                self._DATA__CONTENT_EQUAL_TO_MASTER.set(event, True)
            else:
                event.add_conflict("by content")

    async def __are_streams_equal(self, streamable_1, streamable_2):
        async with contextlib.AsyncExitStack() as stack:
            streams = [
                _Source(await stack.enter_async_context(streamable.stream()))
                for streamable in (streamable_1, streamable_2)
            ]

            conflict_detected = False
            while not conflict_detected:
                await asyncio.gather(*[stream.read_more() for stream in streams if len(stream.buffer) < 1024 * 1024])
                buffer_min_len = min(len(stream.buffer) for stream in streams)
                buffer_max_len = max(len(stream.buffer) for stream in streams)

                buffer_prefix = None
                for stream in streams:
                    stream_buffer_prefix = stream.buffer[:buffer_min_len]
                    if buffer_prefix is None:
                        buffer_prefix = stream_buffer_prefix
                    elif stream_buffer_prefix != buffer_prefix:
                        conflict_detected = True
                        break
                    stream.buffer = stream.buffer[buffer_min_len:]

                    if stream.finished and not stream.buffer and buffer_max_len > buffer_min_len:
                        conflict_detected = True
                        break

                if all(stream.finished for stream in streams) and not any(stream.buffer for stream in streams):
                    break

        return not conflict_detected

    def __source_streamable(
        self, event: parzzley.sync.aspect.events.item.stream.DetermineConflicts, site: parzzley.fs.Site
    ) -> parzzley.fs.stream.ReadStreamable:
        streamable = event.source_streamable(site)
        for pipe in event.stream_pipes(site):
            streamable = pipe(streamable)
        return streamable


class TrackConflicts(parzzley.sync.aspect.Aspect):
    """
    Stores conflict data for later resolution.
    """

    _DATA__CONFLICTS = parzzley.sync.aspect.events.Data([])

    @parzzley.sync.aspect.event_handler()
    async def store_conflict_data(self, event: parzzley.sync.aspect.events.item.SkipDueToConflicts):
        """
        Store conflict data for later resolution from outside (e.g. manually by the user).
        """
        conflicts_storage_site = await _conflicts_storage_site(event)

        conflict_directory_item = _conflict_directory_item(event.item)

        conflict_directory_item_type = await conflicts_storage_site.item_type(conflict_directory_item)

        if conflict_directory_item_type == parzzley.fs.ItemType.NONE:
            await conflicts_storage_site.create_item(
                conflict_directory_item, parzzley.fs.ItemType.DIRECTORY, recursive=True
            )
        elif conflict_directory_item_type != parzzley.fs.ItemType.DIRECTORY:
            await conflicts_storage_site.remove_item(conflict_directory_item)

        for stream_name in {conflict.stream_name for conflict in event.all_conflicts}:
            item = conflict_directory_item(f":{stream_name}".encode())

            if not await conflicts_storage_site.item_exists(item):
                await conflicts_storage_site.create_item(item, parzzley.fs.ItemType.FILE)
            await conflicts_storage_site.write_bytes(item, "".join([f"{xl.name}\n" for xl in event.all_sites]).encode())

        self._DATA__CONFLICTS.get(event).append(conflict_directory_item.path)

    @parzzley.sync.aspect.event_handler()
    async def cleanup_conflicts_storage_site(self, event: parzzley.sync.aspect.events.sync_run.Finish):
        """
        Cleanup of outdated stored conflict data.
        """
        conflicts_storage_site = await _conflicts_storage_site(event)

        async def _cleanup(item):
            for child_item in await conflicts_storage_site.children(item):
                match await conflicts_storage_site.item_type(child_item):
                    case parzzley.fs.ItemType.FILE:
                        if item.path not in self._DATA__CONFLICTS.get(event):
                            for child_item_ in await conflicts_storage_site.children(item):
                                if await conflicts_storage_site.item_type(child_item_) == parzzley.fs.ItemType.FILE:
                                    await conflicts_storage_site.remove_item(child_item_)
                            try:
                                await conflicts_storage_site.remove_item(item)
                            except parzzley.fs.Site.Exception:
                                pass
                    case parzzley.fs.ItemType.DIRECTORY:
                        await _cleanup(child_item)
            try:
                await conflicts_storage_site.remove_item(item)
            except parzzley.fs.Site.Exception:
                pass

        await _cleanup(conflicts_storage_site.root_directory)


class TryResolveConflictsByHint(parzzley.sync.aspect.Aspect):
    """
    Resolves conflicts by external resolution hint files.
    """

    @parzzley.sync.aspect.event_handler()
    async def resolve_conflicts_by_hint_file(self, event: parzzley.sync.aspect.events.item.stream.TryResolveConflicts):
        """
        Resolves conflicts by stored conflict resolution data.
        """
        conflicts_storage_site = await _conflicts_storage_site(event)
        hint_file_item = _conflict_directory_item(event.item)(f":{event.stream_name}".encode())

        if await conflicts_storage_site.item_type(hint_file_item) == parzzley.fs.ItemType.FILE:
            lines = [x.strip() for x in (await conflicts_storage_site.read_bytes(hint_file_item)).decode().split("\n")]
            lines = [x for x in lines if x != ""]

            if len(lines) == 1:
                site_name = lines[0]

                for site in event.all_sites:
                    if site.name == site_name:
                        event.resolve_conflicts(site)
                        return

                event.log.warning("Unable to find name '%s' in conflict resolution info", site_name)


class ApplyConflictResolution(parzzley.sync.aspect.Aspect):
    """
    Apply the conflict resolution determined in :py:class:`parzzley.sync.aspect.events.item.stream.TryResolveConflicts`.
    """

    @parzzley.sync.aspect.event_handler()
    async def apply_conflict_resolution(self, event: parzzley.sync.aspect.events.item.stream.ApplyConflictResolution):
        """
        Apply the conflict resolution.
        """
        if event.conflict_resolution == event.site.name:
            event.set_master_site()
            event.set_sync_run_sn_of_last_change(event.sync_run.sn)

            for conflict in event.conflicts:
                event.remove_conflict(conflict)

            event.log.info("Resolved conflict by taking %s", event.site.name)


def _conflict_directory_item(item: parzzley.fs.Item) -> parzzley.fs.Item:
    segments = []
    while item.name:
        segments.append(item.name)
        item = item.parent

    result = parzzley.fs.item(b"root")
    for segment in reversed(segments):
        result = result(b"_" + segment)

    return result


async def _conflicts_storage_site(event):
    return await event.sync_run.site_control_site(event.site, "conflicts")


@dataclasses.dataclass
class _Source:
    stream: parzzley.fs.stream.ReadStream
    buffer: bytes = b""
    finished: bool = False

    async def read_more(self) -> None:
        """
        Read some more data.
        """
        if self.finished:
            return
        data = await self.stream.read(1024 * 1024)
        if data is None:
            self.finished = True
        else:
            self.buffer += data
