import os

from discord import Intents, Color
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()

cogs = (
    "jishaku",
    "events.launch",
    "events.errors",
    "events.on_interaction",
    "modules.moderation.kick",
    "modules.moderation.ban",
    "modules.moderation.timeout",
    "modules.moderation.untimeout",
    "modules.moderation.unban",
    "modules.moderation.clear",
    "modules.moderation.warn",
    "modules.economy.profile",
    "modules.economy.add_money",
    "modules.economy.remove_money"
)

class Settings(TypedDict):
    token: str | None
    nc_token: str | None
    sdc_token: str | None
    prefix: str
    owner_id: int
    intents: Intents
    bot_id: int
    shard_count: int
    log_channel: int
    color: Color
    support_invite: str

settings: Settings = {
    "token": os.environ.get("TOKEN"),
    "nc_token": os.environ.get("NC_TOKEN"),
    "sdc_token": os.environ.get("SDC_TOKEN"),
    "prefix": "$",
    "owner_id": 560529834325966858,
    "bot_id": 977280463792115833,
    "intents": Intents.default(),
    "shard_count": 1,
    "log_channel": 924241555697594380,
    "color": Color.orange(),
    "support_invite": "https://discord.gg/DvYPRm939R"
}

coders = [
    settings["owner_id"],
]

used_commands = 0
last_command = "Команды ещё не использовались"