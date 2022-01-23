from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import app.services
    import motor.motor_asyncio

try:
    import config
except ModuleNotFoundError:
    print("config.py must be present")

DB: "motor.motor_asyncio.AsyncIOMotorClient"
HTTP: "app.services.HTTPClient"
