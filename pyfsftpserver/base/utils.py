import asyncio
import collections.abc
from asyncio import StreamReader, StreamWriter
from collections import namedtuple
from collections.abc import Awaitable


AddressAndPort = namedtuple("AddressAndPort", ["address", "port"])


class ChannelHolder:
    def __init__(self, value=None):
        self.value = value
        self._semaphore = asyncio.Semaphore()

    def set(self, value):
        if self.value is not None:
            self.value.close()
        self.value = value
        self._semaphore.release()

    async def get_one(self, reset=False):
        while True:
            await self._semaphore.acquire()
            value = self.value
            if value is None:
                continue
            if reset:
                self.value = None
            return value

    async def get_now(self, reset=False):
        value = self.value
        if reset:
            self.value = None
        return value


class Channel:
    reader: StreamReader
    writer: StreamWriter
    buffer_size: int

    def __init__(self, reader, writer, on_write_chunk=None, buffer_size=None):
        if buffer_size is None:
            buffer_size = DEFAULT_BUFFER_SIZE
        self.reader = reader
        self.writer = writer
        self.buffer_size = buffer_size
        self.on_write_chunk = on_write_chunk

    async def readuntil(self, separator=b'\n'):
        return await self.reader.readuntil(separator)

    async def read_all_into(self, writer, buffer_size=None):
        if buffer_size is None:
            buffer_size = self.buffer_size
        while True:
            data = await self.reader.read(buffer_size)
            if not data:
                return
            await as_awaitable(writer(data))

    def close(self):
        self.writer.close()

    async def write_all(self, data, flush=True, close=False):
        try:
            if data is None:
                return
            await self._write_all(data)
            if flush:
                await self.flush()
        finally:
            if close:
                self.close()

    async def flush(self):
        await self.writer.drain()

    async def _write_all(self, data):
        if isinstance(data, (bytes, bytearray)):
            self._write_chunk(data)
        elif isinstance(data, collections.abc.AsyncIterable):
            async for chunk in data:
                self._write_chunk(chunk)
        else:
            for chunk in data:
                self._write_chunk(chunk)

    def _write_chunk(self, data):
        if self.on_write_chunk is not None:
            self.on_write_chunk(data)
        self.writer.write(data)


async def as_awaitable(value):
    if isinstance(value, Awaitable):
        return await value
    return value


def get_server_address_and_port(server):
    addr, port = server.sockets[0].getsockname()
    return AddressAndPort(address=addr, port=port)


DEFAULT_BUFFER_SIZE = 2 ** 14
