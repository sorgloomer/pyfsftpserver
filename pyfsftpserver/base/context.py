from abc import ABC

from .prorocols import ProtocolInterpreter
from .prorocols.command_channel import CommandHandler
from .prorocols.data_channel import DataProtocol
from .prorocols.protocol_interpreter import DEFAULT_ENCODING, ProtocolInterpreterContext
from .utils import Channel, DEFAULT_BUFFER_SIZE


class DefaultImplementationContext(ProtocolInterpreterContext, ABC):
    encoding = DEFAULT_ENCODING
    buffer_size = DEFAULT_BUFFER_SIZE

    def protocol_interpreter_factory(self, command_channel: Channel, host: str):
        return ProtocolInterpreter(command_channel=command_channel, host=host, implementation_context=self)

    def command_protocol_factory(self, data_protocol):
        return CommandHandler(data_protocol=data_protocol, implementation_context=self)

    def data_protocol_factory(self, host, port=None):
        return DataProtocol(host, port=port)
