import asyncio
import re
import config
import motor.motor_asyncio
import aiohttp
from app.objects import client
from app.objects import websocket
from app.state import services

async def setup():
    client = aiohttp.ClientSession(headers={
        "User-Agent" : "ryuunosuke.moe/1.0.0 (we made a fucking mirror)"
    })
    
    # Initialize the client
    services.WS_HANDLER = websocket.WebsocketHandler(client=client)
    services.DB_CLIENT = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_DSN)
    services.DB = services.DB_CLIENT[config.DATABASE]

async def main():
    print(""" ______                                                   _             _ 
(_____ \                                                 | |           | |
 _____) ) _   _  _   _  _   _  ____    ___    ___  _   _ | |  _  _____ | |
|  __  / | | | || | | || | | ||  _ \  / _ \  /___)| | | || |_/ )| ___ ||_|
| |  \ \ | |_| || |_| || |_| || | | || |_| ||___ || |_| ||  _ ( | ____| _ 
|_|   |_| \__  ||____/ |____/ |_| |_| \___/ (___/ |____/ |_| \_)|_____)|_|
         (____/ > Updater v1.0.0 | Copyright (c) 2021- |
""") 

    await setup()
    await services.WS_HANDLER.run()

asyncio.run(main())