import motor.motor_asyncio
import argparse

from config import settings

parser = argparse.ArgumentParser()
parser.add_argument(
    "--debug-mode", "--debug", "-d",
    help="Should bot run with logging.DEBUG level?",
    action="store_true",
    default=False,
    dest="debug_mode"
)
parser.add_argument(
    "--migrate-db", "--migrate",
    help="Should bot migrate DB before startup?",
    action="store_true",
    default=False,
    dest="migrate_db"
)
parser.add_argument(
    "--db-suffix", "--db",
    help="Adds suffix for DB name in MongoDB.",
    type=str,
    default="",
    dest="db_suffix"
)
args = parser.parse_args()
settings['debug_mode'] = args.debug_mode
settings['db_suffix'] = args.db_suffix

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
