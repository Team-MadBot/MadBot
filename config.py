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
    "modules.economy.remove_money",
    "modules.economy.add_item",
    "modules.economy.pay",
    "modules.economy.shop"
)

class Settings(TypedDict):
    token: str | None
    nc_token: str | None
    sdc_token: str | None
    prefix: str | None
    owner_id: int
    intents: Intents
    bot_id: int
    shard_count: int
    log_channel: int
    color: Color
    support_invite: str | None
    mongo_url: str | None

settings: Settings = {
    "token": os.environ.get("TOKEN"),
    "nc_token": os.environ.get("NC_TOKEN"),
    "sdc_token": os.environ.get("SDC_TOKEN"),
    "prefix": os.environ.get("PREFIX"),
    "owner_id": int(os.environ.get("OWNER_ID")),  # type: ignore
    "bot_id": int(os.environ.get("BOT_ID")),  # type: ignore
    "intents": Intents.default(), # type: ignore
    "shard_count": int(os.environ.get("SHARD_COUNT")), # type: ignore
    "log_channel": int(os.environ.get("LOG_CHANNEL_ID")), # type: ignore
    "color": Color.orange(),
    "support_invite": os.environ.get("SUPPORT_URL"),
    "mongo_url": os.environ.get("MONGODB_URL")
}

coders = [
    settings["owner_id"],
]

used_commands = 0
last_command = "Команды ещё не использовались"