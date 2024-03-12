import motor.motor_asyncio

from config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings['mongo_url']) # type: ignore
mongo_db = client['madbot' + ('test' if settings['debug_mode'] else '') + settings['db_suffix']] # type: ignore

from .blacklist import *
from .marries import *
from .premium import *
from .autorole import *
from .shutted_cmds import *
from .bot_stats import *
from .reminder import *
from .guild_stats import *
from .debug import *
