"""
This is database callback code. You can see the structure of collections:

1. Blacklist:
{
    'user_id': str,
    'blocked_at': int,
    'reason': str,
    'blocked_at': Optional[str]
}

2. GuildMemberAction:
{
    'type': int,
    ...and other stuff for specific action
}

3. GuildItem:
{
    'id': int,
    'name': str,
    'cost': int,
    'description': str,
    'req_role': Optional[str]
}

4. GuildMember:
{
    'user_id': str,
    'balance': int,
    'level': int,
    'xp': int,
    'actions': List[GuildMemberAction]
    'inventory': List[GuildItem]
}

5. ButtonRole:
{
    'channel_id': str,
    'message_id': str,
    'type': str in ("single", "multiple")
    'roles': List[str]
}

6. Guild:
{
    'guild_id': str,
    'members': List[GuildMember],
    'autoroles': List[str],
    'buttonroles': List[ButtonRole],
    'items': List[GuildItem]
}
"""
from pymongo import MongoClient
from config import settings

client = MongoClient() if settings['mongo_url'] is None else MongoClient(settings['mongo_url'])
database = client.madbotv2

from .blacklist import *
from .guild_item import *
from .guild_user import *
from .guild import *
