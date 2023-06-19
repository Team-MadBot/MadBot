import discord

from discord import ui
from typing import List, Any, Optional
from tools.models import GuildItem

def paginate(data: list, per_page: int = 10) -> List[List[Any]]:
    pages = []
    for count, page in enumerate(data):
        if count % per_page == 0:
            pages.append([page])
        else:
            pages[count // per_page].append(page)

    return pages

def shop_paginate(pages: List[List[GuildItem]]) -> List[str]:
    formatted_pages: List[str] = ["" for _ in pages]
    
    for count, page in enumerate(pages):
        for i, item in enumerate(page, start=0):
            req_role = f"<@&{item.req_role}>" if item.req_role is not None else "Отсутствует"
            formatted_pages[count] += (
                f"{count * 10 + (i+1)}\\. **{item.name} - ${item.cost:,}**\n"
                f"{item.description}\n**Необходимая роль для покупки:** {req_role}\n"
            )
    
    return formatted_pages

class NavView(ui.View):
    def __init__(self, title: str, pages: List[str]):
        super().__init__(timeout=180)
        self.pages = pages
        self.title = title
        self.pages_len = len(self.pages)
        self.curr_page = 0
    
    async def edit_page(self, interaction: discord.Interaction, button: ui.Button):
        assert button.view is not None
        view: NavView = button.view
        view.page_select.label = str(self.curr_page + 1)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=self.title,
                color=discord.Color.orange(),
                description=self.pages[self.curr_page]
            ),
            view=view
        )
    
    @ui.button(label="<<")
    async def page_begin(self, interaction: discord.Interaction, button: ui.Button):
        self.curr_page = 0
        await self.edit_page(interaction, button)
    
    @ui.button(label="<")
    async def page_prev(self, interaction: discord.Interaction, button: ui.Button):
        self.curr_page = self.curr_page - 1 if self.curr_page != 0 else 1
        await self.edit_page(interaction, button)

    @ui.button(label="1")
    async def page_select(self, interaction: discord.Interaction, button: ui.Button):
        pass

    @ui.button(label=">")
    async def page_next(self, interaction: discord.Interaction, button: ui.Button):
        self.curr_page = self.curr_page + 1 if self.curr_page + 1 != self.pages_len else self.pages_len - 1
        await self.edit_page(interaction, button)

    @ui.button(label=">>")
    async def page_end(self, interaction: discord.Interaction, button: ui.Button):
        self.curr_page = self.pages_len - 1
        await self.edit_page(interaction, button)
    