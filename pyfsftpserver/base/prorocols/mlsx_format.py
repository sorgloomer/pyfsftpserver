import datetime
import re
from typing import Iterable

from ..shell import FileInfo


class ListFormatter:
    def format_line(self, item: FileInfo) -> str:
        raise NotImplementedError()

    def format_all(self, items: Iterable[FileInfo]):
        for item in items:
            line = self.format_line(item)
            yield line


class MlsxFormatter(ListFormatter):
    re_feat_key = re.compile("^[^\r\n=; ]*$")
    re_feat_value = re.compile("^[^\r\n;]*$")
    re_path = re.compile("^[^\r\n]*$")

    @staticmethod
    def format_timeval(dt: datetime.datetime):
        if dt is None:
            return None
        return dt.strftime("%Y%m%d%H%M%S.%f")[:-3]  # Some FTP clients don't accept microseconds

    def format_line(self, fileinfo: FileInfo):
        return self.format_feats(feats={
            "type": "dir" if fileinfo.is_dir else "file",
            "size": str(fileinfo.size),
            "create": self.format_timeval(fileinfo.created),
            "modify": self.format_timeval(fileinfo.modified),
        }, path=fileinfo.name)

    def format_feats(self, feats, path):
        assert self.re_path.match(path) is not None
        return "".join(self.format_feat(k, v) for k, v in feats.items() if v is not None) + " " + path

    def format_feat(self, k: str, v: str):
        assert self.re_feat_key.match(k) is not None
        assert self.re_feat_value.match(v) is not None
        return f"{k}={v};"


class FileListFormatter(ListFormatter):
    def format_line(self, f: FileInfo):
        size = f.size
        name = f.name
        modified = self.format_date(f.modified)
        perms = self.format_permissions(f)
        return f"{perms} 1 user group {size} {modified} {name}"

    @staticmethod
    def format_permissions(f):
        d = 'd' if f.is_dir else '-'
        return f'{d}rw-rw-rw-'

    def format_date(self, dt: datetime.datetime):
        if dt is None:
            return "-"
        if self.delta_since(dt) > datetime.timedelta(days=182):
            return dt.strftime("%b %d %Y")
        return dt.strftime("%b %d %H:%M")

    @staticmethod
    def delta_since(dt):
        dtnow = datetime.datetime.now(datetime.timezone.utc)
        return dtnow - dt
