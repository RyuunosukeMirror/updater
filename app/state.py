import motor.motor_asyncio

import app.services

try:
    import config
except ModuleNotFoundError:
    print("config.py must be present")

DB: motor.motor_asyncio.AsyncIOMotorClient
HTTP: app.services.HTTPClient
