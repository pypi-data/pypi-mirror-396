#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Item type detection.
"""
import parzzley


class DetermineItemTypes(parzzley.sync.aspect.Aspect):
    """
    Determines the item type for this site by querying its :py:meth:`parzzley.fs.Site.item_type_by_cookie`.
    """

    @parzzley.sync.aspect.event_handler()
    async def determine_item_type(self, event: parzzley.sync.aspect.events.item.DetermineType):
        """
        Determine the item type (by asking the site to interpret the main stream cookie).
        """
        event.set_item_type(event.site.item_type_by_cookie(event.stream_cookie()))
