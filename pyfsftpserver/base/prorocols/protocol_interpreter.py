import logging
from abc import ABC

from ..messages import Reply, Command
from .command_channel import CommandChannelContext

logger = logging.getLogger(__name__)


DEFAULT_ENCODING = 'ascii'


class ProtocolInterpreter:
    implementation_context: 'ProtocolInterpreterContext'

    def __init__(self, command_channel, host, implementation_context: 'ProtocolInterpreterContext'):
        self.command_channel = command_channel
        self.host = host

        self.data_protocol = implementation_context.data_protocol_factory(
            host=host,
        )
        self.controller = implementation_context.command_protocol_factory(data_protocol=self.data_protocol)
        self.implementation_context = implementation_context

    async def run(self):
        try:
            await self._respond(Reply("220", "awaiting input"))
            while self.controller.running:
                await self._read_and_handle_command()
        finally:
            self.close()

    async def _read_and_handle_command(self):
        line = await self._readline()
        logger.info(f"cmd recv  <   {line!r}")
        result = await self._process_line(line)
        await self._respond(result)

    async def _readline(self):
        line = await self.command_channel.reader.readuntil(b'\n')
        line = line.decode(encoding=self.implementation_context.encoding)
        return line.rstrip('\r\n')

    async def _process_line(self, line):
        cmd = self._parse_command(line)
        return await self._process_command(cmd)

    def _parse_command(self, line):
        cmd, sep, arg = line.partition(" ")
        if not sep:
            arg = None
        return Command(cmd=cmd.lower(), arg=arg)

    async def _process_command(self, cmd: Command):
        return await self.controller.process(cmd.cmd, cmd.arg)

    def _format_reply(self, reply):
        Reply.validate(reply)
        if not reply.items:
            yield f"{reply.code} {reply.text}"
            return
        yield f"{reply.code}- {reply.text}"
        for item in reply.items:
            yield f" {item}"
        yield f"{reply.code} END"

    async def _respond(self, reply):
        if reply is None:
            reply = Reply.OK
        if reply.payload is not None:
            await self._send_payload(reply.payload)
            return
        if reply.sink is not None:
            await self._receive_payload_into(reply.sink)
            return
        for line in self._format_reply(reply):
            await self._write_command_line(line)

    async def _receive_payload_into(self, writer):
        await self._write_command_line("150 opening ascii data connection")
        try:
            await self.data_protocol.receive_payload_into(writer)
        except Exception as ex:
            await self._write_command_line("451 error while receiving payload")
            logger.exception("Error while seinding payload", ex)
        else:
            await self._write_command_line("226 transfer complete")

    async def _send_payload(self, payload):
        await self._write_command_line("150 opening ascii data connection")
        try:
            await self.data_protocol.send_payload(payload)
        except Exception as ex:
            await self._write_command_line("451 error while sending payload")
            logger.exception("Error while seinding payload", ex)
        else:
            await self._write_command_line("226 transfer complete")

    async def _write_command_line(self, data: str):
        logger.info(f"cmd send >    {data!r}")
        data = data.encode(encoding=self.implementation_context.encoding)
        writer = self.command_channel.writer
        writer.write(data)
        writer.write(b"\r\n")
        await writer.drain()

    def close(self):
        self.controller.close()


class ProtocolInterpreterContext(CommandChannelContext, ABC):
    def data_protocol_factory(self, host):
        raise NotImplementedError()

    def command_protocol_factory(self, data_protocol):
        raise NotImplementedError()
