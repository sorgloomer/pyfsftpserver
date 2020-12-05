import logging

from ..messages import Reply, Command

logger = logging.getLogger(__name__)


DEFAULT_ENCODING = 'utf-8'


class ProtocolInterpreter:
    def __init__(self, ctx):
        self.data_protocol = ctx['data_protocol']
        self.command_channel = ctx['command_channel']
        self.command_protocol = ctx['command_protocol']
        self.command_handler = ctx['command_handler']
        self.protocol_config = ctx['protocol_config']

    async def run(self):
        try:
            await self._respond(Reply("220", "awaiting input"))
            while self.command_handler.running:
                await self._read_and_handle_command()
        finally:
            self.close()

    def _log_error_and_make_reply(self, msg, ex, code="500"):
        logger.exception(msg, ex)
        return Reply(code, f"{msg}: {ex}".replace('\r\n', ' '))

    async def _read_command_handle_errors_return_result(self) -> Reply:
        try:
            line = await self.command_channel.reader.readuntil(b'\n')
        except:
            raise ProtocolInterpreterError("Error while reading command")
        try:
            line = line.decode(encoding=self.protocol_config.encoding)
            line = line.rstrip('\r\n')
        except:
            raise ProtocolInterpreterError("Error while decoding command")

        logger.info(f"cmd recv  <   {line!r}")
        try:
            return await self._process_line(line)
        except:
            raise ProtocolInterpreterError("Error while processing command")

    async def _read_and_handle_command(self):
        try:
            reply = await self._read_command_handle_errors_return_result()
        except Exception as ex:
            reply = self._log_error_and_make_reply("Error while processing command", ex)
        try:
            await self._respond(reply)
        except Exception as ex:
            logger.exception("Unknown error while sending reply", ex)
            await self._respond(Reply("500", "Unknown error while sending reply"))

    async def _readline(self):
        line = await self.command_channel.reader.readuntil(b'\n')
        line = line.decode(encoding=self.protocol_config.encoding)
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
        return await self.command_protocol.process(cmd.cmd, cmd.arg)

    def _format_reply(self, reply):
        Reply.validate(reply)
        if not reply.items:
            yield f"{reply.code} {reply.text}"
            return
        yield f"{reply.code}- {reply.text}"
        for item in reply.items:
            yield f" {item}"
        yield f"{reply.code} END"

    async def _respond(self, reply: Reply):
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
        data = data.encode(encoding=self.protocol_config.encoding)
        writer = self.command_channel.writer
        writer.write(data)
        writer.write(b"\r\n")
        await writer.drain()

    def close(self):
        self.command_handler.close()


class ProtocolInterpreterError(Exception):
    pass
