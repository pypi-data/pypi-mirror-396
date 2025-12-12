#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Parzzley service is a loop.

See :py:class:`Service`.
"""
import asyncio
import dataclasses
import logging
import pathlib
import threading
import time
import traceback
import typing as t

import parzzley.config.loader
import parzzley.sync.control
import parzzley.sync.manager


_logger = logging.getLogger(__name__)


class Service:
    """
    Parzzley service is a loop - usually running in background - that executes the synchronization(s) from its
    configuration in regular intervals and whenever triggered from outside. See e.g. :py:meth:`run`.
    """

    def __init__(self, *, config_dir: pathlib.Path | str):
        """
        :param config_dir: The Parzzley config directory.
        """
        self.__manager = parzzley.sync.manager.Manager.for_config_directory(config_dir)
        self.__stop_requested = False
        self.__force_sync_requested = []
        self.__threads = None

    @property
    def volumes(self) -> t.Sequence["parzzley.config.Volume"]:
        """
        All sync volumes processed by this service.
        """
        return self.__manager.volumes

    def stop_soon(self) -> None:
        """
        Stop the service as soon as possible.

        This method does not wait for that to actually happen but returns instantly (non-blocking).

        This can be called from anywhere in any situation. Once called, the service will stop as soon as possible and
        will never be able to run again (i.e. you need to create a new instance if you want to run it again later).
        """
        if self.__stop_requested:
            return
        self.__stop_requested = True

        _logger.info("Terminating...")
        for thread in self.__threads:
            thread.stop_soon()

    def sync_soon(self, volume_name: str) -> None:
        """
        Request the service loop to execute the sync for a given volume as soon as possible.

        This method does not wait for that to actually happen but returns instantly (non-blocking).

        :param volume_name: The name of the volume to sync.
        """
        self.__force_sync_requested.append(volume_name)

    def run(self) -> None:
        """
        Run the service loop. This will potentially block forever (but see :py:meth:`stop_soon`).

        This will run the configured sync volumes in their regular intervals or whenever :py:meth:`sync_soon` was
        called.
        """
        if self.__threads is not None:
            raise RuntimeError("this service is already running")
        # pylint: disable=unnecessary-dunder-call
        asyncio.new_event_loop().run_until_complete(self.__manager.__aenter__())

        self.__threads = tuple(
            (
                Service._LoopThread(name=f"{self} > noop"),
                *(
                    Service._VolumeThread(self, self.__manager, volume, self.__force_sync_requested)
                    for volume in self.volumes
                ),
                *(
                    Service._MonitorSiteForChangesThread(self, volume, site)
                    for volume in self.volumes
                    for site in volume.sites
                ),
            )
        )

        for thread in self.__threads:
            thread.start()
        for thread in self.__threads:
            thread.join()

        asyncio.new_event_loop().run_until_complete(self.__manager.__aexit__(None, None, None))

        self.__threads = None

    class _LoopThread(threading.Thread):

        def __init__(self, *, name: str):
            super().__init__(target=self.__run, name=name)
            self.__stop_requested = False
            self.__stop_condition = threading.Condition()

        def stop_soon(self) -> None:
            """
            Request this thread to stop as soon as possible and return directly after doing the request (non-blocking).
            """
            with self.__stop_condition:
                self.__stop_requested = True
                self.__stop_condition.notify_all()

        async def _action(self) -> None:
            self._sleep(999)

        async def _stopping(self) -> None:
            pass

        @property
        def stop_requested(self) -> bool:
            """
            Whether this thread was requested to stop (or even already stopped).
            """
            return self.__stop_requested

        def _sleep(self, duration: float) -> None:
            end_time = time.monotonic() + duration
            with self.__stop_condition:
                while not self.__stop_requested and (interval := end_time - time.monotonic()) > 0:
                    self.__stop_condition.wait(interval)

        def __run(self):
            asyncio.new_event_loop().run_until_complete(self.__run__async())

        async def __run__async(self):
            with self.__stop_condition:
                while not self.__stop_requested:
                    self.__stop_condition.release()
                    try:
                        await self._action()
                    except Exception:  # pylint: disable=broad-exception-caught
                        _logger.error(traceback.format_exc())
                        self._sleep(60)
                    finally:
                        self.__stop_condition.acquire()
                await self._stopping()

    class _VolumeThread(_LoopThread):

        def __init__(self, service, manager, volume: parzzley.config.Volume, force_sync_requests: list[str]):
            super().__init__(name=f"{service} > volume {volume.name!r}")
            self.__manager = manager
            self.__volume = volume
            self.__running_sync_task = None
            self.__last_success_time_per_site = {}
            self.__force_sync_requests = force_sync_requests
            self.__i = 0
            self.__last_outdated_sites = ()
            self.__modulus = min(max(1, int(self.__volume.interval.total_seconds() / 3)), 30)

        async def _action(self):
            self.__i += 1
            self._sleep(3)

            if self.__running_sync_task:
                if self.__running_sync_task.sync_control.is_finished:
                    await self.__action__finished_sync_run()
                return

            self.__action__sync_forced_flag()

            outdated_sites = tuple(self.__action__outdated_sites())
            if len(outdated_sites) == 0:
                self.__last_outdated_sites = ()
                return

            outdated_sites_changed = outdated_sites != self.__last_outdated_sites
            self.__last_outdated_sites = outdated_sites

            if outdated_sites_changed or (self.__i % self.__modulus == 1):
                self.__last_outdated_sites = ()
                await self.__action__start_sync(outdated_sites)

        async def _stopping(self):
            if self.__running_sync_task:
                await self.__running_sync_task.prepare_sync_context.__aexit__(None, None, None)
                self.__running_sync_task = None

        def __action__sync_forced_flag(self) -> None:
            forced = False
            while self.__volume.name in self.__force_sync_requests:
                forced = True
                self.__force_sync_requests.remove(self.__volume.name)

            if forced:
                for site in self.__volume.sites:
                    self.__last_success_time_per_site[site.name] = 0
                _logger.debug("Forced sync run for %s", self.__volume.name)

        def __action__outdated_sites(self) -> t.Sequence[parzzley.config.Site]:
            now = time.monotonic()
            return tuple(
                site
                for site in self.__volume.sites
                if self.__last_success_time_per_site.get(site.name, 0) + self.__volume.interval.total_seconds() < now
            )

        async def __action__start_sync(self, outdated_sites: t.Sequence[parzzley.config.Site]):
            prepare_sync_context = self.__manager.prepare_sync(self.__volume, require_one_of=outdated_sites)
            prepared_sync_setup = await prepare_sync_context.__aenter__()  # pylint: disable=unnecessary-dunder-call

            if len(prepared_sync_setup.connected_sites) <= 1:
                await prepare_sync_context.__aexit__(None, None, None)
                return

            try:
                sync_control = await self.__manager.start_sync(prepared_sync_setup)
                if sync_control is not None:
                    self.__running_sync_task = Service._VolumeThread._RunningSyncTask(
                        prepare_sync_context, prepared_sync_setup, sync_control
                    )
                else:
                    await prepare_sync_context.__aexit__(None, None, None)
            except:
                await prepare_sync_context.__aexit__(None, None, None)
                raise

        async def __action__finished_sync_run(self):
            await self.__running_sync_task.prepare_sync_context.__aexit__(None, None, None)

            if self.__running_sync_task.sync_control.was_successful:
                now = time.monotonic()

                other_site_names = [_.name for _ in self.__running_sync_task.prepared_sync_setup.connected_sites]
                for site_setup in self.__running_sync_task.prepared_sync_setup.connected_sites:
                    self.__last_success_time_per_site[site_setup.name] = now
                    other_site_names.remove(site_setup.name)

                if self.__running_sync_task.sync_control.was_effective:
                    for other_site_name in other_site_names:
                        self.__last_success_time_per_site[other_site_name] = 0

            self.__running_sync_task = None

        @dataclasses.dataclass(frozen=True)
        class _RunningSyncTask:
            prepare_sync_context: t.AsyncContextManager["parzzley.sync.manager.Manager.PreparedSyncSetup"]
            prepared_sync_setup: "parzzley.sync.manager.Manager.PreparedSyncSetup"
            sync_control: "parzzley.sync.control.SyncControl"

    class _MonitorSiteForChangesThread(_LoopThread):

        def __init__(self, service, volume, site: parzzley.config.Site):
            super().__init__(name=f"{service} > monitor site {site.name!r}")
            self.__service = service
            self.__volume = volume
            self.__site_setup = parzzley.config.loader.load_site_setup(site)

        async def _action(self):
            try:
                async with self.__site_setup.connect() as site:
                    if not site:
                        raise parzzley.fs.Site.ConnectionLostError()
                    wait_for_changes_task = asyncio.ensure_future(site.wait_for_changes(self.__mark_changed))
                    while not self.stop_requested:
                        await asyncio.sleep(5)
                    wait_for_changes_task.cancel()
            except parzzley.fs.Site.ConnectionLostError:
                _logger.debug(traceback.format_exc())
                self._sleep(60)

        def __mark_changed(self, _):
            self.__service.sync_soon(self.__volume.name)
