import asyncio
import enum
import inspect
import logging
import typing
import aiohttp
import time
import app.state as state


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

    async def sleep(self) -> (float, typing.Awaitable):
        return self.delay, asyncio.sleep(self.delay)


class ShowerLimiter:
    def __init__(self, bucket: int, refill: int = 60):
        self.bucket = bucket
        self.refill = refill
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


_Callback: typing.TypeAlias = typing.Callable[[aiohttp.ClientResponse], typing.Awaitable]
_Future = "asyncio.Future[aiohttp.ClientResponse]"


class Base(str, enum.Enum):
    API = "https://beatsaver.com/api"
    CDN = f"https://{state.config.REGION}.cdn.beatsaver.com"
    TEST = "http://localhost:8080"


class Route:
    def __init__(
            self,
            base: "Base",
            path: str,
            method: str = "GET",
            *,
            vars: dict = None,
            params: dict = None,
    ):
        assert path[0] == "/"

        self.method = method
        self.params = params
        self.base = base

        url = base + path
        if vars: url = url.format_map(vars)
        self.url = url


class HTTPClient:
    RETRY_COUNT = 5

    def __init__(self, client: aiohttp.ClientSession):
        self._client = client
        self.loop = asyncio.get_running_loop()  # init client in an async context

        self.buckets = {
            Base.API: ShowerLimiter(1000),
            Base.CDN: ShowerLimiter(10000, 1)  # apparently not ratelimited
        }

    def request(
            self, route: Route, callback: _Callback = None
    ) -> _Future:
        fut = self.loop.create_future()

        self.loop.create_task(
            self.buckets[route.base].limit(
                self._request(route, fut, callback)
            )
        )

        return fut

    async def _request(
            self, route: Route, fut: _Future, callback: _Callback
    ):
        backoff = Backoff()
        resp = None

        # todo log retry number
        for retry in range(self.RETRY_COUNT):
            resp = await self._client.request(
                method=route.method,
                url=route.url,
                params=route.params,
                verify_ssl=False,  # beatsaver's ssl be crazy
            )

            if resp.status != 200:
                delay, sleep = backoff.sleep()
                logging.debug(f"got {resp.status}, trying again in {delay}")
                await sleep
                continue

        fut.set_result(resp)

        if callback:
            await callback(resp)
