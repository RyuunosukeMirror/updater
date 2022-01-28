from typing import TYPE_CHECKING

try:
    import config
except ModuleNotFoundError:
    print("config.py must be present")

if TYPE_CHECKING:
    from services import HTTPClient
    from pymongo.mongo_client import MongoClient
    from pymongo.database import Database

DB_CLIENT: "MongoClient"
DB: "Database"
HTTP: "HTTPClient"
