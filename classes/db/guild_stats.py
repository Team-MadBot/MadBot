from . import client as mongo_client

db = mongo_client.stats

def add_guild_stats(
    guild_id: int,
    next_update: int = 0,
    channels: list = []
):
    db.guilds.insert_one(
        {
            "id": str(guild_id),
            "next_update": next_update,
            "channels": channels
        }
    )

def get_guilds_stats():
    return list(db.guilds.find())

def get_guild_stats(
    guild_id: int,
    **kwargs
):
    return db.guilds.find_one(
        {
            "id": str(guild_id)
        },
        kwargs
    )

def update_guild_stats(
    guild_id: int,
    **kwargs
):
    db.guilds.update_one(
        {
            'id': str(guild_id)
        },
        {
            "$set": kwargs
        }
    )

def delete_guild_stats(
    guild_id: int
):
    db.guilds.delete_one(
        {
            'id': str(guild_id)
        }
    )