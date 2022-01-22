from pprint import pprint
import aiohttp
from app.utils import JSON
import orjson


class Skip(Exception):
    pass


class WebsocketHandler:
    ENDPOINT = "wss://ws.beatsaver.com/maps"

    def init(self, client: aiohttp.ClientSession) -> None:
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
