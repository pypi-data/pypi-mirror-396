#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Parzzley builtin filesystem implementations. See also :py:mod:`parzzley.fs`.
"""
import abc
import ast
import asyncio
import base64
import contextlib
import dataclasses
import fcntl
import functools
import json
import logging
import os
import pathlib
import re
import shlex
import subprocess
import threading
import time
import traceback
import typing as t
import uuid

import parzzley.fs.utils


_logger = logging.getLogger(__name__)


class ShellBasedBackend(parzzley.fs.Backend, abc.ABC):
    """
    Base class for Unix shell based filesystem backends.
    """

    # pylint: disable=arguments-differ
    async def connect(self, *, path: str, **kwargs):
        return ShellBasedBackend._SiteBackend(self._shell, kwargs, path)

    async def disconnect(self, site_backend: "ShellBasedBackend._SiteBackend"):
        await site_backend.disconnect()

    @abc.abstractmethod
    def _shell(self, **kwargs) -> "Shell":
        """
        Return a shell for the given arguments.

        :param kwargs: The backend arguments.
        """

    class _SiteBackend(parzzley.fs.Backend.SiteBackend):

        class _ShellPool:

            WORKER_COUNT = 3

            def __init__(self, shell_factory: t.Callable, shell_kwargs: dict):
                self.__shell_factory = shell_factory
                self.__shell_kwargs = shell_kwargs
                self.__shells = []
                self.__busy_shells = set()
                self.__lock = threading.Lock()
                self.__shell_released = threading.Condition(self.__lock)

            def disconnect(self):
                """
                Disconnect.
                """
                with self.__lock:
                    for shell in self.__shells:
                        try:
                            shell.__exit__(None, None, None)
                        except Exception:  # pylint: disable=broad-exception-caught
                            _logger.warning(traceback.format_exc())
                    self.__shells = None

            @contextlib.contextmanager
            def shell(self) -> t.Generator["ShellBasedBackend.Shell"]:
                """
                Return a context manager that reserves and returns a free shell for arbitrary usage.
                """
                with self.__lock:
                    if self.__shells is None:
                        raise parzzley.fs.Site.ConnectionLostError()
                    while True:
                        while len(self.__busy_shells) == len(self.__shells):
                            if len(self.__shells) < self.WORKER_COUNT:
                                self.__new_shell()
                            else:
                                self.__shell_released.wait()

                        for shell in self.__shells:
                            if shell not in self.__busy_shells:
                                self.__busy_shells.add(shell)
                                break
                        else:
                            raise RuntimeError()  # cannot really happen

                        try:
                            shell.verify_alive()
                            break
                        except parzzley.fs.Site.ConnectionLostError:
                            self.__shells.remove(shell)
                            self.__busy_shells.remove(shell)

                try:
                    yield shell
                finally:
                    with self.__lock:
                        self.__busy_shells.remove(shell)
                        self.__shell_released.notify_all()

            def __new_shell(self) -> "ShellBasedBackend.Shell":
                for tries_left in reversed(range(5)):
                    try:
                        shell = self.__shell_factory(**self.__shell_kwargs)
                        shell.__enter__()  # pylint: disable=unnecessary-dunder-call
                        self.__shells.append(shell)
                        return shell
                    except Exception as ex:  # pylint: disable=broad-exception-caught
                        if tries_left:
                            time.sleep(2)
                        else:
                            raise parzzley.fs.Site.ConnectionLostError() from ex
                raise RuntimeError()  # cannot happen

        def __init__(self, shell_factory: t.Callable, shell_kwargs: dict, root_path: str):
            self.__shell_pool = ShellBasedBackend._SiteBackend._ShellPool(shell_factory, shell_kwargs)
            self.__root_path = root_path.encode()

        def item_type_by_cookie(self, cookie):
            if cookie is None:  # we also use it internally and need this behavior there
                return parzzley.fs.ItemType.NONE
            return parzzley.fs.ItemType[cookie[0]]

        async def move_item(self, item, to_item):
            path = self.__path(item)
            to_path = self.__path(to_item)
            with self.__shell_pool.shell() as shell:
                await shell.exec(("/bin/mv", "-T", path, to_path))

        async def create_item(self, item, item_type):
            item_full_path = self.__path(item)
            if item_type == parzzley.fs.ItemType.FILE:
                with self.__shell_pool.shell() as shell:
                    await shell.exec(("/bin/touch", item_full_path))
            elif item_type == parzzley.fs.ItemType.DIRECTORY:
                quoted_item_full_path = _shell_quote(item_full_path)
                with self.__shell_pool.shell() as shell:
                    exec_result = await shell.exec(
                        b"/bin/mkdir " + quoted_item_full_path + b" 2>&1"
                        b" || { [ -d " + quoted_item_full_path + b" ] && exit 123 || exit 1; }",
                        fail_on_error=False,
                    )
                    exit_code = exec_result.exit_code
                    if exit_code == 123:
                        raise parzzley.fs.Site.ItemExistsError()
                    if exit_code != 0:
                        raise IOError(exec_result.out.decode())
            elif item_type == parzzley.fs.ItemType.SYMLINK:
                with self.__shell_pool.shell() as shell:
                    await shell.exec(("/bin/ln", "-sTf", str(uuid.uuid4()), item_full_path))
            else:
                raise ValueError(f"invalid item type: {item_type}")

        async def cookie(self, item, stream_name):
            path = self.__path(item)
            with self.__shell_pool.shell() as shell:
                cmd_result = (
                    (await shell.exec(("/bin/stat", "-c", "%A\n%y", path), fail_on_error=False))
                    .out.decode()
                    .split("\n")
                )

            if len(cmd_result) < 2:
                return None

            info_str, mtime_str = cmd_result[:2]

            if stream_name == "":
                item_type = {
                    "-": parzzley.fs.ItemType.FILE,
                    "d": parzzley.fs.ItemType.DIRECTORY,
                    "l": parzzley.fs.ItemType.SYMLINK,
                }.get(info_str[0], parzzley.fs.ItemType.ALIEN)
                return item_type.name, mtime_str

            if stream_name == "xattrs":
                return parzzley.fs.utils.serialize_bytes_dict(await self.__get_xattrs(path)).decode()

            if stream_name == "posix":
                return await self.__get_posix(path)

            raise ValueError(f"invalid stream name: {stream_name}")

        async def remove_item(self, item, recursive):
            with self.__shell_pool.shell() as shell:
                if recursive:
                    await shell.exec(("/bin/rm", "-rf", self.__path(item)))
                else:
                    quoted_path = _shell_quote(self.__path(item))
                    await shell.exec(b"/bin/rm " + quoted_path + b" || /bin/rmdir " + quoted_path)

        async def child_names(self, item):
            path = self.__path(item)
            result = []
            with self.__shell_pool.shell() as shell:
                for line in (
                    (await shell.exec(("/bin/ls", "-A", "--quoting-style=c", "-1", path))).out.decode().split("\n")
                ):
                    if line:
                        result.append(ast.parse("b" + line).body[0].value.value)
            return result

        async def read_streamable(self, item, stream_name=""):
            path = self.__path(item)

            if stream_name == "":
                if self.item_type_by_cookie(await self.cookie(item, "")) == parzzley.fs.ItemType.SYMLINK:
                    with self.__shell_pool.shell() as shell:
                        link_target = (await shell.exec(("/bin/readlink", "-n", path))).out
                    return parzzley.fs.stream.MemoryReadStreamable(link_target)

                return ShellBasedBackend._SiteBackend._FileMainStreamReadStreamable(self.__shell_pool, path)

            if stream_name == "xattrs":
                return parzzley.fs.stream.MemoryReadStreamable(
                    parzzley.fs.utils.serialize_bytes_dict(await self.__get_xattrs(path))
                )

            if stream_name == "posix":
                return parzzley.fs.stream.MemoryReadStreamable((await self.__get_posix(path)).encode())

            raise ValueError(f"invalid stream name: {stream_name}")

        async def write_streamable(self, item, stream_name=""):
            path = self.__path(item)

            if stream_name == "":
                if self.item_type_by_cookie(await self.cookie(item, "")) == parzzley.fs.ItemType.SYMLINK:
                    return parzzley.fs.stream.MemoryWriteStreamable(functools.partial(self.__set_symlink_target, path))
                return ShellBasedBackend._SiteBackend._FileMainStreamWriteStreamable(self.__shell_pool, path)

            if stream_name == "xattrs":
                return parzzley.fs.stream.MemoryWriteStreamable(functools.partial(self.__set_xattrs, path))

            if stream_name == "posix":
                return parzzley.fs.stream.MemoryWriteStreamable(functools.partial(self.__set_posix, path))

            raise ValueError(f"invalid stream name: {stream_name}")

        async def wait_for_changes(self, on_changed):
            with self.__shell_pool.shell() as shell:
                if (await shell.exec('inotifywait -h >/dev/null; [ "$?" = "1" ]', fail_on_error=False)).exit_code != 0:
                    _logger.info(
                        "No change monitoring possible for %s (because 'inotifywait' is not available on that"
                        " system)",
                        self,
                    )
                    while True:
                        await asyncio.sleep(99999)

                process = await shell.exec_raw(
                    b"inotifywait -mr -e attrib,close_write,move,delete --format '}%w%f'"
                    b" " + _shell_quote(self.__root_path) + b" 2>/dev/null"
                )

                fd = process.stdout.fileno()
                flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

                try:
                    prefix = b"}" + self.__root_path
                    while True:
                        shell.verify_alive()
                        if not process.stdout.peek():
                            await asyncio.sleep(1)
                            continue
                        line = process.stdout.readline()
                        if line.startswith(prefix):
                            on_changed(parzzley.fs.item(line[len(prefix) : -1]))
                finally:
                    process.kill()
                    process.wait()

        async def disconnect(self):
            """
            Disconnect.
            """
            self.__shell_pool.disconnect()

        def __path(self, item) -> bytes:
            result = self.__root_path + b"/" + item.path
            if not pathlib.Path(os.fsdecode(result)).is_relative_to(os.fsdecode(self.__root_path)):
                raise IOError(f"invalid item path: {item.path}")
            return result

        async def __set_symlink_target(self, path, target):
            with self.__shell_pool.shell() as shell:
                await shell.exec(f"/bin/ln -sTf {shlex.quote(target.decode())} {shlex.quote(path)}")

        async def __get_posix(self, path) -> str:
            with self.__shell_pool.shell() as shell:
                cmd_output = (await shell.exec(("/bin/stat", "--format", "%Y\n%y", path))).out.decode().split("\n")
                mtime = int(cmd_output[0])
                mtime += float(re.match(r".*(\.\d+) ", cmd_output[1]).group(1))
            mtime = int(mtime * 1000**3)
            return f'{{"mtime": {mtime}}}'

        async def __set_posix(self, path, content):
            with self.__shell_pool.shell() as shell:
                await shell.exec(
                    ("/bin/touch", "-c", "-h", "-m", "-d", f"@{json.loads(content)["mtime"] / 1000 ** 3:f}", path)
                )

        async def __get_xattrs(self, path) -> dict[bytes, bytes]:
            xattrs = {}
            with self.__shell_pool.shell() as shell:
                for line in (
                    (await shell.exec(("/usr/bin/getfattr", "-h", "-e", "base64", "-d", path))).out.decode().split("\n")
                ):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, _, value_base64 = line.partition("=")
                        xattrs[key.encode()] = base64.b64decode(value_base64[2:])
            return xattrs

        async def __set_xattrs(self, path, content):
            xattrs = parzzley.fs.utils.deserialize_bytes_dict(content)

            for key in {*xattrs, *await self.__get_xattrs(path)}:
                if key.startswith(b"user."):
                    val = xattrs.get(key)
                    setfattr_args = (
                        ("-x", key.decode())
                        if val is None
                        else ("-n", key.decode(), "-v", f"0s{base64.b64encode(val).decode()}")
                    )
                    with self.__shell_pool.shell() as shell:
                        await shell.exec(("/usr/bin/setfattr", "-h", *setfattr_args, path))

        class _FileMainStreamWriteStreamable(parzzley.fs.stream.WriteStreamable):

            def __init__(self, shell_pool, path: bytes):
                self.__shell_pool = shell_pool
                self.__path = path

            class _WriteStream(parzzley.fs.stream.WriteStream):

                def __init__(self, shell_pool, path):
                    self.__shell_pool = shell_pool
                    self.__path = path

                async def __aenter__(self):
                    with self.__shell_pool.shell() as shell:
                        await shell.exec(("/bin/touch", self.__path))
                        await shell.exec(("/usr/bin/truncate", "-s0", self.__path))

                async def write(self, data):
                    with self.__shell_pool.shell() as shell:
                        i_block = 0
                        block_size = 32 * 1024**2
                        while True:
                            block = data[i_block * block_size : (i_block + 1) * block_size]
                            if not block:
                                break
                            i_block += 1
                            await shell.exec(
                                b"/usr/bin/dd bs=" + str(len(block)).encode() + b" count=1 iflag=fullblock"
                                b" >> " + _shell_quote(self.__path),
                                input=block,
                            )

                async def commit(self):
                    pass

            async def _stream(self):
                return ShellBasedBackend._SiteBackend._FileMainStreamWriteStreamable._WriteStream(
                    self.__shell_pool, self.__path
                )

        class _FileMainStreamReadStreamable(parzzley.fs.stream.ReadStreamable):

            def __init__(self, shell_pool, path: bytes):
                self.__shell_pool = shell_pool
                self.__path = path

            class _ReadStream(parzzley.fs.stream.ReadStream):

                def __init__(self, shell_pool, path):
                    self.__shell_pool = shell_pool
                    self.__path = path
                    self.__position = 0
                    self.__finished = False

                async def read(self, max_len):
                    if self.__finished:
                        return None
                    with self.__shell_pool.shell() as shell:
                        content_chunk = (
                            await shell.exec(
                                b"/usr/bin/dd if="
                                + _shell_quote(self.__path)
                                + b" skip="
                                + str(self.__position).encode()
                                + b"B "
                                b" count=" + str(max_len).encode() + b"B;"
                                b"/bin/echo X"
                            )
                        ).out[:-2]
                    if len(content_chunk) < max_len:
                        self.__finished = True
                    self.__position += len(content_chunk)
                    return content_chunk

            async def _stream(self):
                return ShellBasedBackend._SiteBackend._FileMainStreamReadStreamable._ReadStream(
                    self.__shell_pool, self.__path
                )

    class Shell(abc.ABC):
        """
        A shell allows to execute arbitrary command lines. See e.g. :py:meth:`exec`.

        Before usage, it needs to be entered (:code:`with`-block). It must only be entered once!
        """

        @dataclasses.dataclass(frozen=True)
        class ExecutionResult:
            """
            The execution result of a shell command line.
            """

            #: The exit code.
            exit_code: int

            #: The output of this command (does not include 'err').
            out: bytes

        def __init__(self):
            self.__process = None

        def __enter__(self) -> None:
            """
            Initialize this shell (or throw :py:class:`parzzley.fs.Site.ConnectionLostError` e.g. if the remote
            connection cannot be established for some reason).
            """
            try:
                self.__process = subprocess.Popen(
                    self._shell_cmdline(),
                    start_new_session=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )
                self.__write_stdin(b"\nexport PS1=''; export LC_ALL=C; /bin/echo asdf\n")
                while self.__process.stdout.readline().strip() != b"asdf":
                    self.verify_alive()
            except Exception as ex:
                raise parzzley.fs.Site.ConnectionLostError() from ex

        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            Uninitialize this shell.

            Only called for shells that were successfully entered before.
            """
            try:
                self.__process.terminate()
            except Exception:  # pylint: disable=broad-exception-caught
                _logger.warning(traceback.format_exc())
            self.__process = None

        @abc.abstractmethod
        def _shell_cmdline(self) -> t.Sequence[str]:
            """
            Return the command line for starting this shell.

            This is implemented by subclasses and only used internally.
            """

        async def exec_raw(self, cmd_line: bytes) -> subprocess.Popen:
            """
            Execute a command line and return the process object for further communication.

            This shell must be currently entered in order to execute commands.

            Note: This is a low-level method for particular use cases. Usually :py:meth:`exec` should be used instead.

            If problems occur, e.g. because it just lost the connection to the remote side, it will raise
            :py:class:`parzzley.fs.Site.ConnectionLostError`. See also :py:meth:`verify_alive` for later checks whether
            the shell is still alive.

            :param cmd_line: The command line to execute.
            """
            try:
                self.__write_stdin(cmd_line)
                self.__write_stdin(b"\n")
            except Exception as ex:
                raise parzzley.fs.Site.ConnectionLostError() from ex

            self.verify_alive()
            return self.__process

        async def exec(  # pylint: disable=redefined-builtin
            self, cmd_line: str | bytes | t.Iterable[str | bytes], *, fail_on_error: bool = True, input: bytes = b""
        ) -> ExecutionResult:
            """
            Execute a command line and return the execution result.

            This shell must be currently entered in order to execute commands.

            If problems occur in the low-level implementation, e.g. because it just lost the connection to the remote
            side, it will raise :py:class:`parzzley.fs.Site.ConnectionLostError`.

            :param cmd_line: The command line to execute.
            :param fail_on_error: Whether to fail (with an :code:`IOError`) if the exit-code is nonzero.
            :param input: The input to stream to the command.
            """
            if isinstance(cmd_line, str):
                cmd_line_str = cmd_line.encode()
            elif isinstance(cmd_line, bytes):
                cmd_line_str = cmd_line
            else:
                cmd_line_str = b" ".join(
                    _shell_quote(_) for _ in (_.encode() if isinstance(_, str) else _ for _ in cmd_line)
                )

            cmd_line_str = (
                b"/bin/echo begin; { (" + cmd_line_str + b") 2>/dev/null ; /bin/echo -n '\n'$?; }"
                b" | /usr/bin/base64 -w0 ; /bin/echo"
            )

            try:
                process = await self.exec_raw(cmd_line_str)
                process.stdout.readline()
                while input:
                    input = input[process.stdin.write(input) :]
                    process.stdin.flush()
                output_line = process.stdout.readline()
                output = base64.b64decode(output_line).removesuffix(b"\n")
                i = output.rfind(b"\n")
                exit_code = int(output[i:].decode())
                output = output[:i]
            except Exception as ex:
                raise parzzley.fs.Site.ConnectionLostError() from ex
            self.verify_alive()

            result = self.ExecutionResult(exit_code, output)

            if result.exit_code != 0 and fail_on_error:
                raise IOError(f"command line {cmd_line!r} failed with exit-code {result.exit_code}: {result.out}")

            return result

        def verify_alive(self):
            """
            Check whether this shell is still alive (e.g. has not lost connection to its remote side) and raise a
            :py:class:`parzzley.fs.Site.ConnectionLostError` if not.

            You only need this method for :py:meth:`exec_raw`.
            """
            if not self.__process or self.__process.poll() is not None:
                raise parzzley.fs.Site.ConnectionLostError()

        def __write_stdin(self, b):
            while b:
                b = b[self.__process.stdin.write(b) :]
            self.__process.stdin.flush()


_find_unsafe = re.compile(rb"[^\w@%+=:,./-]", re.ASCII).search


def _shell_quote(s: bytes) -> bytes:
    """
    Return a shell-escaped version of the given byte string.

    :param s: The byte string.
    """
    if not s:
        return b"''"
    if _find_unsafe(s) is None:
        return s
    return b"'" + s.replace(b"'", b"'\"'\"'") + b"'"
