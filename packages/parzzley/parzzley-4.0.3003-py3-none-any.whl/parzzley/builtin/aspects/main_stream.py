#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Main stream support.
"""
import parzzley


class MainStreamSynchronization(parzzley.sync.aspect.Aspect):
    """
    Main stream specific behavior.
    """

    _SUPPORTED_ITEM_TYPES = (parzzley.fs.ItemType.FILE, parzzley.fs.ItemType.SYMLINK)

    @parzzley.sync.aspect.event_handler()
    async def stream_support(self, event: parzzley.sync.aspect.events.sync_run.DetermineStreamSupport):
        """
        Declare stream support.
        """
        event.set_stream_support("", self._SUPPORTED_ITEM_TYPES, cookies_are_move_stable=True)

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.IsItemTypeOnStreamMasterSiteSupportedByStream(),
        parzzley.sync.aspect.only_if.IsStream(""),
    )
    async def detect_changes(self, event: parzzley.sync.aspect.events.item.stream.DetectChanges):
        """
        Detect changes.
        If a change was detected, and this site was not involved in the last successful sync run on this item, then mark
        one of these as changed as well (so we would never override other versions but raise a conflict instead later).

        The check around the involved sites is sufficient to do on the main stream only, as the potential conflict would
        take the desired effect on the entire item.
        """
        if event.stream_cookie() != event.stream_cookie_after_last_sync():
            event.mark_changed()
            event.mark_all_last_involved_sites_changed_if_this_is_not_one_of_them()

    @parzzley.sync.aspect.event_handler(
        parzzley.sync.aspect.only_if.ItemHereIsType(parzzley.fs.ItemType.ALIEN),
        parzzley.sync.aspect.only_if.IsStream(""),
    )
    async def alien_detect_changes(self, event: parzzley.sync.aspect.events.item.stream.DetectChanges):
        """
        Always detect alien items as changed.
        They will either be mostly ignored later, or raise a type conflict.
        """
        event.mark_changed()
