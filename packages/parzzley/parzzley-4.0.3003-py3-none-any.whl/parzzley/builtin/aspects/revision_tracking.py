#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Revision tracking.
"""
import json

import parzzley


@parzzley.sync.aspect.register_aspect
class RevisionTracking(parzzley.sync.aspect.Aspect):
    """
    Revision tracking.
    """

    _DATA__REVISIONS_SITE = parzzley.sync.aspect.events.Data(per_site=True)

    _DATA__REVISION_ITEM = parzzley.sync.aspect.events.Data(per_site=True, per_item=True)

    _SUPPORTED_ITEM_TYPES = (parzzley.fs.ItemType.FILE,)

    def __init__(self, number_unarchived_revisions: int = 3, number_revisions_per_archive: int = 20):
        """
        :param number_unarchived_revisions: Number of revisions per file to be stored directly, not inside an archive
                                            file.
        :param number_revisions_per_archive: Number of revisions per file to be stored in one archive, before the next
                                             archive file begins.
        """
        super().__init__()
        # TODO actually use parameters
        self.__number_unarchived_revisions = number_unarchived_revisions  # pylint: disable=unused-private-member
        self.__number_revisions_per_archive = number_revisions_per_archive  # pylint: disable=unused-private-member

    @parzzley.sync.aspect.event_handler()
    async def init(self, event: parzzley.sync.aspect.events.sync_run.Prepare):
        """
        Initialize.
        """
        self._DATA__REVISIONS_SITE.set(
            event, await event.sync_run.site_control_site(event.site, "revisions", retain_from_former_manager=True)
        )

    @parzzley.sync.aspect.event_handler(parzzley.sync.aspect.only_if.ItemOnMasterSiteIsType(*_SUPPORTED_ITEM_TYPES))
    async def add_working_item_for_revision(self, event: parzzley.sync.aspect.events.item.SetUpWorkingItems):
        # TODO odd event
        """
        Set up the revision store as one additional destination.
        """
        store_revision = False
        for stream_name in event.stream_support_info.supported_streams:
            stream_event = event.to_stream_event(stream_name)  # TODO odd
            if stream_event.content_version(only_past=True) < stream_event.content_version(
                stream_event.master_site, only_past=False
            ):
                store_revision = True
                break

        if store_revision:
            revisions_site = self._DATA__REVISIONS_SITE.get(event)

            cookie = event.stream_cookie(for_site=event.master_site)
            cookie_str = json.dumps(cookie).encode()

            revision_base_dir = parzzley.fs.item((b"/" + event.item.path).replace(b"/", b"/+"))
            if not await revisions_site.item_exists(revision_base_dir):
                await revisions_site.create_item(revision_base_dir, parzzley.fs.ItemType.DIRECTORY, recursive=True)

            revision_path = None
            revision_working_path = None
            i = 1
            while revision_path is None or await revisions_site.item_exists(revision_path):
                revision_path = revision_base_dir(b"_" + cookie_str + f" #{i}".encode())
                revision_working_path = revision_base_dir(b"-" + cookie_str + f" #{i}".encode())
                i += 1

            if await revisions_site.item_exists(revision_working_path):
                await revisions_site.remove_item(revision_working_path)
            await revisions_site.create_item(revision_working_path, parzzley.fs.ItemType.FILE)
            event.add_working_item(event.site.sub_site_location(revisions_site)(revision_working_path))
            self._DATA__REVISION_ITEM.set(event, (revision_working_path, revision_path))

    @parzzley.sync.aspect.event_handler()
    async def store_working_item(self, event: parzzley.sync.aspect.events.item.RefreshItemsBook):
        """
        Handle new files in the revision store.
        """
        if (revision := self._DATA__REVISION_ITEM.get(event)) is not None:
            revisions_site = self._DATA__REVISIONS_SITE.get(event)
            revision_working_path, revision_path = revision
            await revisions_site.move_item(revision_working_path, revision_path)
