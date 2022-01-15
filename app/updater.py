import aiohttp
import asyncio
from . import state
from app.client import Ratelimit
from app.websocket import WebsocketHandler

async def setup():
    client = aiohttp.ClientSession(headers={
        "User-Agent" : "ryuunosuke.moe/1.0.0 (we made a fucking mirror)"
    })

    state.WS_HANDLER = WebsocketHandler(client=client)

async def run():
    async with Ratelimit():
        pass

    await asyncio.gather(
        state.WS_HANDLER.run(),
    )