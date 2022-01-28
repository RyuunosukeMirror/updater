import asyncio

import aiohttp
from pymongo.mongo_client import MongoClient

import state
from services import Base, HTTPClient, Route, ShowerLimiter
from services.handler import crawler

async def main():
    state.DB = MongoClient(state.config.MONGO_DSN).get_database(state.config.DB_NAME)
    
    client = aiohttp.ClientSession(
        headers={"User-Agent": "ryuunosuke.moe/0.0.0 (https://ryuunosuke.moe)"},
        connector=aiohttp.TCPConnector(limit=0, ttl_dns_cache=1200, force_close=True),
    )

    state.HTTP = HTTPClient(client=client)

    await crawler("1500")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        pass
