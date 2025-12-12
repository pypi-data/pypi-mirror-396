#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Backend`.
"""
import asyncio
import functools
import json
import logging
import os
import pathlib
import shutil
import stat
import time
import traceback
import uuid

import parzzley.fs.utils


_logger = logging.getLogger(__name__)


@parzzley.fs.register_backend
class Backend(parzzley.fs.Backend):
    """
    Local filesystem backend implementation.
    """

    # pylint: disable=arguments-differ
    async def connect(self, *, path: pathlib.Path | str):
        return self._SiteBackend(path)

    async def disconnect(self, site_backend):
        pass

    class _SiteBackend(parzzley.fs.Backend.SiteBackend):

        def __init__(self, path):
            self.__path = pathlib.Path(path)

        def item_type_by_cookie(self, cookie):
            return parzzley.fs.ItemType[cookie[0]]

        async def move_item(self, item, to_item):
            os.rename(self.__internal_path(item), self.__internal_path(to_item))

        async def create_item(self, item, item_type):
            internal_path = self.__internal_path(item)
            try:
                if item_type == parzzley.fs.ItemType.FILE:
                    with open(internal_path, "wb"):
                        pass
                elif item_type == parzzley.fs.ItemType.DIRECTORY:
                    os.mkdir(internal_path)
                elif item_type == parzzley.fs.ItemType.SYMLINK:
                    os.symlink(str(uuid.uuid4()), internal_path)
                else:
                    raise ValueError(f"invalid item_type: {item_type}")
            except FileExistsError as ex:
                raise parzzley.fs.Site.ItemExistsError() from ex

        async def cookie(self, item, stream_name):
            internal_path = self.__internal_path(item)
            try:
                stat_ = os.lstat(internal_path)
            except FileNotFoundError as ex:
                if not self.__path.exists():
                    raise RuntimeError("site unavailable") from ex
                return None

            if stream_name == "":
                if stat.S_ISLNK(stat_.st_mode):
                    itp = parzzley.fs.ItemType.SYMLINK
                elif stat.S_ISREG(stat_.st_mode):
                    itp = parzzley.fs.ItemType.FILE
                elif stat.S_ISDIR(stat_.st_mode):
                    itp = parzzley.fs.ItemType.DIRECTORY
                else:
                    itp = parzzley.fs.ItemType.ALIEN
                return itp.name, stat_.st_mtime_ns

            if stream_name == "xattrs":
                return (await self.__get_xattrs(internal_path)).decode()

            if stream_name == "posix":
                return (await self.__get_posix(internal_path)).decode()

            raise ValueError(f"invalid stream name: {stream_name}")

        async def remove_item(self, item, recursive):
            internal_path = self.__internal_path(item)

            if os.path.isdir(internal_path) and not os.path.islink(internal_path):
                if recursive:
                    shutil.rmtree(internal_path)
                else:
                    os.rmdir(internal_path)

            else:
                os.unlink(internal_path)

        async def child_names(self, item):
            return os.listdir(self.__internal_path(item))

        async def read_streamable(self, item, stream_name=""):
            internal_path = self.__internal_path(item)

            if stream_name == "":
                if os.path.islink(internal_path):
                    return parzzley.fs.stream.MemoryReadStreamable(os.readlink(internal_path))
                return Backend._SiteBackend._FileMainStreamReadStreamable(internal_path)

            if stream_name == "xattrs":
                return parzzley.fs.stream.MemoryReadStreamable(await self.__get_xattrs(internal_path))

            if stream_name == "posix":
                return parzzley.fs.stream.MemoryReadStreamable(await self.__get_posix(internal_path))

            raise ValueError(f"invalid stream name: {stream_name}")

        async def write_streamable(self, item, stream_name=""):
            internal_path = self.__internal_path(item)

            if stream_name == "":
                if os.path.islink(internal_path):
                    return parzzley.fs.stream.MemoryWriteStreamable(
                        functools.partial(self.__set_symlink_target, internal_path)
                    )
                return Backend._SiteBackend._FileMainStreamWriteStreamable(internal_path)

            if stream_name == "xattrs":
                return parzzley.fs.stream.MemoryWriteStreamable(functools.partial(self.__set_xattrs, internal_path))

            if stream_name == "posix":
                return parzzley.fs.stream.MemoryWriteStreamable(functools.partial(self.__set_posix, internal_path))

            raise ValueError(f"invalid stream name: {stream_name}")

        async def wait_for_changes(self, on_changed):
            try:
                # pylint: disable=import-outside-toplevel
                import watchdog.observers
                import watchdog.events
            except ImportError:
                _logger.info("No change monitoring possible for %s (because 'watchdog' is not available)", self)
                while True:
                    await asyncio.sleep(99999)

            root_path = str(self.__path).encode()
            if not root_path.endswith(b"/"):
                root_path += b"/"

            class _MyEventHandler(watchdog.events.FileSystemEventHandler):

                def on_closed(self, event):
                    self.__on_changed(event.src_path)

                def on_deleted(self, event):
                    self.__on_changed(event.src_path)

                def on_moved(self, event):
                    self.__on_changed(event.src_path)
                    self.__on_changed(event.dest_path)

                def __on_changed(self, path):
                    if f"{path}/".encode().startswith(root_path):
                        on_changed(parzzley.fs.item(path[len(root_path) :].encode()))

            event_handler = _MyEventHandler()
            observer = watchdog.observers.Observer()
            observer.schedule(event_handler, self.__path, recursive=True)
            observer.start()

            try:
                while True:
                    await asyncio.sleep(99999)
            finally:
                try:
                    observer.stop()
                except Exception:  # pylint: disable=broad-exception-caught
                    _logger.debug(traceback.format_exc())
                try:
                    observer.join()
                except Exception:  # pylint: disable=broad-exception-caught
                    _logger.debug(traceback.format_exc())

        def __internal_path(self, item: parzzley.fs.Item) -> bytes:
            return str(self.__path).encode() + b"/" + item.path

        async def __set_symlink_target(self, internal_path, target):
            try:
                os.unlink(internal_path)
            except IOError:
                pass
            os.symlink(target.decode(), internal_path)

        async def __get_posix(self, internal_path: bytes) -> bytes:
            stat_ = os.lstat(internal_path)
            return f'{{"mtime": {stat_.st_mtime_ns}}}'.encode()

        async def __set_posix(self, internal_path: bytes, content: bytes) -> None:
            os.utime(
                internal_path, ns=(int(time.time() * (1000**3)), json.loads(content)["mtime"]), follow_symlinks=False
            )

        async def __get_xattrs(self, internal_path: bytes) -> bytes:
            xattrs = {
                key: os.getxattr(internal_path, key, follow_symlinks=False)
                for key in (k.encode() for k in sorted(os.listxattr(internal_path, follow_symlinks=False)))
                if key.startswith(b"user.")
            }
            return parzzley.fs.utils.serialize_bytes_dict(xattrs)

        async def __set_xattrs(self, internal_path: bytes, content: bytes) -> None:
            xattrs = parzzley.fs.utils.deserialize_bytes_dict(content)
            for ky in {*xattrs.keys(), *[k.encode() for k in os.listxattr(internal_path, follow_symlinks=False)]}:
                if ky.startswith(b"user."):
                    val = xattrs.get(ky)
                    if val is None:
                        os.removexattr(internal_path, ky, follow_symlinks=False)
                    else:
                        os.setxattr(internal_path, ky, val, follow_symlinks=False)

        class _FileMainStreamReadStreamable(parzzley.fs.stream.ReadStreamable):

            def __init__(self, full_path):
                self.__full_path = full_path

            class _ReadStream(parzzley.fs.stream.ReadStream):

                def __init__(self, full_path):
                    self.__full_path = full_path
                    self.__file = None
                    self.__buffer = b""

                async def __aenter__(self):
                    self.__file = open(self.__full_path, "rb")  # pylint: disable=consider-using-with

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    self.__file.close()
                    self.__file = None

                async def read(self, max_len):
                    if self.__buffer is None:
                        return None
                    if not self.__buffer:
                        self.__buffer = self.__file.read(500 * 1024**2) or None
                        if self.__buffer is None:
                            return None

                    result = self.__buffer[:max_len]
                    self.__buffer = self.__buffer[max_len:]
                    return result

            async def _stream(self):
                return Backend._SiteBackend._FileMainStreamReadStreamable._ReadStream(self.__full_path)

        class _FileMainStreamWriteStreamable(parzzley.fs.stream.WriteStreamable):

            def __init__(self, full_path):
                self.__full_path = full_path

            class _WriteStream(parzzley.fs.stream.WriteStream):

                def __init__(self, full_path):
                    self.__full_path = full_path
                    self.__file = None

                async def __aenter__(self):
                    self.__file = open(self.__full_path, "wb")

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    if self.__file:
                        await self.commit()

                async def write(self, data):
                    while data:
                        data = data[self.__file.write(data) or 0 :]

                async def commit(self):
                    self.__file.close()
                    self.__file = None

            async def _stream(self):
                return Backend._SiteBackend._FileMainStreamWriteStreamable._WriteStream(self.__full_path)
