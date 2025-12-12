#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Sync runs. See :py:class:`SyncRun`.
"""
import datetime
import logging
import pathlib
import typing as t
import urllib.parse

import parzzley.fs.utils
import parzzley.sync.utils

if t.TYPE_CHECKING:
    import parzzley.sync.manager


_logger = logging.getLogger(__name__)


class SyncRun:
    """
    Representation of one sync run (i.e. one execution) on some volume, used inside the engine and aspects.
    For controlling a sync run from outside, see :py:mod:`parzzley.sync.control.SyncControl` instead.

    In particular, see :py:meth:`store_success_info`!
    """

    def __init__(
        self,
        *,
        manager,
        volume: "parzzley.sync.Volume",
        sites: t.Iterable["parzzley.fs.Site"],
        started_at: datetime.datetime,
    ):
        """
        :param manager: The associated manager.
        :param volume: The volume to associate with this sync run.
        :param sites: The sites of the :code:`volume` that were able to actually establish a connection.
        :param started_at: The time when this sync run has been started.
        """
        self.__volume = volume
        self.__sites = tuple(sites)
        self.__manager = manager
        self.__sn = parzzley.sync.utils.run_coroutine_in_new_thread(self.__get_next_sn(), thread_name_postfix="get sn")
        self.__id = f"{manager.id}#{volume.name}#{self.__sn}"
        self.__started_at = started_at

    @property
    def sn(self) -> int:
        """
        The serial number of this sync run.

        This will increase for each sync run on a given volume. The first sync run will be :code:`1`.
        """
        return self.__sn

    @property
    def volume_name(self) -> str:
        """
        The name of the volume associated to this sync run.
        """
        return self.__volume.name

    @property
    def manager_id(self) -> str:
        """
        This manager's identifier (the same for each run, unless it gets synced by another manager - e.g. after system
        reinstallation of the Parzzley machine).
        """
        return self.__manager.id

    @property
    def manager_var_dir(self) -> pathlib.Path:
        """
        The manager's data root directory.
        """
        return self.__manager.var_dir

    @property
    def id(self) -> str:
        """
        This sync run's identifier (always a new unique one for each run!).
        """
        return self.__id

    @property
    def sites(self) -> t.Sequence["parzzley.fs.Site"]:
        """
        The connected sites associated to this sync run. Note: This only contains sites that actually could be
        connected to.
        """
        return self.__sites

    @property
    def started_at(self) -> datetime.datetime:
        """
        The time when this sync run has been started.
        """
        return self.__started_at

    def aspects(self, site_name: str) -> t.Sequence["parzzley.sync.aspect.Aspect"]:
        """
        Return the aspects associated to this sync run for a given site.

        :param site_name: The site name.
        """
        return self.__volume.aspects(site_name)

    def volume_state_variable(
        self, name: str, *, initial_value: t.Any = None
    ) -> "parzzley.sync.manager.Manager.VolumeStateVariable":
        """
        Return a volume state variable (see also :py:class:`parzzley.sync.manager.Manager.VolumeStateVariable`).

        This variable will automatically contain the value(s) that were stored in earlier sync runs.

        Calling this method with the same name on the same instance more than once is only allowed with the same
        settings (e.g. :code:`initial_value`).

        Data stored in this variable is persisted locally in a Parzzley data directory.

        :param name: The variable name.
        :param initial_value: The initial value.
        """
        return self.__manager.volume_state_variable(self.volume_name, name, initial_value=initial_value)

    async def site_control_site(
        self, for_site: "parzzley.fs.TSiteInput", key: str, *, retain_from_former_manager: bool = False
    ) -> "parzzley.fs.Site":
        """
        Return the control site for a given key and site.

        Multiple calls with the same combination of key and site will return the same site, even beyond a sync run. So
        control sites can be used for persistence of arbitrary internal status data.

        Data will be stored on the site. It will be lost when the site itself (maybe on some remote device) gets
        replaced by an empty one, e.g. due to hardware replacement. See also :py:meth:`manager_control_site`.
        It will, depending on its configuration, also be dropped whenever a new Parzzley manager takes over (usually
        after a reinstallation of the Parzzley machine).

        :param for_site: The storage site. All data will be stored on that site (but usually invisible to the user).
        :param key: Arbitrary string.
        :param retain_from_former_manager: Whether to retain the related content even from a former manager (e.g. after
                                           a backup was restored on some site).
        """
        if isinstance(for_site, str):
            for_site = [site for site in self.__sites if site.name == for_site][0]
        root_control_site = await for_site.control_site()

        if key != ".__owners":
            owners_site = await self.site_control_site(for_site, ".__owners")
            owner_item = parzzley.fs.item(urllib.parse.quote_plus(key).encode())

            if not retain_from_former_manager:
                keep = False
                if await owners_site.item_exists(owner_item):
                    last_owner = (await owners_site.read_bytes(owner_item)).decode().strip()
                    if last_owner == self.manager_id:
                        keep = True
                if not keep:
                    try:
                        await root_control_site.remove_item(owner_item, recursive=True)
                    except parzzley.fs.Site.Exception:
                        pass

            try:
                await owners_site.create_item(owner_item, parzzley.fs.ItemType.FILE)
            except parzzley.fs.Site.Exception:
                pass
            await owners_site.write_bytes(owner_item, self.manager_id.encode())

        return await parzzley.fs.utils.site_for_key(root_control_site, key)

    async def manager_control_site(self, key: str) -> "parzzley.fs.Site":
        """
        Return the local control site for a given key.

        Multiple calls with the same combination of key and site will return the same site, even beyond a sync run. So
        control sites can be used for persistence of arbitrary internal status data.

        Manager control sites are local. They will lose their content when the Parzzley machine gets replaced or loses
        its filesystem in other ways. See also :py:meth:`site_control_site`.

        Note: This provides much flexibility, but for most cases, it is recommended to use the simpler
        :py:meth:`volume_state_variable` instead.

        :param key: Arbitrary string.
        """
        return await self.__manager._manager_control_site(key)

    async def store_success_info(self, sites: t.Iterable[parzzley.fs.TSiteInput]) -> None:
        """
        Store success info for this sync run.

        To be called after the sync run has been completed successfully.

        :param sites: The involved sites.
        """
        await self.__manager.store_success_info(self.volume_name, sites)

    async def __get_next_sn(self) -> int:
        run_counter = self.volume_state_variable("run_counter", initial_value=0)
        run_no = await run_counter.value() + 1
        await run_counter.set_value(run_no)
        return run_no
