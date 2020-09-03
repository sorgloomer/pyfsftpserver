import datetime
from typing import Union, Iterable, AsyncIterable


class FileInfo:
    is_dir: bool
    name: str
    size: int
    modified: datetime.datetime
    created: datetime.datetime


class ShellException(Exception):
    pass


class DirectoryNotEmpty(ShellException):
    pass


class FtpShell:
    async def set_cwd(self, path):
        raise NotImplementedError()

    async def get_cwd(self):
        raise NotImplementedError()

    async def change_dir(self, path):
        raise NotImplementedError()

    async def change_dir_up(self):
        raise NotImplementedError()

    async def list_dir(self, path) -> Union[Iterable[FileInfo], AsyncIterable[FileInfo]]:
        raise NotImplementedError()

    async def make_dir(self, path):
        raise NotImplementedError()

    async def open_read(self, path):
        raise NotImplementedError()

    async def open_write(self, path):
        raise NotImplementedError()

    async def remove_file(self, path):
        raise NotImplementedError()

    async def remove_dir(self, path):
        raise NotImplementedError()

    def close(self):
        pass
