import asyncio
import pprint

import aiohttp

import app.services
import state
import motor.motor_asyncio
from services import Route, Base, ShowerLimiter


async def _parse_latest(resp):
    print(resp)


async def main():
    state.DB = motor.motor_asyncio.AsyncIOMotorClient(state.config.MONGO_DSN)[
        state.config.DB_NAME
    ]

    client = aiohttp.ClientSession(
        headers={"User-Agent": "ryuunosuke.moe/0.0.0"},
        connector=aiohttp.TCPConnector(limit=0, ttl_dns_cache=1200, force_close=True),
    )

    state.HTTP = app.services.HTTPClient(client=client)

    l = ShowerLimiter(1200, conns=300)
    for i in range(5000):
        state.HTTP.request(
            Route(Base.CDN, "/17b224cbc23de8abcbde852bd9a2beba50d208bf.zip"),
            callback=_parse_latest,
        )

    await state.HTTP.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        pass
