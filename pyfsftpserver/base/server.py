import asyncio
import logging
from asyncio import StreamWriter, StreamReader

from pyfsftpserver.base import utils
from pyfsftpserver.base.default_context import DefaultContextMixin
from pyfsftpserver.base.utils import get_server_endpoint, Channel, IpEndpoint
from pyfsftpserver.di.context import Context

logger = logging.getLogger(__name__)


class FtpServer(DefaultContextMixin):
    def __init__(self, host=None, port=None):
        if port is None:
            port = 2121
        if host is None:
            host = "127.0.0.1"
        self.host = host
        self.port = port
        self.server = None
        self.context_def = self

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

    def get_server_endpoint(self):
        return get_server_endpoint(self.server)

    @property
    def server_port(self):
        return self.get_server_endpoint().port

    @property
    def server_address(self):
        return self.get_server_endpoint().address

    async def _handle_client(self, reader: StreamReader, writer: StreamWriter):
        try:
            command_channel = Channel(reader=reader, writer=writer)
            logger.info(f"Client connected {command_channel.remote_endpoint}")
            context = self._make_context(command_channel=command_channel)
            protocol_interpreter = context['protocol_interpreter']
            await protocol_interpreter.run()
        except Exception as ex:
            logger.exception("Uncaught error during handling client connection", ex)

    def _make_context(self, command_channel):
        parent = {
            'command_channel': command_channel,
            'data_endpoint_config': IpEndpoint(address=self.host, port=None),
        }
        return Context(
            context_def=self.context_def,
            parent=parent,
        )


def print_listening_message(server: FtpServer):
    ap = server.get_server_endpoint()
    logger.info(f"Started listening on {ap.address}:{ap.port}")


_BUFFER_SIZE = 8192
