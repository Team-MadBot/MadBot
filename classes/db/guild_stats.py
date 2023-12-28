from . import client as mongo_client  # type: ignore

db = mongo_client.stats  # type: ignore

async def add_guild_stats(
    guild_id: int,
    next_update: int = 0,
    channels: list[dict[str, str]] | None = None
):
    await db.guilds.insert_one(  # type: ignore
        {
            "id": str(guild_id),
            "next_update": next_update,
            "channels": channels or []
        }
    )

def get_guilds_stats():
    return db.guilds.find()  # type: ignore

async def get_guild_stats(  # type: ignore
    guild_id: int,
    **kwargs  # type: ignore
):
    return await db.guilds.find_one(  # type: ignore
        {
            "id": str(guild_id)
        },
        kwargs
    )

async def update_guild_stats(
    guild_id: int,
    **kwargs  # type: ignore
):
    await db.guilds.update_one(  # type: ignore
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
    await db.guilds.delete_one(  # type: ignore
        {
            'id': str(guild_id)
        }
    )
