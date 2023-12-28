import motor.motor_asyncio

from config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings['mongo_url']) # type: ignore
mongo_db = client.madbottest if settings['debug_mode'] else client.madbot # type: ignore

from .blacklist import *
from .marries import *
from .premium import *
from .autorole import *
from .shutted_cmds import *
from .bot_stats import *
from .reminder import *
from .guild_stats import *
from .debug import *
