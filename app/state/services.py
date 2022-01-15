import typing
import config

from app.objects.websocket import WebsocketHandler
from motor.motor_asyncio import AsyncIOMotorClient

DB: AsyncIOMotorClient
WS_HANDLER: WebsocketHandler