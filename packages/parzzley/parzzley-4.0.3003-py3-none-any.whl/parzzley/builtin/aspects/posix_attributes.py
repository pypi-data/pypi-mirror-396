#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
POSIX attributes support.
"""
import json

import parzzley


class PosixAttributesSynchronization(parzzley.sync.aspect.Aspect):
    """
    Synchronization of some POSIX file attributes.
    """

    _SUPPORTED_ITEM_TYPES = (parzzley.fs.ItemType.FILE, parzzley.fs.ItemType.DIRECTORY, parzzley.fs.ItemType.SYMLINK)

    @parzzley.sync.aspect.event_handler()
    async def stream_support(self, event: parzzley.sync.aspect.events.sync_run.DetermineStreamSupport):
        """
        Declare stream support.
        """
        event.set_stream_support("posix", self._SUPPORTED_ITEM_TYPES)

    @parzzley.sync.aspect.event_handler(parzzley.sync.aspect.only_if.IsStream("posix"))
    async def comparator(self, event: parzzley.sync.aspect.events.item.stream.DetermineComparator):
        """
        Compare POSIX file attribute streams.
        """

        async def comparator_(_a, _b):
            a_dict, b_dict = json.loads(await _a.read_bytes()), json.loads(await _b.read_bytes())
            a_mtime, b_mtime = a_dict.pop("mtime", 0) / 1000**3, b_dict.pop("mtime", 0) / 1000**3
            return (a_mtime - b_mtime) <= 2 and a_dict == b_dict

        event.set_comparator(comparator_)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsItemTypeOnStreamMasterSiteSupportedByStream(),
        parzzley.sync.aspect.only_if.IsStream("posix"),
        parzzley.sync.aspect.only_if.ItemExistsHere(),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(of_stream=""),
    )
    async def detect_changes(self, event: parzzley.sync.aspect.events.item.stream.DetectChanges):
        """
        Mark the main stream master as changed for the posix stream if it was marked as changed for the main stream.
        """
        main_stream_event = event.to_stream_event("")
        if main_stream_event.content_version(only_past=True) != main_stream_event.content_version(only_past=False):
            event.mark_changed()

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsStream("posix"),
        parzzley.sync.aspect.only_if.ThisIsMasterSite(of_stream=""),
        parzzley.sync.aspect.only_if.ItemHereIsType(parzzley.fs.ItemType.DIRECTORY),
    )
    async def resolve_conflicts_on_directories(
        self, event: parzzley.sync.aspect.events.item.stream.TryResolveConflicts
    ):
        """
        Resolves conflicts on directories (that will come up regularly, but are not really relevant).
        """
        event.resolve_conflicts(event.site)

    @parzzley.sync.aspect.event_handler(parzzley.sync.aspect.only_if.IsStream("posix"))
    async def disable_change_detection(
        self, event: parzzley.sync.aspect.events.item.stream.CollectDestinationStreamables
    ):
        """
        Disable change detection for the posix stream.
        """
        event.disable_change_detection()
