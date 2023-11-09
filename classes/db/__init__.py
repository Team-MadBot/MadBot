import pymongo

client = pymongo.MongoClient()
db = client.madbot

from . import blacklist
from . import marries
from . import premium
from . import autorole
from . import shutted_cmds
from . import vote
