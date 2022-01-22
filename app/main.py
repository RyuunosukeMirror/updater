import asyncio
import pprint

import aiohttp

import app.services
import state
import motor.motor_asyncio
from services import Route, Base


async def _parse_latest(resp):
    print(resp)


async def main():
    state.DB = motor.motor_asyncio.AsyncIOMotorClient(state.config.MONGO_DSN)[
        state.config.DB_NAME
    ]

    client = aiohttp.ClientSession(headers={"User-Agent": "ryuunosuke.moe/0.0.0"})

    state.HTTP = app.services.HTTPClient(client=client)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        pass
