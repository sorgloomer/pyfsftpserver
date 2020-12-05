from .shell import PyfsFtpShell
from ..base.server import FtpServer


class PyfsFtpServer(FtpServer):
    def __init__(self, pyfs_url=None, host=None, port=None, threaded=None):
        if pyfs_url is None:
            pyfs_url = "osfs://."
        super().__init__(host=host, port=port)
        self.pyfs_url = pyfs_url
        self.threaded = threaded

    async def create_shell(self, username):
        return PyfsFtpShell(self.pyfs_url, threaded=self.threaded)
