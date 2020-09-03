import functools
from typing import Iterable, Union

import fs as pyfs
import fs.base
import fs.errors
import fs.info

from ..base.shell import FtpShell, DirectoryNotEmpty, FileInfo
from . import aioexecutor


def _offload(fn):
    @functools.wraps(fn)
    async def _offloaded(self, *args, **kwargs):
        return await self.executor.run(lambda: fn(self, *args, **kwargs))
    return _offloaded


def open_fs_patched(url: str):
    if url.startswith("gcs-patched://"):
        bucket_name, root_path = url[14:].split('/', 1)
        from pyfsftpserver.patches.patched_gcsfs import PatchedGCSFS
        return PatchedGCSFS(bucket_name, root_path=root_path)
    return pyfs.open_fs(url)


class PyfsFtpShell(FtpShell):
    fs: pyfs.base.FS
    cwd: str

    def __init__(self, fs: Union[str, pyfs.base.FS], cwd=None, executor=None, threaded=None):
        if cwd is None:
            cwd = "/"
        if threaded is None:
            threaded = True
        if executor is None:
            executor = aioexecutor.create(threaded)
        if isinstance(fs, str):
            fs = open_fs_patched(fs)
        self.fs = fs
        self.cwd = cwd
        self.executor = executor

    async def set_cwd(self, path):
        self.cwd = path

    async def get_cwd(self):
        return self.cwd

    async def change_dir(self, path):
        cwd = self._resolvepath(path)
        self.cwd = cwd
        return cwd

    async def change_dir_up(self):
        cwd = pyfs.path.dirname(self.cwd)
        self.cwd = cwd
        return cwd

    @_offload
    def list_dir(self, path) -> Iterable[FileInfo]:
        path = self._resolvepath(path)
        # TODO: explicit conversion from pyfs.info.Info to FileInfo
        infos: Iterable[pyfs.info.Info] = self.fs.scandir(path, namespaces=["details"])
        infos = list(infos)
        return infos

    @_offload
    def make_dir(self, path):
        path = self._resolvepath(path)
        self.fs.makedir(path)

    @_offload
    def open_read(self, path):
        path = self._resolvepath(path)
        return self.fs.open(path, 'rb')

    @_offload
    def open_write(self, path):
        path = self._resolvepath(path)
        return self.fs.open(path, 'wb')

    @_offload
    def remove_file(self, path):
        path = self._resolvepath(path)
        return self.fs.remove(path)

    @_offload
    def remove_dir(self, path):
        path = self._resolvepath(path)
        try:
            return self.fs.removedir(path)
        except pyfs.errors.DirectoryNotEmpty:
            raise DirectoryNotEmpty()

    def _resolvepath(self, path):
        if path is None:
            return self.cwd
        return pyfs.path.join(self.cwd, path)

    def close(self):
        self.executor.close()
