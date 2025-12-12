#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Aspects for attaching sites to the current manager and detecting foreign sites.
"""
import typing as t

import parzzley


class AttachSites(parzzley.sync.aspect.Aspect):
    """
    Attaches sites and detects foreign sites.
    """

    _LAST_SYNC_RUN_SN_FILE = parzzley.fs.item(b"_last_sync_run_sn")
    _EARLY_LAST_SYNC_RUN_SN_FILE = parzzley.fs.item(b"-last_sync_run_sn")
    _WORKING_LAST_SYNC_RUN_SN_FILE = parzzley.fs.item(b"~last_sync_run_sn")
    _MANAGED_BY_FILE = parzzley.fs.item(b"_managed_by")
    _EXCEPTED_LAST_SYNC_RUN_SN_PER_SITE_KEY = "expected_last_sync_run_sn_per_site"

    @parzzley.sync.aspect.event_handler()
    async def attach_site(self, event: parzzley.sync.aspect.events.sync_run.Prepare):
        """
        Attaches sites.
        """
        if not await self.__check_whether_to_stay_attached(event):
            await self.__take_over_site_control(event)
        await self.__store_current_sync_run(event)

    async def __check_whether_to_stay_attached(self, event: parzzley.sync.aspect.events.sync_run.Prepare) -> bool:
        control_site = await event.site.control_site()
        site_file = parzzley.fs.item(f"_{event.site.name}".encode())
        early_site_file = parzzley.fs.item(f"-{event.site.name}".encode())

        if not await control_site.item_exists(self._MANAGED_BY_FILE):
            return False

        if (
            await control_site.read_bytes(self._MANAGED_BY_FILE)
        ).decode().strip() != f"{event.sync_run.manager_id}/{event.sync_run.volume_name}":
            return False

        if (
            site_last_sync_run_sn := await self.__read_last_sync_run_sn(
                control_site, (self._EARLY_LAST_SYNC_RUN_SN_FILE, self._LAST_SYNC_RUN_SN_FILE)
            )
        ) is None:
            return False

        if (
            last_sync_run_sn := await self.__read_last_sync_run_sn(
                await event.sync_run.manager_control_site(AttachSites._EXCEPTED_LAST_SYNC_RUN_SN_PER_SITE_KEY),
                (early_site_file, site_file),
            )
        ) is None:
            return False

        return site_last_sync_run_sn >= last_sync_run_sn

    async def __read_last_sync_run_sn(
        self, site: parzzley.fs.Site, from_items: t.Iterable[parzzley.fs.Item]
    ) -> int | None:
        for file in from_items:
            if await site.item_exists(file):
                return int(await site.read_bytes(file))
        return None

    async def __take_over_site_control(self, event: parzzley.sync.aspect.events.sync_run.Prepare) -> None:
        control_site = await event.site.control_site()

        await event.remove_site_from_items_books(event.site)

        removed_old = False
        for file in (
            AttachSites._MANAGED_BY_FILE,
            AttachSites._EARLY_LAST_SYNC_RUN_SN_FILE,
            AttachSites._LAST_SYNC_RUN_SN_FILE,
        ):
            if await control_site.item_exists(file):
                removed_old = True
                await control_site.remove_item(file)

        await control_site.create_item(AttachSites._MANAGED_BY_FILE, parzzley.fs.ItemType.FILE)
        await control_site.write_bytes(
            AttachSites._MANAGED_BY_FILE, f"{event.sync_run.manager_id}/{event.sync_run.volume_name}".encode()
        )

        if removed_old:
            event.log.warning(
                "This Parzzley instance takes over control from an earlier one for site %s.", repr(event.site.name)
            )
        else:
            event.log.info("This is the first sync run for site %s.", repr(event.site.name))

    async def __store_current_sync_run(self, event: parzzley.sync.aspect.events.sync_run.Prepare) -> None:
        await self.__write_last_sync_run_sn(
            await event.site.control_site(),
            (self._WORKING_LAST_SYNC_RUN_SN_FILE, self._EARLY_LAST_SYNC_RUN_SN_FILE, self._LAST_SYNC_RUN_SN_FILE),
            event.sync_run.sn,
        )

        await self.__write_last_sync_run_sn(
            await event.sync_run.manager_control_site(AttachSites._EXCEPTED_LAST_SYNC_RUN_SN_PER_SITE_KEY),
            (f"~{event.site.name}".encode(), f"-{event.site.name}".encode(), f"_{event.site.name}".encode()),
            event.sync_run.sn,
        )

    async def __write_last_sync_run_sn(
        self,
        site: parzzley.fs.Site,
        with_items: tuple[parzzley.fs.TItemInput, parzzley.fs.TItemInput, parzzley.fs.TItemInput],
        value: int,
    ) -> None:
        try:
            await site.remove_item(with_items[0])
        except parzzley.fs.Site.Exception:
            pass
        await site.create_item(with_items[0], parzzley.fs.ItemType.FILE)

        await site.write_bytes(with_items[0], str(value).encode())
        await site.move_item(with_items[0], with_items[1])
        await site.move_item(with_items[1], with_items[2])
