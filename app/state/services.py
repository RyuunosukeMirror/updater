from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient
    from motor.core import Database
    from objects.websocket import WebsocketHandler # :>
    
DB_CLIENT: 'AsyncIOMotorClient'
DB: 'Database'
WS_HANDLER: 'WebsocketHandler'