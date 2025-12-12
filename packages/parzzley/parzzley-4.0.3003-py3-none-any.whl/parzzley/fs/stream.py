#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Filesystem streams.
"""
import abc
import contextlib
import typing as t


class ReadStream(abc.ABC):
    """
    Base class for read streams.

    A read stream is able to provide arbitrary binary content in chunk-wise manner (see :py:meth:`read`).

    After it is consumed once, it cannot be used anymore. It should not be used directly for any API, but only by
    internal code. See :py:class:`ReadStreamable` instead.
    """

    async def __aenter__(self) -> None:
        """
        Automatically called by the streamable for stream preparation.
        """

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically called by the streamable for stream shutdown (e.g. in order to release resources).
        """

    @abc.abstractmethod
    async def read(self, max_len: int) -> bytes | None:
        """
        Read the next chunk of data from the stream and return it, or return :code:`None` if the end of the stream has
        been reached.

        :param max_len: The maximum chunk length.
        """


class WriteStream(abc.ABC):
    """
    Base class for write streams.

    A write stream is able to receive arbitrary binary content in chunk-wise manner. Once everything is written (see
    :py:meth:`write`), one has to :py:meth:`commit`. Otherwise, everything written before might only exist in some
    hidden, temporary place (client code must never rely on that, though).

    After it is committed once, it cannot be used anymore. It should not be used directly for any API, but only by
    internal code. See :py:class:`WriteStreamable` instead.
    """

    async def __aenter__(self) -> None:
        """
        Automatically called by the streamable for stream preparation.
        """

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically called by the streamable for stream shutdown (e.g. in order to release resources).
        """

    @abc.abstractmethod
    async def write(self, data: bytes) -> None:
        """
        Append a chunk of data to the stream.

        :param data: The data.
        """

    @abc.abstractmethod
    async def commit(self) -> None:
        """
        Commit the written data.
        """


class ReadStreamable(abc.ABC):
    """
    Base class for read-streamables.

    A read-streamable can create :py:class:`ReadStream` instances (so, in contrast to that one, it can be used multiple
    times).
    """

    @contextlib.asynccontextmanager
    async def stream(self) -> t.AsyncGenerator[ReadStream]:
        """
        Return a context manager (:code:`with`-block) that provides a :py:class:`ReadStream` for the actual read
        operation.
        """
        read_stream = await self._stream()
        async with read_stream:
            yield read_stream

    async def read_bytes(self) -> bytes:
        """
        Convenience function that reads the complete binary content at once.
        """
        content = b""
        async with self.stream() as stream:
            while True:
                buf = await stream.read(1024 * 1024)
                if buf is None:
                    break
                content += buf
        return content

    @abc.abstractmethod
    async def _stream(self) -> ReadStream:
        """
        Return a new stream.

        This method is implemented by subclasses and only used internally. See :py:meth:`stream`.
        """


class WriteStreamable(abc.ABC):
    """
    Base class for write-streamables.

    A write-streamable can create :py:class:`WriteStream` instances (so, in contrast to that one, it can be used
    multiple times).
    """

    @contextlib.asynccontextmanager
    async def stream(self) -> t.AsyncGenerator[WriteStream]:
        """
        Return a context manager (:code:`with`-block) that provides a :py:class:`WriteStream` for the actual write
        operation.
        """
        write_stream = await self._stream()
        async with write_stream:
            yield write_stream

    async def write_bytes(self, content: bytes) -> None:
        """
        Convenience function that writes a complete binary content at once.

        :param content: The binary content to write.
        """
        async with self.stream() as stream:
            await stream.write(content)
            await stream.commit()

    @abc.abstractmethod
    async def _stream(self) -> WriteStream:
        """
        Return a new stream.

        This method is implemented by subclasses and only used internally. See :py:meth:`stream`.
        """


class MemoryReadStreamable(ReadStreamable):
    """
    A memory backed read-streamable.
    """

    class _ReadStream(ReadStream):

        def __init__(self, content: bytes):
            super().__init__()
            self.__content = content
            self.__position = 0

        async def read(self, max_len):
            if self.__position == len(self.__content):
                return None
            answer = self.__content[self.__position : self.__position + max_len]
            self.__position += len(answer)
            return answer

    def __init__(self, content: bytes):
        """
        :param content: The content of this stream.
        """
        super().__init__()
        self.__content = content

    async def _stream(self):
        return MemoryReadStreamable._ReadStream(self.__content)


class MemoryWriteStreamable(WriteStreamable):
    """
    A memory backed write-streamable.
    """

    class _WriteStream(WriteStream):

        def __init__(self, commit_func: t.Callable):
            """
            :param commit_func: The commit function to call when a stream finished writing.
            """
            super().__init__()
            self.__content = b""
            self.__commit_func = commit_func

        async def write(self, data):
            self.__content += data

        async def commit(self):
            await self.__commit_func(self.__content)

    def __init__(self, commit_func: t.Callable):
        super().__init__()
        self.__commit_func = commit_func

    async def _stream(self):
        return MemoryWriteStreamable._WriteStream(self.__commit_func)
