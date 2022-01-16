import enum
from typing import Callable, Awaitable, TYPE_CHECKING, Optional, overload

if TYPE_CHECKING:
    import aiohttp


class Cooldown:
    def __init__(self):
        pass


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
        assert self.is_cdn and "_region" not in pathvars

        url = base + path
        if pathvars:
            url = url.format_map(pathvars)

        self.url = url
        self.params = params


class Client:
    RETRY_COUNT = 5

    def __init__(self, client):
        self._client = client
        # self.loop =

        # really depends on where updater is being run
        # usually gonna be na but sometime not
        # interprets region from various requests
        self.region: str = "na"
        self.buckets = {
            Base.API: ...,
            Base.CDN: ...,
        }

    def request(self, route: Route, callback: Callback): ...

    async def _request(self, route: Route, callback: Callback):
        for retry in range(self.RETRY_COUNT):
            ...
            # todo log retry number
