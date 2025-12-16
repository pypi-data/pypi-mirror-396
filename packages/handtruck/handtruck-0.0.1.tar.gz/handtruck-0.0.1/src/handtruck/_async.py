from abc import abstractmethod
import contextlib
import functools
import os
import typing

import anyio.from_thread
import anyio.to_thread
import anyio.streams.file
import anyio.streams.memory


QUEUE_SIZE = 32


def generate_in_thread(func: typing.Callable) -> typing.Callable:
    @functools.wraps(func)
    async def _(*pargs, **kwargs):
        def thread_wrapper(stream: anyio.streams.memory.MemoryObjectSendStream):
            for item in func(*pargs, **kwargs):
                anyio.from_thread.run(stream.send, item)

        async def async_wrapper(stream: anyio.streams.memory.MemoryObjectSendStream):
            async with stream:
                await anyio.to_thread.run_sync(thread_wrapper, stream)

        send_stream, recv_stream = anyio.create_memory_object_stream(max_buffer_size=QUEUE_SIZE)
        async with anyio.create_task_group() as tg:
            tg.start_soon(async_wrapper, send_stream, name=f"{func}")
            async with recv_stream:
                async for item in recv_stream:
                    yield item

    return _


def run_in_thread(func):
    @functools.wraps(func)
    def _(*p, **kw):
        return anyio.to_thread.run_sync(lambda: func(*p, **kw))

    return _


FileChunk = tuple[int, bytes]

ChunkSendStream = anyio.streams.memory.MemoryObjectSendStream[FileChunk]


class ParallelFileWriterBase(anyio.AsyncContextManagerMixin):
    _fp: anyio.AsyncFile[bytes]
    _size_hint: int | None

    def __init__(self, fp: anyio.AsyncFile, total_size: int | None = None):
        self._fp = fp
        self._size_hint = total_size

    @abstractmethod
    def __asynccontextmanager__(self) -> typing.AsyncContextManager[typing.Self]:
        ...

    async def _fallocate(self, start: int, end: int):
        if hasattr(os, 'posix_fallocate'):
            fd: int|None = self._fp.wrapped.fileno()
            if fd is not None:
                await anyio.to_thread.run_sync(os.posix_fallocate, fd, start, end-start)

    @abstractmethod
    async def get_block(self, start: int|None = None, end: int|None = None) -> ChunkSendStream:
        """
        Get a stream. start and end are hints, but not binding.
        """
        ...


class ChunkSendStream_Pwrite(ChunkSendStream):
    _file: anyio.AsyncFile[bytes]

    def __init__(self, file: anyio.AsyncFile[bytes]):
        self._file = file

    async def send(self, item: FileChunk) -> None:
        fd = self._file.wrapped.fileno()
        position, data = item
        try:
            while data:
                actual = await anyio.to_thread.run_sync(os.pwrite, fd, data, position)
                position += actual
                data = data[actual:]
        except ValueError:
            raise anyio.ClosedResourceError from None
        except OSError as exc:
            raise anyio.BrokenResourceError from exc

    async def aclose(self):
        # Do nothing, not our file
        pass


class PWriteFileWriter(ParallelFileWriterBase):
    """
    Just wraps pwrite() as thinly as possible.
    """
    def __init__(self, fp: anyio.AsyncFile, total_size: int | None = None):
        super().__init__(fp, total_size)
        self._stream = ChunkSendStream_Pwrite(fp)

    @contextlib.asynccontextmanager
    async def __asynccontextmanager__(self) -> typing.AsyncGenerator[typing.Self, None]:
        if self._size_hint is not None:
            await self._fallocate(0, self._size_hint)
        yield self

    async def get_block(self, start: int|None = None, end: int|None = None) -> ChunkSendStream:
        if start is not None and end is not None:
            await self._fallocate(start, end)
        # We can just return the same stream every time because it's not
        # actually tracking anything, it's just a shell around calling pwrite()
        return self._stream


class SyncedFileWriter(ParallelFileWriterBase):
    _stream: ChunkSendStream

    async def _recv_task(self, stream: anyio.abc.ObjectReceiveStream[FileChunk]):
        async with stream:
            async for position, data in stream:
                await self._fp.seek(position)
                await self._fp.write(data)

    @contextlib.asynccontextmanager
    async def __asynccontextmanager__(self) -> typing.AsyncGenerator[typing.Self, None]:
        if self._size_hint is not None:
            await self._fallocate(0, self._size_hint)
        self._stream, receive_stream = anyio.create_memory_object_stream()
        async with anyio.create_task_group() as tg:
                tg.start_soon(self._recv_task, receive_stream)
                yield self
                self._stream.close()


    async def get_block(self, start: int|None = None, end: int|None = None) -> ChunkSendStream:
        if start is not None and end is not None:
            await self._fallocate(start, end)
        return self._stream.clone()

def parallel_file_writer(fp: anyio.AsyncFile, total_size: int | None = None) -> ParallelFileWriterBase:
        if hasattr(os, 'pwrite'):
            return PWriteFileWriter(fp, total_size)
        else:
            return SyncedFileWriter(fp, total_size)
