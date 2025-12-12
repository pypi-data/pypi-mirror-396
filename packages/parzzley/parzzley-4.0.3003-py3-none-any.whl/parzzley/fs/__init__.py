#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Parzzley filesystem abstraction.

All Parzzley sync operations operate on this API instead of direct OS filesystem APIs. So, Parzzley can sync not only
parts of the local filesystem, but anything that Parzzley has a backend for (in particular this means full support for
ssh-based locations, incl. some features that sshfs would not offer).

- Actual filesystem operations can be done with :py:class:`Site` instances.
  Where needed, Parzzley API usually provides you with such an instance. So the following steps just provide background
  information.
- In order to get a :py:class:`Site`, you usually take a :py:class:`SiteSetup` and :py:meth:`SiteSetup.connect` it.
- In order to get a :py:class:`SiteSetup`, you need to specify a :py:class:`Backend` and some additional,
  backend-specific arguments.
- A :py:class:`Backend` implements a particular kind of filesystem. Directly though, it just implements an interface
  that establishes the connection to that filesystem and returns a :py:class:`Backend.SiteBackend` which is the actual
  implementation of filesystem operations.

Note: :py:class:`Site` and :py:class:`Backend.SiteBackend` look very similar. They are not the same, though. The latter
one is the implementation of a particular kind of filesystem and not to be used directly, but mostly used by the former
one. :py:class:`Site` is the API to be used for filesystem operations outside of this module. It adds various additional
checks and convenience features to what the site backend itself would provide.

For backend implementations, see :py:mod:`parzzley.builtin.fs`.
"""
import abc
import contextlib
import enum
import logging
import threading
import traceback
import typing as t
import uuid

import parzzley.asset
import parzzley.fs.stream


_logger = logging.getLogger(__name__)


class ItemType(enum.Enum):
    """
    Filesystem item type.
    """

    #: A regular file.
    FILE = enum.auto()

    #: A directory.
    DIRECTORY = enum.auto()

    #: A symlink.
    SYMLINK = enum.auto()

    #: An alien file, i.e. anything that does not match any of the former item types. Could be pipes, devices files, ...
    #: These items will be mostly ignored by Parzzley, because they are unsupported.
    #: Parzzley will (with usual configuration) at least report conflicts if an item has a non-alien type on some sites,
    #: but are alien on others.
    ALIEN = enum.auto()

    #: Does not exist. Note: For items that exist but are not one of the known types, see :py:attr:`ALIEN`.
    NONE = enum.auto()


class Item(abc.ABC):
    """
    Represents a particular location (usually in some volume). This is like a path, but not it your local filesystem.
    """

    @property
    @abc.abstractmethod
    def path(self) -> bytes:
        """
        This item's path (segments split by :code:`'/'`; never at the start or end of a path).
        A volume's root directory has item path :code:`''`.

        Paths are byte strings. They are usually UTF-8 encoded strings. It might be encoded in an invalid way, though,
        so it must only be decoded to a string for presentation purposes and this decoding must not fail for invalid
        input. Paths never contain the NULL character, though.

        Site backends that internally deal with file names encoded in another encoding than UTF-8 (or have a different
        set of allowed characters) have to translate between these representations; also in a way that does not fail for
        invalid input.
        """

    @property
    @abc.abstractmethod
    def parent(self) -> "Item|None":
        """
        The parent item (or :code:`None` as the root item's parent).
        """

    @property
    @abc.abstractmethod
    def name(self) -> bytes | None:
        """
        This item's name, i.e. the last segment of :py:attr:`path` (or :code:`None` for the root item).
        """

    @abc.abstractmethod
    def _descendant(self, *relative_paths: bytes) -> "Item":
        pass

    def __call__(self, *relative_paths):
        return self._descendant(*relative_paths)

    def __eq__(self, o):
        return isinstance(o, Item) and self.path == o.path

    def __hash__(self):
        return hash(self.path)


TItemInput = bytes | Item


class _Item(Item):

    def __init__(self, path: TItemInput, descendant_of: Item | None):
        super().__init__()
        self.__path = self.__sanitize_path(path.path if isinstance(path, Item) else path)
        self.__descendant_of = descendant_of

    @property
    def path(self):
        return b"/".join(filter(None, [(self.__descendant_of.path if self.__descendant_of else b""), self.__path]))

    @property
    def parent(self):
        self_path = self.path
        if self_path == b"":
            return None
        if self.__path and self.__descendant_of:
            return self.__descendant_of(self.__path, b"..")
        return item(self_path, b"..")

    @property
    def name(self):
        if self.path == b"":
            return None
        return self.path.rpartition(b"/")[2]

    def _descendant(self, *relative_paths):
        return _Item(b"/".join([p.path if isinstance(p, Item) else p for p in relative_paths if p]), descendant_of=self)

    def __sanitize_path(self, path: bytes) -> bytes:
        segments = [s for s in path.split(b"/") if (s and s != b".")]
        try_remove_uplevel_refs = True
        while try_remove_uplevel_refs:
            try_remove_uplevel_refs = False
            for i_segment, segment in list(enumerate(segments)):
                if segment == b"..":
                    segments.pop(i_segment)
                    if i_segment > 0:
                        segments.pop(i_segment - 1)
                    try_remove_uplevel_refs = True
                    break
        return b"/".join(segments)


def item(*paths_or_items: TItemInput) -> Item:
    """
    Return an item for a given item-like object.

    :param paths_or_items: Paths or item objects.
    """
    if len(paths_or_items) == 1 and isinstance(paths_or_items[0], Item):
        return paths_or_items[0]
    return _Item(b"/".join(_.path if isinstance(_, Item) else _ for _ in paths_or_items), None)


class Site:  # pylint: disable=too-many-public-methods
    """
    A filesystem site.

    All kinds of filesystem operations are provided by means of its methods. Any pieces of Parzzley that execute some
    filesystem operations (i.e. virtually all aspects - see :py:mod:`parzzley.sync.aspect` - and much more) work with
    these.

    The actual effect might be somewhere in the local OS filesystem, but could also be somewhere else, e.g. somewhere in
    some remote machine's filesystem.

    See also :py:class:`Site.Exception` about error handling.
    """

    def __init__(self, name: str | None, site_backend: "Backend.SiteBackend"):
        """
        Do not use directly. See :py:mod:`parzzley.fs`.

        :param name: The site name. See also :py:attr:`name`!
        :param site_backend: The site backend.
        """
        self.__name = name
        self.__site_backend = site_backend

    @property
    def name(self) -> str | None:
        """
        The site name.

        Each 'real' site, i.e. each one that is directly associated to a site configuration from the end user, has a
        non-empty site name that is unique in the scope of the volume configuration it is owned by.

        In some places, there can be artificial sites, e.g. for the purpose of internal state data storage. You should
        not rely on their names in any way, as they typically do not have one at all.
        """
        return self.__name

    @property
    def root_directory(self) -> Item:
        """
        The site root directory. This is always an item with path :code:`""`.
        """
        return item(b"")

    async def create_item(self, item_: TItemInput, item_type: ItemType, *, recursive: bool = False) -> None:
        """
        Create a new item.

        If there already is an item at the same location, raise :py:class:`Site.ItemExistsError`.

        :param item_: The item location.
        :param item_type: The new item type.
        :param recursive: For a directory, whether to create super-directories on demand as well.
        """
        if item_type in (ItemType.NONE, ItemType.ALIEN):
            raise ValueError(f"items cannot be created with type {item_type}")
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            if recursive:
                if item_type != ItemType.DIRECTORY:
                    raise ValueError("recursive can only be set for directories")

                item_segments = []
                item__ = item_
                item_ = item__
                while item_.path:
                    item_segments.append(item_)
                    item_ = item_.parent
                for item_segment in reversed(item_segments):
                    try:
                        await self.create_item(item_segment, parzzley.fs.ItemType.DIRECTORY)
                    except Site.ItemExistsError:
                        if item_segment == item__:
                            raise
                return

            return await self.__site_backend.create_item(item(item_), item_type)

    async def remove_item(self, item_: TItemInput, *, recursive: bool = False) -> None:
        """
        Remove an item.

        :param item_: The item location.
        :param recursive: For a directory, whether to remove all content inside it as well if not empty.
        """
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            return await self.__site_backend.remove_item(item_, recursive)

    def item_type_by_cookie(self, cookie: object) -> ItemType:
        """
        Return the item type by the main stream cookie. If you do not already have it, use :py:meth:`item_type` instead.

        :param cookie: The main stream cookie.
        """
        if cookie is None:
            return parzzley.fs.ItemType.NONE
        with Site.__translate_arbitrary_exception_to_site_exception():
            return (self.__site_backend.item_type_by_cookie(cookie)) or ItemType.NONE

    async def cookie(self, item_: TItemInput, stream_name: str = "") -> object:
        """
        Return the cookie for a stream of an item.

        Stream cookies are mostly an opaque data structure. They fulfill two purposes:

        - The main stream's cookie must somehow carry the item type. Each site backend knows how to extract it from such
          a cookie. This will happen when :py:meth:`item_type_by_cookie` is called.
        - But primarily, comparing stream cookies from the same item and site and from different times allows to detect
          changes (without interpreting their actual content in any way, just by simple equality-comparisons).

        Each stream cookie must be one of Python's simple types (:code:`str`, :code:`float`, :code:`int`, :code:`bool`
        and :code:`None`), or a tuple or list (lists will be translated to tuples automatically, though).

        :param item_: The item location.
        :param stream_name: The stream name (default: the main stream).
        """
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            return Site.sanitized_cookie(await self.__site_backend.cookie(item_, stream_name))

    async def item_type(self, item_: TItemInput) -> ItemType:
        """
        Return the item type for an item. If you only want to check whether an item exists, see :py:meth:`item_exists`
        instead.

        :param item_: The item location.
        """
        return self.item_type_by_cookie(await self.cookie(item_, ""))

    async def item_exists(self, item_: TItemInput) -> bool:
        """
        Return whether an item exists.

        :param item_: The item location.
        """
        return await self.item_type(item_) != ItemType.NONE

    async def move_item(self, item_: TItemInput, to_item: TItemInput, *, to_site: "Site|None" = None) -> None:
        """
        Move an item.

        If the source is a normal file and the destination already exists and is also a normal file, the destination
        will be overwritten.

        :param item_: The source item location.
        :param to_item: The destination location.
        :param to_site: The destination site (default: the same site). Note: Do not use. It is only allowed under
                        particular circumstances and only used internally by Parzzley for specific functionality.
        """
        item_ = item(item_)
        to_item = item(to_item)
        with Site.__translate_arbitrary_exception_to_site_exception():
            if to_site:
                to_item = self.sub_site_location(to_site)(to_item.path)
            return await self.__site_backend.move_item(item_, to_item)

    async def child_names(self, item_: TItemInput) -> t.Sequence[str]:
        """
        Return the names of all children of an item (sorted). See also :py:meth:`children`.

        Note: This will never contain the :file:`..parzzley.control` directory on root level (which is used internally
        by Parzzley for persistence of some sync states).

        :param item_: The item location.
        """
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            return sorted(
                _
                for _ in await self.__site_backend.child_names(item_)
                if not (item_.path == b"" and _ == Backend.CONTROL_SITE_ROOT_DIR_NAME)
            )

    async def children(self, item_: TItemInput) -> t.Sequence[Item]:
        """
        Return all child items of an item (sorted by name). See also :py:meth:`child_names`.

        Note: This will never contain the :file:`..parzzley.control` directory on root level (which is used internally
        by Parzzley for persistence of some sync states).

        :param item_: The item location.
        """
        item_ = item(item_)
        return [item_(child_name) for child_name in await self.child_names(item_)]

    async def read_streamable(self, item_: TItemInput, stream_name: str = "") -> "parzzley.fs.stream.ReadStreamable":
        """
        Return a read-streamable for an item.

        :param item_: The item location.
        :param stream_name: The stream name (default: the main stream).
        """
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            return await self.__site_backend.read_streamable(item_, stream_name)

    async def write_streamable(self, item_: TItemInput, stream_name: str = "") -> "parzzley.fs.stream.WriteStreamable":
        """
        Return a write-streamable for an item.

        :param item_: The item location.
        :param stream_name: The stream name (default: the main stream).
        """
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            return await self.__site_backend.write_streamable(item_, stream_name)

    async def read_bytes(self, item_: TItemInput, stream_name: str = "") -> bytes:
        """
        Read binary content from an item.

        Note: If the content can exceed a few megabytes of size, you should better use :py:meth:`read_streamable`.

        :param item_: The item location.
        :param stream_name: The stream name (default: the main stream).
        """
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            return await (await self.read_streamable(item_, stream_name)).read_bytes()

    async def write_bytes(self, item_: TItemInput, content: bytes, stream_name: str = "") -> None:
        """
        Write binary content to an item.

        Note: If the content can exceed a few megabytes of size, you should better use :py:meth:`write_streamable`.

        :param item_: The item location.
        :param content: The content to write.
        :param stream_name: The stream name (default: the main stream).
        """
        item_ = item(item_)
        with Site.__translate_arbitrary_exception_to_site_exception():
            return await (await self.write_streamable(item_, stream_name)).write_bytes(content)

    async def wait_for_changes(self, on_changed: t.Callable[[Item], None]) -> None:
        """
        Until canceled, watch this site for any changes.

        Access to the control site directory will be filtered and not reported. Also watch the control site explicitly
        if needed.

        :param on_changed: The function to call whenever changes were observed.
        """

        def _on_changed(item_: Item):
            if not (item_.path + b"/").startswith(parzzley.fs.Backend.CONTROL_SITE_ROOT_DIR_NAME + b"/"):
                on_changed(item_)

        with Site.__translate_arbitrary_exception_to_site_exception():
            return await self.__site_backend.wait_for_changes(_on_changed)

    async def create_temp_item(self, item_type: ItemType) -> Item:
        """
        Create and return a temporary item in some hidden temporary place that gets cleaned up automatically.

        :param item_type: The item type.
        """
        temp_item = self.sub_site_location(await self.temp_site())(str(uuid.uuid4()).encode())
        await self.create_item(temp_item, item_type)
        return temp_item

    def sub_site(self, root_dir: TItemInput) -> "Site":
        """
        Return sub site, i.e. a site that represents a subtree of this site.

        Note: Do not use. It is only used internally by Parzzley for specific functionality.

        :param root_dir: The root directory of the new site.
        """
        return Site(None, _SubTreeSiteBackend(self.__site_backend, root_dir))

    def sub_site_location(self, sub_site: "Site") -> "Item":
        """
        Return the location of the root directory of a given subsite in this site.

        Note: Do not use. It is only used internally by Parzzley for specific functionality.

        :param sub_site: The sub site.
        """
        site_backend_for_location = sub_site.__site_backend
        location = parzzley.fs.item(b"")
        if site_backend_for_location is self.__site_backend:
            return location

        while sub_site_info := site_backend_for_location.is_sub_site_of():
            site_backend_for_location = sub_site_info[0]
            location = parzzley.fs.item(sub_site_info[1])(location)
            if site_backend_for_location is self.__site_backend:
                return location

        raise Site.Exception(f"{sub_site!r} is not a sub site of {self}")

    async def control_site(self) -> "Site":
        """
        Return the control site.

        Note: Do not use. It is only used internally by Parzzley for specific functionality.
        """
        control_root_item = parzzley.fs.item(Backend.CONTROL_SITE_ROOT_DIR_NAME)

        try:
            await self.create_item(control_root_item, parzzley.fs.ItemType.DIRECTORY)
        except parzzley.fs.Site.ItemExistsError:
            pass

        readme_file = control_root_item(b"README.txt")
        try:
            await self.create_item(readme_file, parzzley.fs.ItemType.FILE)
        except parzzley.fs.Site.ItemExistsError:
            pass
        await self.write_bytes(
            readme_file,
            f"This directory structure (i.e. the one that contains"
            f" '{parzzley.fs.Backend.CONTROL_SITE_ROOT_DIR_NAME.decode()}')\n"
            f"is synchronized by Parzzley.\n\n"
            f"Visit {parzzley.asset.project_info.homepage_url} for more information.\n".encode(),
        )

        return self.sub_site(control_root_item)

    async def temp_site(self) -> "Site":
        """
        Return a sub-site that is able to store arbitrary temporary items and gets cleaned up automatically.

        Note: Do not use. It is only used internally by Parzzley for specific functionality.
        """
        result = await self.control_site()
        sub_item = item(b"temp")
        try:
            await result.create_item(sub_item, ItemType.DIRECTORY)
        except parzzley.fs.Site.ItemExistsError:
            pass
        return result.sub_site(b"temp")

    @staticmethod
    @contextlib.contextmanager
    def __translate_arbitrary_exception_to_site_exception():
        try:
            yield
        except Site.Exception:
            raise
        except Exception as ex:
            raise Site.Exception(f"site error: {ex}") from ex

    @staticmethod
    def sanitized_cookie(cookie: t.Any) -> t.Any:
        """
        Return the sanitized variant of a given cookie (e.g. convert all lists to tuples).

        :param cookie: The cookie to sanitize.
        """
        if cookie is None or isinstance(cookie, (str, float, int)):
            return cookie
        if isinstance(cookie, (list, tuple)):
            return tuple(Site.sanitized_cookie(_) for _ in cookie)
        raise ValueError(f"invalid part of a cookie: {cookie!r}")

    class Exception(Exception):
        """
        Base class for arbitrary errors during a site operation.

        Note: All operations on a :py:class:`Site` will only throw :code:`ValueError` (if an input value is invalid) or
        :py:class:`Site.Exception` (or one of its subclasses).

        Operations in a :py:class:`Backend.SiteBackend` are free to raise arbitrary exceptions, but any exception that
        is not a :py:class:`Site.Exception` will transparently be wrapped up by one when used by a :py:class:`Site`.
        """

    class ItemExistsError(Exception):
        """
        The item already exists.
        """

    class ConnectionLostError(Exception):
        """
        The site has been physically disconnected meanwhile.
        """


class Backend(abc.ABC):
    """
    Base class for implementations of a particular kind of filesystem.

    This part of the filesystem API is only relevant for the implementation of filesystems. Anywhere else, use
    :py:class:`Site` instead.

    While this interface defines some abstract methods, the majority implementation happens in the
    :py:class:`Backend.SiteBackend` implementation that :py:meth:`connect` returns.
    """

    CONTROL_SITE_ROOT_DIR_NAME = b"..parzzley.control"

    # pylint: disable=redefined-outer-name
    class SiteBackend(abc.ABC):
        """
        Base class for site backends for a particular kind of filesystem.
        """

        @abc.abstractmethod
        async def create_item(self, item: Item, item_type: ItemType) -> None:
            """
            Create a new item.

            See :py:meth:`Site.create_item` about what exception it must raise in which situations.

            :param item: The item location.
            :param item_type: The new item type.
            """

        @abc.abstractmethod
        async def remove_item(self, item: Item, recursive: bool) -> None:
            """
            Remove an item.

            :param item: The item location.
            :param recursive: For a directory, whether to remove all content inside it as well if not empty.
            """

        @abc.abstractmethod
        def item_type_by_cookie(self, cookie: t.Any) -> ItemType:
            """
            Return the item type by the main stream cookie.

            :param cookie: The main stream cookie.
            """

        @abc.abstractmethod
        async def cookie(self, item: Item, stream_name: str) -> object:
            """
            Return the item cookie for an item. See also :py:meth:`Site.cookie`.

            :param item: The item location.
            :param stream_name: The stream name.
            """

        @abc.abstractmethod
        async def move_item(self, item: Item, to_item: Item) -> None:
            """
            Move an item.

            If the source is a normal file and the destination already exists and is also a normal file, the destination
            will be overwritten.

            :param item: The source item location.
            :param to_item: The destination location.
            """

        @abc.abstractmethod
        async def child_names(self, item: Item) -> t.Iterable[str]:
            """
            Return the names of all children of an item.

            :param item: The item location.
            """

        @abc.abstractmethod
        async def read_streamable(self, item: Item, stream_name: str) -> "parzzley.fs.stream.ReadStreamable":
            """
            Return a read-streamable for an item.

            :param item: The item location.
            :param stream_name: The stream name.
            """

        @abc.abstractmethod
        async def write_streamable(self, item: Item, stream_name: str) -> "parzzley.fs.stream.WriteStreamable":
            """
            Return a write-streamable for an item.

            :param item: The item location.
            :param stream_name: The stream name.
            """

        @abc.abstractmethod
        async def wait_for_changes(self, on_changed: t.Callable[[Item], None]) -> None:
            """
            Until canceled, watch this site for any changes.

            There will be on filtering, so it will also report changes e.g. on the control site directory.

            :param on_changed: The function to call whenever changes were observed.
            """

        def is_sub_site_of(self) -> tuple["Backend.SiteBackend", Item] | None:
            """
            Return information about its relation to an outer site, if it is a sub site.

            Do not override this method.
            """

    @abc.abstractmethod
    async def connect(self, **kwargs) -> SiteBackend | None:
        """
        Connect and return a site backend for given arguments (or :code:`None` if this is impossible for some reasons).

        This method does not raise any exceptions.

        :param kwargs: Additional arguments for the site backend (specific to its type).
        """

    @abc.abstractmethod
    async def disconnect(self, site_backend: SiteBackend) -> None:
        """
        Disconnect a given site backend (returned earlier by :py:meth:`connect`).

        Must only be called once for each site backend.

        This method does not raise any exceptions.

        :param site_backend: The site backend to disconnect. This is what the last :py:meth:`connect` call returned.
        """


SiteContextManager = t.AsyncContextManager[Site | None]


class SiteSetup:
    """
    A site setup specifies a name, a backend and additional arguments. It can eventually generate a :py:class:`Site` out
    of that (see :py:meth:`connect`).
    """

    def __init__(self, name: str, backend: Backend, arguments: dict[str, str]):
        """
        Usually not used directly. See :py:func:`parzzley.config.loader.load_site_setup` or even
        :py:func:`parzzley.config.loader.load_volume`.

        :param name: The site name.
        :param backend: The backend.
        :param arguments: The additional arguments.
        """
        self.__name = name
        self.__backend = backend
        self.__arguments = arguments
        self.__connect_counter = 0
        self.__site_backend = None
        self.__lock = threading.RLock()

    @property
    def name(self) -> str:
        """
        The site name.
        """
        return self.__name

    @contextlib.asynccontextmanager
    async def connect(self) -> SiteContextManager:
        """
        Connect this site setup. To be used in a `with`-block.

        This method does not raise any exceptions, but the context manager might return :code:`None` instead of a site
        if there were problems during connecting.

        This context is allowed to be entered multiple times; even nested. It will automatically reuse the existing
        connection when an active context gets entered again and only disconnect the backend after the 'last' context
        exits.
        """
        with self.__lock:
            if self.__connect_counter == 0:
                site_backend = await self.__backend.connect(**self.__arguments)

                if site_backend is not None:
                    try:
                        if (
                            root_cookie := await site_backend.cookie(parzzley.fs.item(b""), "")
                        ) is None or site_backend.item_type_by_cookie(root_cookie) == parzzley.fs.ItemType.NONE:
                            raise RuntimeError("root directory does not exist")
                    except Exception:  # pylint: disable=broad-exception-caught
                        _logger.debug(traceback.format_exc())
                        site_backend = None

                if not site_backend:
                    yield None
                    return
                self.__site_backend = site_backend

            self.__connect_counter += 1

        try:
            site = Site(self.name, self.__site_backend)
            try:
                await site.remove_item(site.sub_site_location(await site.temp_site()), recursive=True)
            except parzzley.fs.Site.Exception:  # TODO noh more specific, e.g. ItemDoesNotExistError ?!
                pass
            yield site
        finally:
            with self.__lock:
                self.__connect_counter -= 1
                if self.__connect_counter == 0:
                    if self.__site_backend:
                        await self.__backend.disconnect(self.__site_backend)
                        self.__site_backend = None


_registered_backends = {}


def register_backend(backend_type: type[Backend]):
    """
    Decorator that registers a filesystem backend with its parent module name as kind name (e.g. :code:`"baz"` if the
    backend is implemented in a package like :code:`foo.bar.baz`), so it can be located later by
    :py:func:`backend_by_kind`.

    :param backend_type: The backend type.
    """
    _registered_backends[backend_type.__module__.rpartition(".")[2]] = backend_type()
    return backend_type


def backend_by_kind(kind: str) -> Backend | None:
    """
    Return a filesystem backend by its kind name (as registered by :py:func:`register_backend`).

    :param kind:
    """
    return _registered_backends.get(kind)


#: A site specification that can at least be transformed to a site name by :py:func:`site_name`.
TSiteInput = Site | SiteSetup | str


def site_name(site: TSiteInput | None) -> str | None:
    """
    Return a site name for a given site specification.

    :param site: The site specification.
    """
    if site is None:
        return None
    if isinstance(site, str):
        return site
    return site.name


# pylint: disable=redefined-outer-name
class _SubTreeSiteBackend(Backend.SiteBackend):

    def __init__(self, origin_site_backend: Backend.SiteBackend, root_item: TItemInput):
        super().__init__()
        self.__origin_site_backend = origin_site_backend
        self.__root_item = item(root_item)

    def item_type_by_cookie(self, cookie):
        return self.__origin_site_backend.item_type_by_cookie(cookie)

    async def cookie(self, item, stream_name):
        return await self.__origin_site_backend.cookie(self.__root_item(item.path), stream_name)

    async def remove_item(self, item, recursive):
        return await self.__origin_site_backend.remove_item(self.__root_item(item.path), recursive)

    async def move_item(self, item, to_item):
        return await self.__origin_site_backend.move_item(self.__root_item(item.path), self.__root_item(to_item.path))

    async def child_names(self, item):
        return await self.__origin_site_backend.child_names(self.__root_item(item.path))

    async def create_item(self, item, item_type):
        return await self.__origin_site_backend.create_item(self.__root_item(item.path), item_type)

    async def read_streamable(self, item, stream_name):
        return await self.__origin_site_backend.read_streamable(self.__root_item(item.path), stream_name)

    async def write_streamable(self, item, stream_name):
        return await self.__origin_site_backend.write_streamable(self.__root_item(item.path), stream_name)

    async def wait_for_changes(self, on_changed):
        def _on_changed(item_: Item):
            if f"{item_.path}/".startswith(f"{self.__root_item.path}/"):
                on_changed(item(item_.path[len(self.__root_item.path) :]))

        return await self.__origin_site_backend.wait_for_changes(_on_changed)

    def is_sub_site_of(self):
        return self.__origin_site_backend, self.__root_item
