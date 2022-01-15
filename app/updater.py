import aiohttp
import asyncio
import app.state
from app.objects.client import Ratelimit
from app.objects.websocket import WebsocketHandler
import config

import motor.motor_asyncio

async def setup():
    client = aiohttp.ClientSession(headers={
        "User-Agent" : "ryuunosuke.moe/1.0.0 (we made a fucking mirror)"
    })
    
    app.state.services.DB = motor.motor_asyncio.AsyncIOMotorClient(
        config.MONGODB_DSN
    )[config.DATABASE]

    app.state.services.WS_HANDLER = WebsocketHandler(client=client)

async def run():
    resp = await app.state.services.DB.find_one({
        'id' : "1"
    })
    print(resp)
    await asyncio.gather(
        app.state.WS_HANDLER.run(),
    )