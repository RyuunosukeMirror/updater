from asyncio.log import logger
from pprint import pprint
from time import sleep
from typing import Optional

import aiohttp
import orjson
import state
from utils import JSON

from pathlib import Path
from aiofiles import open as aioopen
from services.client import Base, Route
from services.parser import parse_beatmap_metadata


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
    j = await resp.json()
    parsed = parse_beatmap_metadata(j)
    state.DB.beatmaps.find_one_and_replace({"id": parsed["id"]}, parsed, upsert=True)

    for version in parsed["versions"]:
        for asset_type in [f"{version['hash']}.zip", "preview.mp3", "cover.jpg"]:
            if Path(f"{state.config.BEATMAP_PATH}/{version['hash']}/{asset_type}").exists():
                continue
                
            Path(f"{state.config.BEATMAP_PATH}/{parsed['id']}/{version['hash']}").mkdir(parents=True, exist_ok=True)
            
            await state.HTTP.request(
                Route(Base.CDN, "/" + version["hash"] + asset_type),
                params={
                    "save_path": f"{state.config.BEATMAP_PATH}/{parsed['id']}/{version['hash']}/{asset_type}"
                },
                callback=shunt_download_response,
            )


async def shunt_download_response(resp: aiohttp.ClientResponse, params: dict):
    async with aioopen(params["save_path"], "wb") as f:
        await f.write(await resp.read())


async def crawler(_start: str = "1", _end: Optional[str] = "ffffff"):
    print("Crawling beatmaps...")
    start = int(_start, 16)
    end = int(_end, 16)

    for map_id in range(start, end):
        print(f"Crawling {map_id}... ({map_id}/{end})")
        await state.HTTP.request(
            Route(Base.API, "/maps/id/{id}", vars={"id": format(map_id, "x")}),
            callback=shunt_api_response,
        )
