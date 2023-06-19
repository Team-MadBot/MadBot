from . import database
from tools import models

def add_guild_item(item: models.GuildItem) -> bool:
    """
    Добавляет предмет в магазин сервера.

    Параметры:
    item (models.GuildItem): Объект предмета сервера. Содержит:
    - guild_id (int): ID сервера
    - name (str): Название предмета
    - cost (int): Цена предмета
    - description (str): Описание предмета
    - req_role (Optional[int]): Необходимая роль для покупки предмета

    Функциональность:
    - Проверяет, есть ли запись о сервере в базе данных. Если нет, создает новую запись.
    - Добавляет предмет в список предметов сервера.
    - Возвращает True в случае успеха, иначе False.
    """
    coll = database.guild
    guild_id = item.guild_id
    name = item.name
    cost = item.cost
    description = item.description
    req_role = item.req_role
    if req_role is not None: req_role = str(req_role)

    guild = coll.find_one({'guild_id': str(guild_id)})
    if guild is None:
        coll.insert_one(
            {
                'guild_id': str(guild_id),
                'members': [],
                'autoroles': [],
                'buttonroles': [],
                'items': [
                    {
                        'name': name,
                        'cost': cost,
                        'description': description,
                        'req_role': req_role
                    }
                ]
                
            }
        )
        return True
    
    coll.update_one(
        {'guild_id': str(guild_id)},
        {
            '$push': {
                "items": {
                    'name': name,
                    'cost': cost,
                    'description': description,
                    'req_role': req_role
                }
            }
        }
    )
    return True