import asyncio
import logging
from abc import ABC
from asyncio import StreamWriter, StreamReader

from . import utils
from .context import DefaultImplementationContext
from .utils import get_server_address_and_port, Channel

logger = logging.getLogger(__name__)


class FtpServer(DefaultImplementationContext, ABC):
    def __init__(self, host=None, port=None, implementation_context=None):
        if port is None:
            port = 2121
        if host is None:
            host = "127.0.0.1"
        if implementation_context is None:
            implementation_context = self
        self.port = port
        self.host = host
        self.server = None
        self.implementation_context = implementation_context

    async def run(self, on_before_listening=None):
        await self._setup()
        if on_before_listening is not None:
            await utils.as_awaitable(on_before_listening(self))
        await self._serve()

    async def _setup(self):
        self.server = await asyncio.start_server(self._handle_client, host=self.host, port=self.port)

    async def _serve(self):
        async with self.server:
            await self.server.serve_forever()

    def get_server_address_and_port(self):
        return get_server_address_and_port(self.server)

    @property
    def server_port(self):
        return self.get_server_address_and_port().port

    @property
    def server_address(self):
        return self.get_server_address_and_port().address

    async def _handle_client(self, reader: StreamReader, writer: StreamWriter):
        try:
            logger.info(f"Client connected")
            await self.protocol_interpreter_factory(
                Channel(reader=reader, writer=writer),
                host=self.host,
            ).run()
        except Exception as ex:
            logger.exception("Uncaught error during handling client connection", ex)


def print_listening_message(server: FtpServer):
    ap = server.get_server_address_and_port()
    logger.info(f"Started listening on {ap.address}:{ap.port}")


_BUFFER_SIZE = 8192
