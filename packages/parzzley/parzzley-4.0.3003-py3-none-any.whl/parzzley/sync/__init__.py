#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Parzzley syncing.

This module only defines some common structures and interfaces. See submodules for more.
In order to execute syncing, see :py:mod:`parzzley.sync.manager`.
"""
import importlib
import pkgutil
import typing as t

if t.TYPE_CHECKING:
    import parzzley.sync.aspect


class Volume:
    """
    A sync volume.

    A sync volume basically defines some sites (see :py:class:`parzzley.fs.Site`), i.e. some local or remote filesystems
    and aspects (see :py:class:`parzzley.sync.aspect.Aspect`). A synchronization takes place on a particular volume.
    """

    def __init__(
        self,
        name: str,
        site_setups: t.Iterable["parzzley.fs.SiteSetup"],
        aspects_per_site: dict[str, t.Iterable["parzzley.sync.aspect.Aspect"]],
    ):
        """
        :param name: The volume name.
        :param site_setups: The sites associated to this volume (as site setups).
        :param aspects_per_site: The aspects per site.
        """
        self.__name = name
        self.__site_setups = tuple(site_setups)
        self.__aspects_per_site = dict(aspects_per_site)

    @property
    def name(self) -> str:
        """
        The volume name.
        """
        return self.__name

    @property
    def site_setups(self) -> t.Sequence["parzzley.fs.SiteSetup"]:
        """
        The sites associated to this volume (as site setups).
        """
        return self.__site_setups

    def aspects(self, site_name: str) -> t.Sequence["parzzley.sync.aspect.Aspect"]:
        """
        Return the aspects associated to a given site of this volume.

        This includes all aspects that were configured particularly on the given site, but also all aspects that were
        configured for the entire volume.

        :param site_name: The site name.
        """
        return tuple(self.__aspects_per_site.get(site_name, ()))


def load_implementations_from_package(package_name: str) -> None:
    """
    Load custom implementations (for aspects, filesystem backends, ...).

    :param package_name: The Python package to load implementations from.
    """
    module = importlib.import_module(package_name)
    package_paths = getattr(module, "__path__", None)
    if package_paths:
        for sub_package_info in pkgutil.walk_packages(module.__path__):
            load_implementations_from_package(f"{package_name}.{sub_package_info.name}")
