import pymongo

client = pymongo.MongoClient()
mongo_db = client.madbot

from .blacklist import *
from .marries import *
from .premium import *
from .autorole import *
from .shutted_cmds import *
from .bot_stats import *
