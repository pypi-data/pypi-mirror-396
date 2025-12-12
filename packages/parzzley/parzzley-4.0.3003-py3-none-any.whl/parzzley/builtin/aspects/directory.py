#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Directory support.
"""
import uuid

import parzzley.builtin.aspects.streaming


class ListDirectory(parzzley.sync.aspect.Aspect):
    """
    Retrieves the list of all item children names.
    """

    @parzzley.sync.aspect.event_handler(parzzley.sync.aspect.only_if.ItemHereIsType(parzzley.fs.ItemType.DIRECTORY))
    async def list_dir(self, event: parzzley.sync.aspect.events.item.dir.List):
        """
        List all children of this directory.
        """
        event.add_child_names(await event.site.child_names(event.item))


class MarkChangedIfItemIsDirectoryButWasNotBefore(parzzley.sync.aspect.Aspect):
    """
    Marks directories as changed if they were not there (or not a directory) last time.
    """

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsStream(""),
        parzzley.sync.aspect.only_if.ItemHereIsType(parzzley.fs.ItemType.DIRECTORY),
    )
    async def detect_changes(self, event: parzzley.sync.aspect.events.item.stream.DetectChanges):
        """
        Detect changes.
        """
        if event.item_type_after_last_sync() != parzzley.fs.ItemType.DIRECTORY:
            event.mark_changed()


class DirectoryCreation(parzzley.sync.aspect.Aspect):
    """
    Creates new directories.
    """

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemExistsHere(False),
        parzzley.sync.aspect.only_if.ItemOnMasterSiteIsType(parzzley.fs.ItemType.DIRECTORY),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
    )
    async def create_dir(self, event: parzzley.sync.aspect.events.item.PrepareUpdating):
        """
        Create directory.
        """
        await event.site.create_item(event.item, parzzley.fs.ItemType.DIRECTORY)
        event.mark_effective()


class RemoveForReplacement(parzzley.sync.aspect.Aspect):
    """
    Cleanup sites for replacements, often after resolved conflicts.
    """

    _DATA__ROLLBACK_DIR = parzzley.sync.aspect.events.Data(per_site=True, per_item=True)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemExistsHere(),
        parzzley.sync.aspect.only_if.ItemExistsOnMasterSite(),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
    )
    async def prepare_updating(self, event: parzzley.sync.aspect.events.item.PrepareUpdating):
        """
        Remove (with rollback data) the item if its item type is incompatible to the master site's one.
        """
        if event.item_type() != event.item_type(event.master_site):
            site_rollback_site = await event.sync_run.site_control_site(event.site, "rollback")
            item_rollback_dir = parzzley.fs.item(str(uuid.uuid4()).encode())
            item_rollback_path_file = item_rollback_dir(b"path")
            item_rollback_path_file_working = item_rollback_dir(b"~path")
            item_rollback_origin = item_rollback_dir(b"origin")
            await site_rollback_site.create_item(item_rollback_dir, parzzley.fs.ItemType.DIRECTORY)
            RemoveForReplacement._DATA__ROLLBACK_DIR.set(event, item_rollback_dir)
            await site_rollback_site.create_item(item_rollback_path_file_working, parzzley.fs.ItemType.FILE)
            await site_rollback_site.write_bytes(item_rollback_path_file_working, event.item.path)
            await site_rollback_site.move_item(item_rollback_path_file_working, item_rollback_path_file)

            await event.site.move_item(event.item, item_rollback_origin, to_site=site_rollback_site)

            if event.item_type(event.master_site) == parzzley.fs.ItemType.DIRECTORY:
                await event.site.create_item(event.item, parzzley.fs.ItemType.DIRECTORY)

    @parzzley.sync.aspect.event_handler()  # TODO odd event
    async def remove_rollback_data_after_finished(self, event: parzzley.sync.aspect.events.item.RefreshItemsBook):
        """
        Remove rollback data after item sync is finished.
        """
        if item_rollback_dir := RemoveForReplacement._DATA__ROLLBACK_DIR.get(event):
            site_rollback_site = await event.sync_run.site_control_site(event.site, "rollback")
            await site_rollback_site.remove_item(item_rollback_dir, recursive=True)


class RollbackCrashedTransfers(parzzley.sync.aspect.Aspect):
    """
    Rollback crashed transfers.
    """

    @parzzley.sync.aspect.event_handler()
    async def prepare_sync_run(self, event: parzzley.sync.aspect.events.sync_run.Prepare):
        """
        Rollback crashed transfers.
        """
        site_rollback_site = await event.sync_run.site_control_site(event.site, "rollback")
        for item_rollback_dir in await site_rollback_site.children(b""):
            item_rollback_path_file = item_rollback_dir(b"path")
            item_rollback_origin = item_rollback_dir(b"origin")
            if await site_rollback_site.item_exists(item_rollback_path_file) and await site_rollback_site.item_exists(
                item_rollback_origin
            ):
                item = parzzley.fs.item((await site_rollback_site.read_bytes(item_rollback_path_file)).decode())
                if not await event.site.item_exists(item) and await event.site.item_exists(item.parent):
                    item_origin = event.site.sub_site_location(site_rollback_site)(item_rollback_origin.path)
                    await event.site.move_item(item_origin, item)

            await site_rollback_site.remove_item(item_rollback_dir, recursive=True)
