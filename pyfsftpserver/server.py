import argparse
import asyncio
import logging

from pyfsftpserver import PyfsFtpServer
from pyfsftpserver.base.server import DEFAULT_HOST, DEFAULT_PORT, print_listening_message

logger = logging.getLogger(__name__)


def main(args=None):
    logging.basicConfig(level=logging.INFO)
    if args is None:
        # argparse does not work well with a running event loop, because it calls sys.exit
        # so we invoke it before the event loop
        args = parse_args()
    asyncio.run(serve(args))


def make_argparser():
    parser = argparse.ArgumentParser("pyfsftpserver")
    parser.add_argument("url", nargs='?', help="Pyfs url to be served over ftp", default="osfs://.")
    parser.add_argument("-H", "--host", help="Sets listening host", default=DEFAULT_HOST)
    parser.add_argument("-p", "--port", help="Sets listening port", default=DEFAULT_PORT, type=int)
    parser.add_argument(
        "-t", "--threaded", type=str2bool, default=True,
        help="Offload pyfs invocations to a thread per shell [yes, 1, no 0]"
    )
    return parser


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_args():
    return make_argparser().parse_args()


async def serve(args):
    server = PyfsFtpServer(
        host=args.host,
        port=args.port,
        pyfs_url=args.url,
        threaded=args.threaded,
    )
    await run_server(server)


async def run_server(server):
    await server.run(on_before_listening=print_listening_message)


if __name__ == "__main__":
    main()
