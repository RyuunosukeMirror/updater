import asyncio
import inspect
from dataclasses import dataclass
from typing import Callable, Optional

import aiohttp

"""
self.ratelimiter = Ratelimit(60, 100)

average time a request takes (under a domain)

cdn.beatsaver.com -> 600ms
beatsaver.com -> 200ms

r = 60 / 100 * 1000 = 600ms
1 worker
   |     |     |     |     |
|     |     |     |     |
|  |  |  |  |  |  |  |  |

len(queue)


200 / r = 0.3333 remai
+ 400 ms


with self.BUCKETS["cdn.beatsaver.com"]:
    do shit

"""


class Ratelimit:
    def __init__(self, reset: float = 60, bucket: int = 1000):
        self.average: float = 0.0
        self.timers = {}


    async def __aenter__(self):
        print("entered")

    async def __aexit__(self, *args):
        print("exit", *args)



@dataclass
class Task:
    request: aiohttp.ClientRequest
    callback: Optional[Callable]

class HTTPClient:
    """
    A well intentioned http client for high request throughput. Massive parellelization via workers, and callback code
    to help with data parsin'
    
    
    WIP
    """

    BUCKETS = {
        "cdn.beatsaver.com": Ratelimit(),
        "beatsaver.com": Ratelimit()
    }

    def __init__(self) -> None:
        self._loop = asyncio.get_event_loop()
        self._queue: asyncio.Queue["Task"] = asyncio.Queue()
        self._workers: list[asyncio.Task] = None
        self.threshold = 0
        self.__client: aiohttp.ClientSession = None

    @classmethod
    async def spawn(cls, num: int = 1) -> "HTTPClient":
        ret = cls()
        ret.__client = aiohttp.ClientSession()
        ret.threshold = num
        ret._spawn_workers(num)
        return ret

    async def close(self, force=False):
        if not force:
            await self._queue.join()

        for worker in self._workers:
            worker.cancel()
        await self.__client.close()

    async def do(self, method, url, *, callback=None, **kwargs) -> Optional[aiohttp.ClientResponse]:
        kwargs |= {
            "method": method,
            "url": url
        }

        if callback and not inspect.iscoroutinefunction(callback):
            raise TypeError("callback must be an async function")

        await self._queue.put(
            Task(
                request=kwargs,
                callback=callback
            )
        )

    def _spawn_workers(self, num: int): self._workers = [self._loop.create_task(self._worker()) for _ in range(num)]

    # TODO lol what is this
    async def _worker(self):
        while True:
            task = await self._queue.get()
            resp: aiohttp.ClientResponse = None
            try:
                resp: aiohttp.ClientResponse = await self.__client.request(**task.request)
            except Exception as e: 
                print("oops:", e)
                continue

            if resp.status == 200:
                # await task.callback(resp)
                if task.callback:
                    self._loop.create_task(task.callback(resp))
            else:
                print("FAILED", resp.status, resp.headers)
                await self._queue.put(task)

            self._queue.task_done()