import asyncio
from concurrent.futures.thread import ThreadPoolExecutor


class AioExecutor:
    @staticmethod
    async def run(fn):
        return fn()

    def close(self):
        pass


AIO_EXECUTOR = AioExecutor()


class ThreadedExecutor(AioExecutor):
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def run(self, fn):
        return await asyncio.get_running_loop().run_in_executor(self._executor, fn)

    def close(self):
        self._executor.shutdown(True)


def create(threaded):
    return ThreadedExecutor() if threaded else AIO_EXECUTOR
