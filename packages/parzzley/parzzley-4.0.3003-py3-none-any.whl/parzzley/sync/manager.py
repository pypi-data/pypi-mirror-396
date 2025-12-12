#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Parzzley manager. See :py:class:`Manager`.
"""
import asyncio
import contextlib
import copy
import dataclasses
import datetime
import json
import logging
import os
import pathlib
import socket
import time
import traceback
import typing as t
import urllib.parse
import uuid

import parzzley.config.loader
import parzzley.fs.utils
import parzzley.sync.control
import parzzley.sync.engine
import parzzley.sync.logger
import parzzley.sync.run


_logger = logging.getLogger(__name__)


class Manager:
    """
    A manager allows to execute the syncing of given configuration.

    Its context must be entered (:code:`with`-block) in order to use it. You must enter its context only once.

    Each manager is associated to a 'control site' (basically a filesystem location - usually somewhere in the local
    filesystem's :file:`/var` directory - where Parzzley stores various internal state information). Sync executions of
    a particular volume should always use the same control site. A fresh control site will drop state information, which
    potentially incurs a much longer time for syncing and maybe further inconveniences like conflicts.
    """

    _MANAGERS = {}

    def __init__(self, *, id_hint: str, config: "parzzley.config.Configuration"):
        """
        Do not use directly. See :py:meth:`for_config_directory`.

        :param id_hint: If this is a new manager (i.e. there never was a manager using the same control site), the id
                        hint will be used as part of its manager id (see :py:attr:`id`).
        :param config: All specified configuration.
        """
        self.__id_hint = id_hint
        self.__control_site = None
        self.__control_site_backend = None
        self.__var_dir = None
        self.__config = config
        self.__id = None
        self.__volume_state_variables = {}

    async def __aenter__(self):
        if self.__var_dir is not None:
            raise RuntimeError("you must not use a manager more than once")

        var_root_dir = (
            pathlib.Path("/var/local/parzzley")
            if (os.geteuid() == 0)
            else pathlib.Path("~/.local/parzzley").expanduser()
        )

        if not var_root_dir.exists():
            var_root_dir.mkdir(parents=True, mode=0o700)
            (var_root_dir / "README.txt").write_text(
                "This is the local Parzzley state data storage.\nYou should not include it in your backups."
            )

        self.__var_dir = var_root_dir / urllib.parse.quote_plus(self.__id_hint)
        self.__var_dir.mkdir(exist_ok=True)
        self.__control_site_backend = await parzzley.fs.backend_by_kind("local").connect(path=self.__var_dir)
        self.__control_site = parzzley.fs.Site("", self.__control_site_backend)

        id_item = parzzley.fs.item(b"id")
        if await self.__control_site.item_exists(id_item):
            self.__id = (await self.__control_site.read_bytes(id_item)).decode()
        else:
            self.__id = f"{socket.getfqdn()}#{self.__id_hint}#{uuid.uuid4()}"
            await self.__control_site.create_item(id_item, parzzley.fs.ItemType.FILE)
            await self.__control_site.write_bytes(id_item, self.__id.encode())

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await parzzley.fs.backend_by_kind("local").disconnect(self.__control_site_backend)

    def __enter__(self):
        asyncio.new_event_loop().run_until_complete(self.__aenter__())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.new_event_loop().run_until_complete(self.__aexit__(exc_type, exc_val, exc_tb))

    @property
    def var_dir(self) -> pathlib.Path:
        """
        This manager's data root directory.
        """
        self.__verify_entered()
        return self.__var_dir

    @staticmethod
    def for_config_directory(config_dir: pathlib.Path | str) -> "Manager":
        """
        Return a manager for a given config directory.

        :param config_dir: The Parzzley config directory.
        """
        config_dir = pathlib.Path(config_dir).resolve()

        if not config_dir.exists():
            raise IOError(f"config directory {str(config_dir)!r} does not exist")

        if not (result := Manager._MANAGERS.get(config_dir)):
            result = Manager._MANAGERS[config_dir] = Manager(
                id_hint=str(config_dir), config=parzzley.config.file_formats.read_configuration(config_dir)
            )

        return result

    @property
    def volumes(self) -> t.Sequence["parzzley.config.Volume"]:
        """
        All specified volumes.
        """
        return self.__config.volumes

    @property
    def id(self) -> str:
        """
        The sync manager id.

        This id is permanent for a given control site (as long as it does not lose its data) and globally unique.
        """
        self.__verify_entered()
        return self.__id

    async def start_sync(
        self, prepared_sync_setup: "Manager.PreparedSyncSetup"
    ) -> "parzzley.sync.control.SyncControl|None":
        """
        Start a sync (and return a control object for watching or canceling it). The actual sync run will happen in
        background.

        You need to use :py:meth:`prepare_sync` before in order to get the required argument.

        If you do not need all this control flexibility, see :py:meth:`run_sync` instead.

        :param prepared_sync_setup: The prepared sync setup to execute.
        """
        if len(prepared_sync_setup.connected_sites) >= 2:
            sites = dict(prepared_sync_setup.connected_sites.values())
            new_sync_run = parzzley.sync.run.SyncRun(
                manager=self, volume=prepared_sync_setup.volume, sites=sites.keys(), started_at=datetime.datetime.now()
            )
            engine = parzzley.sync.engine.Engine(
                sync_run=new_sync_run, sites=sites, loggings=prepared_sync_setup.loggings
            )
            engine.start()
            return engine.sync_control

    def run_sync(
        self, s: "parzzley.config.Volume|Manager.PreparedSyncSetup"
    ) -> "parzzley.sync.control.SyncControl|None":
        """
        Run a sync (and return a control object that contains some auxiliary information).

        :param s: The volume to sync (or a prepared sync setup as returned by :py:meth:`prepare_sync`).
        """
        return asyncio.run(self.__run_sync__async(s))

    @contextlib.asynccontextmanager
    async def prepare_sync(
        self,
        volume_config: "parzzley.config.Volume",
        *,
        require_one_of: t.Iterable[parzzley.fs.TSiteInput] | None = None,
    ) -> t.AsyncGenerator["PreparedSyncSetup"]:
        """
        For a given volume configuration, try to connect to all its sites and return a prepared sync setup as required
        for :py:meth:`start_sync`.

        You must always call this function right before starting a sync and use that fresh instance.

        :param volume_config: The volume configuration.
        :param require_one_of: If none of these sites are able to connect, then do not even try to connect the other
                               ones, but continue with an empty connection list instead.
        """
        self.__verify_entered()
        require_one_of = None if require_one_of is None else set(parzzley.fs.site_name(_) for _ in require_one_of)
        volume = parzzley.config.loader.load_volume(volume_config)
        loggings = tuple(parzzley.config.loader.load_logging(_) for _ in self.__config.loggings)

        require_one_of_site_setups = [
            site_setup
            for site_setup in volume.site_setups
            if require_one_of is None or site_setup.name in require_one_of
        ]
        require_one_of_site_other_setups = [
            site_setup for site_setup in volume.site_setups if site_setup not in require_one_of_site_setups
        ]

        sites: dict["parzzley.fs.SiteSetup", Manager._TSiteTuple] = dict(
            await asyncio.gather(*[self.__try_connect(site_setup) for site_setup in require_one_of_site_setups])
        )

        try:
            for site_setup, (site, site_context_manager) in list(sites.items()):
                if not site:
                    sites.pop(site_setup)
                    await site_context_manager.__aexit__(None, None, None)

            if len(sites) > 0:
                sites.update(
                    dict(
                        await asyncio.gather(
                            *[self.__try_connect(site_setup) for site_setup in require_one_of_site_other_setups]
                        )
                    )
                )

                for site_setup, (site, site_context_manager) in list(sites.items()):
                    if not site:
                        sites.pop(site_setup)
                        await site_context_manager.__aexit__(None, None, None)

            yield Manager.PreparedSyncSetup(volume_config, volume, sites, loggings)
            await self.__emit_not_synced_warnings(volume_config, loggings)

        finally:
            for site_setup, (site, site_context_manager) in list(sites.items()):
                try:
                    await site_context_manager.__aexit__(None, None, None)
                except Exception:  # pylint: disable=broad-exception-caught
                    _logger.debug(traceback.format_exc())

    async def store_success_info(self, volume_name: str, sites: t.Iterable[parzzley.fs.TSiteInput]) -> None:
        """
        See :py:meth:`parzzley.sync.run.SyncRun.store_success_info`.
        """
        now = time.time()
        site_success_info_var = self.__site_success_info_variable(volume_name)
        site_success_info = await site_success_info_var.value()
        for site in sites:
            site_success_info[parzzley.fs.site_name(site)] = now, True
        await site_success_info_var.set_value(site_success_info)

    async def _manager_control_site(self, key: str) -> "parzzley.fs.Site":
        """
        See :py:meth:`parzzley.sync.run.SyncRun.manager_control_site`.
        """
        self.__verify_entered()
        return await parzzley.fs.utils.site_for_key(self.__control_site, key)

    def volume_state_variable(
        self, volume_name: str, name: str, *, initial_value: t.Any = None
    ) -> "Manager.VolumeStateVariable":
        """
        See :py:meth:`parzzley.sync.run.SyncRun.volume_state_variable`.
        """
        self.__verify_entered()
        initial_value = copy.deepcopy(initial_value)
        key = name, volume_name
        settings = (initial_value,)

        if (result_tuple := self.__volume_state_variables.get(key, self)) is self:
            result = Manager.VolumeStateVariable(self._manager_control_site, volume_name, name, initial_value)
            self.__volume_state_variables[key] = result, settings
        else:
            if settings != result_tuple[1]:
                raise ValueError(
                    f"volume state variable {name!r} already exists on {volume_name!r} with different" f" settings"
                )
            result = result_tuple[0]

        return result

    def __verify_entered(self):
        if self.__id is None:
            raise RuntimeError("you must not use a manager outside of its context")

    def __site_success_info_variable(self, volume_name: str) -> "Manager.VolumeStateVariable":
        return self.volume_state_variable(volume_name, "site_success_info", initial_value={})

    def __last_warned_info_variable(self, volume_name: str) -> "Manager.VolumeStateVariable":
        return self.volume_state_variable(volume_name, "last_warned_info", initial_value={})

    async def __run_sync__async(
        self, s: "parzzley.config.Volume|Manager.PreparedSyncSetup"
    ) -> "parzzley.sync.control.SyncControl|None":
        async with contextlib.AsyncExitStack() as stack:
            if isinstance(s, parzzley.config.Volume):
                s = await stack.enter_async_context(self.prepare_sync(s))
            if not isinstance(s, Manager.PreparedSyncSetup):
                raise ValueError(f"invalid input {s!r}")

            if not (sync_control := await self.start_sync(s)):
                return

            sync_control.wait_finished()
            if not sync_control.was_successful:
                raise RuntimeError("critical problems occurred during sync")

            return sync_control

    _TSiteTuple = tuple["parzzley.fs.Site|None", "parzzley.fs.SiteContextManager"]
    _TFullSiteTuple = tuple["parzzley.fs.SiteSetup", _TSiteTuple]

    @staticmethod
    async def __try_connect(site_setup: "parzzley.fs.SiteSetup") -> _TFullSiteTuple:
        site_context_manager = site_setup.connect()
        site = await site_context_manager.__aenter__()  # pylint: disable=unnecessary-dunder-call
        return site_setup, (site, site_context_manager)

    async def __emit_not_synced_warnings(
        self, volume_config: parzzley.config.Volume, loggings: t.Iterable["parzzley.sync.logger.Logging"]
    ) -> None:
        # pylint: disable=too-many-locals
        site_success_info_variable = self.__site_success_info_variable(volume_config.name)
        last_warned_info_variable = self.__last_warned_info_variable(volume_config.name)

        old_site_success_info = await site_success_info_variable.value()
        old_last_warned_info = await last_warned_info_variable.value()
        now = time.time()
        site_success_info = {
            site.name: old_site_success_info.get(site.name, (now, False)) for site in volume_config.sites
        }
        await site_success_info_variable.set_value(site_success_info)

        warn_entries = []
        last_warned_info = {}
        for site in volume_config.sites:
            last_warned = last_warned_info[site.name] = old_last_warned_info.get(site.name, 0)
            last_ago = now - site_success_info[site.name][0]
            if site.warn_after is not None and last_ago > site.warn_after.total_seconds():
                if last_warned + site.warn_after.total_seconds() < now:
                    last_warned_info[site.name] = now
                    for factor, unit in ((24 * 60 * 60, "days"), (60 * 60, "hours"), (60, "minutes")):
                        if last_ago > 2 * factor:
                            not_synced_for_str = f"{int(last_ago / factor)} {unit}"
                            break
                    else:
                        not_synced_for_str = f"{int(last_ago)} seconds"
                    warn_entries.append(
                        parzzley.sync.logger.Entry(
                            message=f"The site {site.name!r} in volume {volume_config.name!r} was not synchronized for"
                            f" {not_synced_for_str}.",
                            message_args=(),
                            severity=parzzley.sync.logger.Severity.WARNING,
                            item=None,
                            stream=None,
                        )
                    )

        for logging_ in loggings:
            logging_.emit(None, warn_entries)
        await last_warned_info_variable.set_value(last_warned_info)

    @dataclasses.dataclass(frozen=True)
    class PreparedSyncSetup:
        """
        A prepared sync setup. Such objects are returned by :py:meth:`Manager.prepare_sync` and used for
        :py:meth:`Manager.start_sync`.
        """

        #: The volume config to sync.
        volume_config: "parzzley.config.Volume"

        #: The volume to sync.
        volume: "parzzley.sync.Volume"

        #: All sites that were actually able to connect.
        connected_sites: dict["parzzley.fs.SiteSetup", "_TSiteTuple"]

        #: The loggings.
        loggings: t.Sequence["parzzley.sync.logger.Logging"]

    class VolumeStateVariable:
        """
        A persistent volume state variable. Used for storing arbitrary state data about a sync volume, in order to make
        it available for later sync runs on that volume.

        Each variable could be used for keeping a single value, but also as a key/value-store (by specifying a
        :code:`key`).

        Data stored in this variable is persisted locally in a Parzzley data directory. It will stay there as long as
        the local filesystem stays intact.
        """

        def __init__(
            self,
            manager_control_site: t.Callable[[str], t.Coroutine[t.Any, t.Any, "parzzley.fs.Site"]],
            volume_name: str,
            name: str,
            initial_value: t.Any,
        ):
            """
            Do not use directly. See also :py:meth:`parzzley.sync.run.SyncRun.volume_state_variable`.
            """
            super().__init__()
            self.__manager_control_site = manager_control_site
            self.__volume_name = volume_name
            self.__name = name
            self.__initial_value = initial_value

        async def value(self, *, key: str = "") -> t.Any:
            """
            Return the current value of this variable.

            :param key: The key. Leave to default for single value storage.
            """
            control_site = await self.__control_site()
            await self.__promote_early_file_to_final_file(control_site, key)
            value_item = parzzley.fs.item(f"_{urllib.parse.quote_plus(key)}".encode())

            if await control_site.item_exists(value_item):
                return json.loads(await control_site.read_bytes(value_item))
            return copy.deepcopy(self.__initial_value)

        async def set_value(self, value: t.Any, *, key: str = "") -> None:
            """
            Set the value of this variable.

            This will happen atomically, i.e. it will either fail, leaving the variable in its old state, or succeed;
            even if the process would get killed meanwhile.

            :param value: The new value.
            :param key: The key. Leave to default for single value storage.
            """
            control_site = await self.__control_site()
            await self.__promote_early_file_to_final_file(control_site, key)

            quoted_key = urllib.parse.quote_plus(key)
            working_value_item = parzzley.fs.item(f"~{quoted_key}".encode())
            early_value_item = parzzley.fs.item(f"-{quoted_key}".encode())

            try:
                await control_site.remove_item(working_value_item)
            except parzzley.fs.Site.Exception:
                pass
            try:
                await control_site.create_item(working_value_item, parzzley.fs.ItemType.FILE)
            except parzzley.fs.Site.Exception:
                pass
            await control_site.write_bytes(working_value_item, json.dumps(value).encode())
            await control_site.move_item(working_value_item, early_value_item)
            await self.__promote_early_file_to_final_file(control_site, key)

        async def __promote_early_file_to_final_file(self, control_site, key):
            quoted_key = urllib.parse.quote_plus(key)
            early_value_item = parzzley.fs.item(f"-{quoted_key}".encode())
            value_item = parzzley.fs.item(f"_{quoted_key}".encode())

            if await control_site.item_exists(early_value_item):
                await control_site.move_item(early_value_item, value_item)

        async def __control_site(self):
            control_site = await self.__manager_control_site(self.__name)

            try:
                await control_site.create_item(
                    parzzley.fs.item(self.__volume_name.encode()), parzzley.fs.ItemType.DIRECTORY
                )
            except parzzley.fs.Site.ItemExistsError:
                pass

            return control_site.sub_site(self.__volume_name.encode())
