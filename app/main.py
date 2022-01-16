import asyncio
import state
import motor.motor_asyncio
from services import Route, Base

async def setup():
    state.DB = motor.motor_asyncio.AsyncIOMotorClient(
        state.config.MONGO_DSN
    )[state.config.DB_NAME]


async def main():
    await setup()
    print(await state.DB.beatmaps.find_one({"id": "1"}))

    r = Route(Base.CDN, "/doodoo/{yea}", pathvars={
        "_region": "bar"
    }, params={
        "_region": "bar"
    })

    print(r.url)



if __name__ == '__main__':
    asyncio.run(main())
