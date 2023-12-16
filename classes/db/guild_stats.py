from . import client as mongo_client
from motor import MotorCursor

db = mongo_client.stats

async def add_guild_stats(
    guild_id: int,
    next_update: int = 0,
    channels: list = []
):
    await db.guilds.insert_one(
        {
            "id": str(guild_id),
            "next_update": next_update,
            "channels": channels
        }
    )

def get_guilds_stats() -> MotorCursor:
    return db.guilds.find()

async def get_guild_stats(
    guild_id: int,
    **kwargs
):
    return await db.guilds.find_one(
        {
            "id": str(guild_id)
        },
        kwargs
    )

async def update_guild_stats(
    guild_id: int,
    **kwargs
):
    await db.guilds.update_one(
        {
            'id': str(guild_id)
        },
        {
            "$set": kwargs
        }
    )

async def delete_guild_stats(
    guild_id: int
):
    await db.guilds.delete_one(
        {
            'id': str(guild_id)
        }
    )