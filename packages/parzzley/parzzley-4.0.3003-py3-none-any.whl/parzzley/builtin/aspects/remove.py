#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Removal.
"""
import datetime
import time
import uuid

import parzzley.config.file_formats
import parzzley.builtin.aspects.streaming


@parzzley.sync.aspect.register_aspect
class DirectRemove(parzzley.sync.aspect.Aspect):
    """
    Basic, non-trashing removal. For a trash bin, see :py:class:`TrashRemove` instead.
    """

    _DATA__LOG_REMOVAL = parzzley.sync.aspect.events.Data(False, per_item=True)

    def __init__(self):
        super().__init__(CleanupTrashBin())

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemExistsHere(),
        parzzley.sync.aspect.only_if.ItemHereIsType(no=[parzzley.fs.ItemType.DIRECTORY]),
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(False),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
        afterwards=(parzzley.builtin.aspects.streaming.WorkingItem.commit_update,),
    )
    async def remove_non_dir(self, event: parzzley.sync.aspect.events.item.ApplyUpdate):
        """
        Remove the (non-directory) item if this reflects the most recent state.
        """
        await event.site.remove_item(event.item)
        self._DATA__LOG_REMOVAL.set(event, True)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemHereIsType(parzzley.fs.ItemType.DIRECTORY),
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(False, of_stream=""),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False, of_stream=""),
        afterwards=(parzzley.builtin.aspects.streaming.WorkingItem.commit_update,),
    )
    async def remove_dir(self, event: parzzley.sync.aspect.events.item.ApplyUpdate):
        """
        Remove directory if this reflects the most recent state.
        """
        await event.site.remove_item(event.item, recursive=True)
        self._DATA__LOG_REMOVAL.set(event, True)
        event.mark_effective()

    @parzzley.sync.aspect.event_handler()
    async def log_removal(self, event: parzzley.sync.aspect.events.item.RefreshItemsBook):  # TODO odd event
        """
        Log removals.
        """
        if self._DATA__LOG_REMOVAL.get(event):
            self._DATA__LOG_REMOVAL.set(event, False)
            event.log.info("Removed")


@parzzley.sync.aspect.register_aspect
class TrashRemove(parzzley.sync.aspect.Aspect):
    """
    Removal with a trash bin. For no trash bin, see :py:class:`DirectRemove` instead.
    """

    _DATA__LOG_REMOVAL = parzzley.sync.aspect.events.Data(False, per_item=True)

    def __init__(self, *, trash_max_age: str | float | datetime.timedelta = "30d"):
        super().__init__(CleanupTrashBin(trash_max_age=trash_max_age))

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemExistsHere(),
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(False),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
        afterwards=(parzzley.builtin.aspects.streaming.WorkingItem.commit_update,),
    )
    async def move_to_trash(self, event: parzzley.sync.aspect.events.item.ApplyUpdate):
        """
        Move the (non-directory) item to the trash bin if this reflects the most recent state.
        """
        trash_site = await event.sync_run.site_control_site(event.site, "trash")

        trash_item_dir = None
        while not trash_item_dir:
            trash_item_dir_ = parzzley.fs.item(str(uuid.uuid4()).encode())
            try:
                await trash_site.create_item(trash_item_dir_, parzzley.fs.ItemType.DIRECTORY, recursive=True)
                trash_item_dir = trash_item_dir_
            except parzzley.fs.Site.ItemExistsError:
                pass

        await trash_site.create_item(parzzley.fs.item(trash_item_dir, b"path"), parzzley.fs.ItemType.FILE)
        await trash_site.write_bytes(parzzley.fs.item(trash_item_dir, b"path"), event.item.path)
        await trash_site.create_item(parzzley.fs.item(trash_item_dir, b"trashed_at"), parzzley.fs.ItemType.FILE)
        await trash_site.write_bytes(parzzley.fs.item(trash_item_dir, b"trashed_at"), str(time.time()).encode())
        await event.site.move_item(event.item, trash_item_dir(b"item"), to_site=trash_site)
        self._DATA__LOG_REMOVAL.set(event, True)

    @parzzley.sync.aspect.event_handler()
    async def log_removal(self, event: parzzley.sync.aspect.events.item.RefreshItemsBook):  # TODO odd event
        """
        Log removals.
        """
        if self._DATA__LOG_REMOVAL.get(event):
            self._DATA__LOG_REMOVAL.set(event, False)
            event.log.info("Removed")


class DetectRemoval(parzzley.sync.aspect.Aspect):
    """
    Detect a change on the main stream when an item was removed on this site (and not modified on any other site).
    """

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsStream(""), parzzley.sync.aspect.only_if.ItemExistsHere(False)
    )
    async def detect_changes(self, event: parzzley.sync.aspect.events.item.stream.DetectChanges):
        """
        Detect removal.
        """
        if event.item_type_after_last_sync() != parzzley.fs.ItemType.NONE:
            changed_on_other_sites = False

            for site in event.all_sites:
                if (site == event.site) or (event.item_type(site) == parzzley.fs.ItemType.NONE):
                    continue

                if event.item_type(site) == parzzley.fs.ItemType.DIRECTORY:
                    if event.item_type_after_last_sync(site) != parzzley.fs.ItemType.DIRECTORY:
                        changed_on_other_sites = True
                        break
                    continue

                if event.item_type_after_last_sync(
                    site
                ) == parzzley.fs.ItemType.NONE or event.stream_cookie_after_last_sync(site) != event.stream_cookie(
                    site
                ):
                    changed_on_other_sites = True
                    break

            if not changed_on_other_sites:
                event.mark_changed()


class CleanupTrashBin(parzzley.sync.aspect.Aspect):
    """
    Removes aged stuff from the trash bin (only for the root directory).
    """

    def __init__(self, *, trash_max_age: str | float | datetime.timedelta = "30d"):
        super().__init__()
        self.__trash_max_age = parzzley.config.file_formats.timedelta(trash_max_age).total_seconds()

    @parzzley.sync.aspect.event_handler()
    async def cleanup_trash_bin(self, event: parzzley.sync.aspect.events.item.dir.Iterated):
        """
        Clean up the trash bin.
        """
        if event.item.name is None:
            trash_site = await event.sync_run.site_control_site(event.site, "trash")
            now = time.time()
            for trash_entry in await trash_site.children(b""):
                trashed_at_file = trash_entry(b"trashed_at")
                keep_entry = False

                if await trash_site.item_exists(trashed_at_file):
                    trashed_at_str = (await trash_site.read_bytes(trashed_at_file)).decode()
                    try:
                        trashed_at = float(trashed_at_str)
                    except ValueError:
                        trashed_at = 0

                    keep_entry = trashed_at + self.__trash_max_age > now

                if not keep_entry:
                    await trash_site.remove_item(trash_entry, recursive=True)
