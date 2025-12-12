#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Extended attributes support.
"""
import parzzley.builtin.aspects.streaming
import parzzley.fs.utils


class XattrSynchronization(parzzley.sync.aspect.Aspect):
    """
    Extended attributes support.
    """

    _DATA__NEEDS_TAGGING = parzzley.sync.aspect.events.Data(False, per_stream=True, per_site=True)

    _SUPPORTED_ITEM_TYPES = (parzzley.fs.ItemType.DIRECTORY, parzzley.fs.ItemType.FILE)

    _XATTR_TAG_KEY = b"user.__parzzley_f"

    @parzzley.sync.aspect.event_handler()
    async def stream_support(self, event: parzzley.sync.aspect.events.sync_run.DetermineStreamSupport):
        """
        Declare stream support.
        """
        event.set_stream_support("xattrs", self._SUPPORTED_ITEM_TYPES)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsItemTypeOnStreamMasterSiteSupportedByStream(),
        parzzley.sync.aspect.only_if.IsStream("xattrs"),
    )
    async def detect_changes(self, event: parzzley.sync.aspect.events.item.stream.DetectChanges):
        """
        Detect changes.
        """
        if event.stream_cookie() != event.stream_cookie_after_last_sync():
            xattrs = parzzley.fs.utils.deserialize_bytes_dict(await event.site.read_bytes(event.item, "xattrs"))

            if self._XATTR_TAG_KEY not in xattrs:
                self._DATA__NEEDS_TAGGING.set(event, True)
                if not xattrs:
                    event.mark_refresh_needed()
                    return

            event.mark_changed()
            event.mark_all_last_involved_sites_changed_if_this_is_not_one_of_them()

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsItemTypeOnStreamMasterSiteSupportedByStream(),
        parzzley.sync.aspect.only_if.IsStream("xattrs"),
    )
    async def collect_source(self, event: parzzley.sync.aspect.events.item.stream.CollectSourceStreamables):
        """
        Collect the source streamable.
        """
        event.add_stream_pipe(self._PatchDictPipe)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsItemTypeOnStreamMasterSiteSupportedByStream(),
        parzzley.sync.aspect.only_if.IsStream("xattrs"),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(),
    )
    async def collect_destination(self, event: parzzley.sync.aspect.events.item.stream.CollectDestinationStreamables):
        """
        Add a destination streamable for the master site as well if the item was marked this way.
        """
        if self._DATA__NEEDS_TAGGING.get(event):
            event.add_destination_streamable(await event.site.write_streamable(event.item, event.stream_name))

    @parzzley.sync.aspect.event_handler(parzzley.sync.aspect.only_if.IsStream("xattrs"))
    async def disable_change_detection(
        self, event: parzzley.sync.aspect.events.item.stream.CollectDestinationStreamables
    ):
        """
        Disable change detection for the xattrs stream.
        """
        event.disable_change_detection()

    class _PatchDictPipe(parzzley.sync.aspect.events.item.stream.CollectSourceStreamables.FullContentPipe):

        async def pipe_content(self, data):
            return parzzley.fs.utils.serialize_bytes_dict(
                {**parzzley.fs.utils.deserialize_bytes_dict(data), XattrSynchronization._XATTR_TAG_KEY: b""}
            )
