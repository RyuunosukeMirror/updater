from typing import Optional
from pprint import pprint
import aiohttp
import app.state
from app.utils import JSON
import orjson

from app.services.client import Route, Base


class Skip(Exception):
    pass


class WebsocketHandler:
    ENDPOINT = "wss://ws.beatsaver.com/maps"

    def __init__(self, client: aiohttp.ClientSession) -> None:
        self._client = client
        self.handlers = {
            "MAP_UPDATE": self.handle_map_update,
            "MAP_DELETE": self.handle_map_delete,
        }

    async def run(self):
        ws = await self._client.ws_connect(WebsocketHandler.ENDPOINT)

        while True:
            resp = await ws.receive_json(loads=orjson.loads)

            try:
                await self.handlers[resp["type"]](resp["msg"])
            except KeyError:
                pass

    async def handle_map_update(self, data: JSON):
        if data["automapper"]:
            return

        pprint(data)

    async def handle_map_delete(self, data: JSON):
        pprint(data)


async def shunt_api_response(resp: aiohttp.ClientResponse):
    pass


async def shunt_zip(resp: aiohttp.ClientResponse):
    pass


async def shunt_cover(resp: aiohttp.ClientResponse):
    pass


async def shunt_preview(resp: aiohttp.ClientResponse):
    pass


async def crawler(_start: str = "1", _end: Optional[str] = None):
    if not _end:
        _end = "ffffff"

    start = int(_start, 16)
    end = int(_end, 16)

    for map_id in range(start, end):
        app.state.HTTP.request(
            Route(Base.API, "/maps/id/{id}", vars={
                "id": format(map_id, "x")
            }), callback=shunt_api_response
        )
