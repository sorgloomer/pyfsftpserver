from ..base.server import FtpServer

from .shell import PyfsFtpShell


class PyfsFtpServer(FtpServer):
    def __init__(self, pyfs_url=None, host=None, port=None, threaded=None):
        if pyfs_url is None:
            pyfs_url = "osfs://."
        super().__init__(host=host, port=port)
        self.pyfs_url = pyfs_url
        self.threaded = threaded

    async def shell_factory(self, username):
        return PyfsFtpShell(self.pyfs_url, threaded=self.threaded)
