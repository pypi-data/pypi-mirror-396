#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Pull&purge is a special way to configure a Parzzley volume. There are one or more sources and one sink. Files will
be transferred from the sources to the sink and removed on the source site after that.
"""
import parzzley.builtin.aspects.default_sync
import parzzley.builtin.aspects.directory
import parzzley.builtin.aspects.remove
import parzzley.builtin.aspects.streaming


@parzzley.sync.aspect.register_aspect
class PullAndPurgeSyncSink(parzzley.sync.aspect.Aspect):  # TODO forbid more than one sink!
    """
    Pull&purge sync sink. There must be exactly one in a pull&purge volume (and the other sites must be sources).
    """

    _MOVABLE_ITEM_TYPES = (parzzley.fs.ItemType.FILE, parzzley.fs.ItemType.SYMLINK)  # TODO  test ALIEN handling?

    def __init__(self):
        super().__init__(
            parzzley.builtin.aspects.default_sync.DefaultBase(),
            parzzley.builtin.aspects.directory.DirectoryCreation(),
            parzzley.builtin.aspects.remove.CleanupTrashBin(),
            parzzley.builtin.aspects.streaming.WorkingItem(),
        )

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsStream(""),
        parzzley.sync.aspect.only_if.ItemHereIsType(parzzley.fs.ItemType.DIRECTORY),
    )
    async def detect_changes(self, event: parzzley.sync.aspect.events.item.stream.DetectChanges):
        """
        Mark each directory as changed.
        """
        event.mark_changed()

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsStream(""),
        parzzley.sync.aspect.only_if.ItemExistsHere(),
        parzzley.sync.aspect.only_if.ItemOnMasterSiteIsType(*_MOVABLE_ITEM_TYPES),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(False),
    )
    async def rename_already_existing(self, event: parzzley.sync.aspect.events.item.stream.MasterSiteDetermined):
        """
        Rename an already existing entry to some new name.
        """
        i = 1
        while True:
            new_item = parzzley.fs.item(event.item.path + f" (old #{i})".encode())
            if not await event.site.item_exists(new_item):
                break
            i += 1

        await event.site.move_item(event.item, new_item)
        event.set_item_info(parzzley.fs.ItemType.NONE, None)


@parzzley.sync.aspect.register_aspect
class PullAndPurgeSyncSource(parzzley.sync.aspect.Aspect):
    """
    Pull&purge sync source.
    """

    def __init__(self):
        super().__init__(parzzley.builtin.aspects.default_sync.DefaultBase())

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemHereIsType(*PullAndPurgeSyncSink._MOVABLE_ITEM_TYPES),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(),
    )
    async def remove(self, event: parzzley.sync.aspect.events.item.ApplyUpdate):
        """
        Remove the file in the source site.
        """
        event.log.debug("Removed on %s", event.site.name)
        await event.site.remove_item(event.item)
