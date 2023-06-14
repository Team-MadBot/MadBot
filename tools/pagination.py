from typing import List, Any
from tools.models import GuildItem

def paginate(data: list, per_page: int = 10) -> List[List[Any]]:
    pages_num = len(data) // per_page + 1
    pages = [[]] * pages_num
    for count, page in enumerate(data):
        pages[count // per_page].append(page)
    
    return pages

def shop_paginate(pages: List[List[GuildItem]]) -> List[str]:
    formatted_pages: List[str] = ["" for _ in pages]
    
    for count, page in enumerate(pages):
        for i, item in enumerate(page, start=1):
            req_role = f"<@&{item.req_role}>" if item.req_role is not None else "Отсутствует"
            formatted_pages[count] += (
                f"{i*(count+1)}\. **{item.name} - ${item.cost:,}**\n"
                f"{item.description}\n**Необходимая роль для покупки:** {req_role}\n"
            )
    
    return formatted_pages
