from . import mongo_db

def add_user(
    *,
    user_id: int,
    enabled: bool = False,
    next_bump: int = 0,
    reminded: bool = False,
    up_count: int = 0
):
    mongo_db.reminder.insert_one(
        {
            "user_id": str(user_id),
            "enabled": enabled,
            "next_bump": next_bump,
            "reminded": reminded,
            "up_count": up_count
        }
    )

def get_user(user_id: int):
    return mongo_db.reminder.find_one({"user_id": str(user_id)})

def get_users(**kwargs):
    return list(mongo_db.reminder.find(kwargs))

def increment_user(
    user_id: int,
    **kwargs
):
    mongo_db.reminder.update_one(
        {"user_id": str(user_id)},
        {
            "$inc": kwargs
        }
    )

def update_user(
    user_id: int,
    **kwargs
):
    mongo_db.reminder.update_one(
        {"user_id": str(user_id)},
        {
            "$set": kwargs
        }
    )
