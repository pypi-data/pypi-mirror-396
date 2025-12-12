#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Exclude paths.
"""
import re

import parzzley


@parzzley.sync.aspect.register_aspect
class ExcludePaths(parzzley.sync.aspect.Aspect):
    """
    Exclude paths by a regular expression pattern.
    """

    def __init__(self, *, pattern: str):
        super().__init__()
        self.__pattern = re.compile(pattern)

    @parzzley.sync.aspect.event_handler()
    async def decide_to_skip(self, event: parzzley.sync.aspect.events.item.DecideToSkip):
        """
        Check whether to skip this item by applying the regexp pattern to its path.
        """
        if self.__pattern.fullmatch(f"/{repr(event.item.path)[2:-1]}"):
            event.skip_item()
