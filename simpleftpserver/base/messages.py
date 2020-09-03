import typing
from dataclasses import dataclass
from typing import Union


class ReplyBase:
    code: str
    text: str
    payload: Union[None, bytes, bytearray, typing.AsyncIterable, typing.Iterable]


class Reply(ReplyBase):
    def __init__(self, code="200", text="OK", payload=None, sink=None, items=None):
        self.code = code
        self.text = text
        self.items = items
        self.payload = payload
        self.sink = sink
        Reply.validate(self)

    @staticmethod
    def validate(reply):
        assert "\n" not in reply.text
        assert " " not in reply.code
        assert "\n" not in reply.code


Reply.OK = Reply()


class UnknownCommandReply(Reply):
    def __init__(self, cmd):
        super().__init__("502", f"Unknown command {cmd}")
        self.cmd = cmd


@dataclass(frozen=True)
class Command:
    cmd: str
    arg: typing.Optional[str]
