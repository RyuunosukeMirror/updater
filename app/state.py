import motor.motor_asyncio
try:
    import config
except ModuleNotFoundError:
    print("config.py must be present")

DB: motor.motor_asyncio.AsyncIOMotorClient
# CLIENT: "TBD"

