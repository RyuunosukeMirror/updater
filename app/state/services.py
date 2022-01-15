import typing
import config

if typing.TYPE_CHECKING:
    import app.websocket
    import motor.motor_asyncio

__slots__ = (
    "WS_HANDLER",
    "DB"
)

WS_HANDLER: app.websocket.WebsocketHandler
DB: motor.motor_asyncio.MotorClient(config.DATABASE)