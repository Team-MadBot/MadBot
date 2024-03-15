from . import mongo_db


async def add_user(
    *,
    user_id: int,
    enabled: bool = False,
    next_bump: int = 0,
    reminded: bool = False,
    up_count: int = 0
):
    await mongo_db.reminder.insert_one(
        {
            "user_id": str(user_id),
            "enabled": enabled,
            "next_bump": next_bump,
            "reminded": reminded,
            "up_count": up_count,
        }
    )


async def get_user(user_id: int):
    return await mongo_db.reminder.find_one({"user_id": str(user_id)})


def get_users(**kwargs):
    return mongo_db.reminder.find(kwargs)


async def increment_user(user_id: int, **kwargs):
    await mongo_db.reminder.update_one({"user_id": str(user_id)}, {"$inc": kwargs})


async def update_user(user_id: int, **kwargs):
    await mongo_db.reminder.update_one({"user_id": str(user_id)}, {"$set": kwargs})
