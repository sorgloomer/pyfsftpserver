import asyncio

from ..utils import ChannelHolder, get_server_address_and_port, Channel


class DataProtocol:
    def __init__(self, host, port=None):
        self.server = None
        self.host = host
        self.port = port
        self.channel_holder = ChannelHolder()

    def close(self):
        self.channel_holder.set(None)  # This should close the open connection, if any
        if self.server is not None:
            self.server.close()

    async def enter_passive_mode(self):
        if self.server is None:
            self.server = await self._create_server()
        return get_server_address_and_port(self.server)

    async def _create_server(self):
        port = self.port
        if port is None:
            port = 0
        return await asyncio.start_server(self._store_data_channel, host=self.host, port=port)

    def _store_data_channel(self, reader, writer):
        channel = Channel(reader=reader, writer=writer)
        self.channel_holder.set(channel)

    async def _wait_conn(self):
        return await self.channel_holder.get_one(reset=True)

    async def send_payload(self, payload):
        data_channel = await self._wait_conn()
        await data_channel.write_all(payload, close=True)

    async def receive_payload_into(self, writer):
        async def _sink_write(chunk):
            writer.write(chunk)
        data_channel = await self._wait_conn()
        await data_channel.read_all_into(_sink_write)
        writer.close()
