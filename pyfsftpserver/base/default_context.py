from dataclasses import dataclass
from typing import Optional

from pyfsftpserver.base.prorocols import ProtocolInterpreter
from pyfsftpserver.base.prorocols.command_channel import CommandHandler, CommandProtocol
from pyfsftpserver.base.prorocols.data_channel import DataProtocol
from pyfsftpserver.base.prorocols.mlsx_format import MlsxFormatter, ListFormatter
from pyfsftpserver.base.prorocols.protocol_interpreter import DEFAULT_ENCODING
from pyfsftpserver.base.utils import DEFAULT_BUFFER_SIZE


@dataclass
class ProtocolConfig:
    encoding: str
    buffer_size: int


class DefaultContextMixin:
    bean_protocol_interpreter = ProtocolInterpreter
    bean_command_protocol = CommandProtocol
    bean_command_handler = CommandHandler
    bean_data_protocol = DataProtocol

    config_encoding = DEFAULT_ENCODING
    config_buffer_size = DEFAULT_BUFFER_SIZE

    @staticmethod
    def bean_mlsx_formatter(ctx):
        return MlsxFormatter()

    @staticmethod
    def bean_list_formatter(ctx):
        return ListFormatter()

    @classmethod
    def bean_protocol_config(cls, ctx):
        return ProtocolConfig(
            encoding=cls.config_encoding,
            buffer_size=cls.config_buffer_size,
        )

    def bean_shell_factory(self, ctx):
        return self.create_shell

    async def create_shell(self, username):
        raise NotImplementedError()
