import asyncio
import enum
import functools
import inspect
import logging
import random
from typing import Callable, Awaitable, TYPE_CHECKING, Optional, overload
import aiohttp


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

    async def sleep(self):
        await asyncio.sleep(self.delay)


Callback = Callable[[aiohttp.ClientResponse], Awaitable]


class Base(str, enum.Enum):
    API = "https://beatsaver.com/api"
    CDN = "https://{_region}.cdn.beatsaver.com"


class Route:
    def __init__(self, base: "Base",
                 path: str,
                 method: str = "GET", *,
                 pathvars: dict = None,
                 params: dict = None):
        assert path[0] == "/"

        self.method = method
        self.is_cdn = Base == Base.CDN
        if self.is_cdn and "_region" not in pathvars:
            raise ValueError("cannot use _region in a CDN base")

        url = base + path
        if pathvars:
            url = url.format_map(pathvars)

        self.url = url
        self.params = params


class HTTPClient:
    RETRY_COUNT = 5

    def __init__(self, client: aiohttp.ClientSession):
        self._client = client
        self.loop = asyncio.get_running_loop()  # init client in an async context

        # really depends on where updater is being run
        # usually gonna be na but sometime not
        # interprets region from various requests
        self.region: str = "na"
        self.buckets = {
            Base.API: ...,
            Base.CDN: ...,
        }



    def request(self, route: Route, callback: Callback = None) -> "asyncio.Future[aiohttp.ClientResponse]":
        fut = self.loop.create_future()

        # lul what
        if callback and inspect.isawaitable(callback):
            fut.add_done_callback(
                lambda f: self.loop.create_task(
                    callback(f.result())
                )
            )

        self.loop.create_task(self._request(route, fut))

        return fut

    async def _request(self, route: Route, fut: "asyncio.Future[aiohttp.ClientResponse]"):
        backoff = Backoff()

        # todo log retry number
        for retry in range(self.RETRY_COUNT):
            # todo might become self.region + "." + url
            if route.is_cdn:
                route.url = route.url.format(_region=self.region)

            resp = await self._client.request(
                method=route.method,
                url=route.url,
                params=route.params,
                verify_ssl=False  # beatsaver's ssl be crazy
            )

            status = resp.status
            if 500 < status < 600:
                logging.debug(f"got {status}, will try again later")
                await backoff.sleep()
                continue
            elif 400 < status < 500:
                logging.debug(f"got {status}, trying again")
                break

            fut.set_result(resp)
            break
