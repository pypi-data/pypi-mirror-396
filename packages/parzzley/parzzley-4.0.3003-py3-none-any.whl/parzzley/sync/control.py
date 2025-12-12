#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Sync controls. See :py:class:`SyncControl`.
"""
import abc


class SyncControl(abc.ABC):
    """
    Base class for sync controls. A sync control allows to monitor and control a running sync run.

    These objects are returned e.g. by :py:meth:`parzzley.sync.manager.Manager.run_sync`.

    See e.g. :py:meth:`wait_finished` and :py:attr:`was_successful`.
    """

    def __init__(self):
        self.__is_cancel_requested = False

    @property
    @abc.abstractmethod
    def sync_run_id(self) -> str:
        """
        This sync run's identifier (always a new unique one for each run!).
        """

    @property
    @abc.abstractmethod
    def is_finished(self) -> bool:
        """
        Whether the associated sync run is already finished (either successfully or not).
        """

    @property
    @abc.abstractmethod
    def was_successful(self) -> bool:
        """
        Whether the associated sync run is already finished and was successful.

        For a finished but unsuccessful run, there is at least one critical alert (see :py:attr:`alerts`).
        """

    @property
    @abc.abstractmethod
    def was_effective(self) -> bool:
        """
        Whether the associated sync run had any effects, i.e. synced any changes.

        Note: This is only a hint. You must not rely on it for any critical decisions!
        """

    @abc.abstractmethod
    def wait_finished(self) -> None:
        """
        Wait until the associated sync run is finished. When this function returns, :py:attr:`is_finished` is set.
        """

    @property
    def is_cancel_requested(self) -> bool:
        """
        Whether this sync run was requested to cancel. See also :py:meth:`cancel`.
        """
        return self.__is_cancel_requested

    def cancel(self) -> None:
        """
        Request this sync run to cancel.
        """
        self.__is_cancel_requested = True
        self.wait_finished()
