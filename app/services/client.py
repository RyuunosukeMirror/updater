import asyncio
import enum
import inspect
import logging
import typing
import aiohttp
import time
import state


class Backoff:
    def __init__(self, base: int = 1, ceil: int = 10):
        self._exp = 0
        self._base = base
        self._max = ceil

        # self._rand = random.Random()
        # self._rand.seed()

    @property
    def delay(self) -> float:
        self._exp = max(self._exp + 1, self._max)
        return self._base * 2 ** self._exp

    def reset(self):
        self._exp = 0

    def sleep(self) -> tuple[float, typing.Awaitable]:
        return self.delay, asyncio.sleep(self.delay)


class ShowerLimiter:
    """
    A ratelimiter solution that I figured out in the shower.
    """

    def __init__(self, bucket: int, refill: int = 60, *, conns: int = 20):
        self.bucket = bucket
        self.refill = refill
        self.conns = asyncio.Semaphore(conns)
        self.edge = 0

    @property
    def every(self):
        return self.refill / self.bucket

    @staticmethod
    async def _wait(aws: typing.Awaitable, wait: float):
        await asyncio.sleep(wait)
        await aws

    def limit(self, aws: typing.Awaitable) -> typing.Coroutine:
        called = time.perf_counter_ns() / (10 ** 9)
        self.edge += self.every

        if called > self.edge:
            self.edge = called

        return self._wait(aws, self.edge - called)


_Callback = typing.Callable[[aiohttp.ClientResponse], typing.Awaitable]
_Future = "asyncio.Future[aiohttp.ClientResponse]"


class Base(str, enum.Enum):
    API = "https://beatsaver.com/api"
    CDN = f"https://{state.config.REGION}.cdn.beatsaver.com"
    TEST = "http://localhost:8888"


class Route:
    buckets = {
        Base.API: ShowerLimiter(1000),
        Base.CDN: ShowerLimiter(10000, 1, conns=50),  # apparently not ratelimited
    }

    def __init__(
        self,
        base: "Base",
        path: str,
        method: str = "GET",
        *,
        vars: dict = None,
        params: dict = None,
        limiter: "ShowerLimiter" = None,
    ):
        assert path[0] == "/"

        self.method = method
        self.params = params
        self.base = base

        url = base + path
        if vars:
            url = url.format_map(vars)
        self.url = url

        self.limiter = limiter or self.buckets[base]


class HTTPClient:
    RETRY_COUNT = 5

    def __init__(self, client: aiohttp.ClientSession):
        self._client = client
        self.loop = asyncio.get_running_loop()  # init client in an async context
        self.tasks: set[asyncio.Task] = set()

    def request(
        self, route: Route, callback: _Callback = None, *args, **kwargs
    ) -> typing.Optional[_Future]:
        fut = self.loop.create_future()

        task = self.loop.create_task(
            route.limiter.limit(self._request(route, fut, callback, *args, **kwargs))
        )
        self.tasks.add(task)

        if callback:
            return fut

    async def _request(self, route: Route, fut: _Future, callback: _Callback, *args, **kwargs):
        backoff = Backoff()
        resp = None

        for _ in range(self.RETRY_COUNT):
            try:
                async with route.limiter.conns, self._client.request(
                    method=route.method,
                    url=route.url,
                    params=route.params,
                    verify_ssl=False,  # beatsaver's ssl be crazy
                    timeout=10,
                ) as resp:
                    if resp.status == 404:
                        return fut.set_result(None)
                    
                    if resp.status != 200:
                        delay, sleep = backoff.sleep()
                        print(f"got {resp.status}, trying again in {delay}")
                        await sleep
                        continue

                    self.tasks.remove(asyncio.current_task(loop=self.loop))
                    fut.set_result(resp)

                    if callback:
                        await callback(resp, *args, **kwargs)

                    break

            except asyncio.TimeoutError:
                print("client timeout error")
                return
        else:
            print("client failed to complete request")
            fut.set_exception(asyncio.TimeoutError())

    async def close(self, force=False):
        if force:
            [task.cancel("force close") for task in self.tasks]
        else:
            await asyncio.gather(*self.tasks)
