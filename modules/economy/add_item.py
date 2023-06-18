from typing import Any, Optional
import discord

from discord.ext import commands
from discord import app_commands
from discord import ui
from tools import models, db

class AddItemRoleSelect(ui.RoleSelect):
    def __init__(self, item: models.GuildItem):
        super().__init__(
            placeholder="Выберите необходимую роль для покупки", 
            min_values=1, 
            max_values=1,
            row=0
        )
        self.item = item
    
    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        self.item.req_role = role.id
        db.add_guild_item(self.item)
        embed = discord.Embed(
            title="Добавление предмета - Успешно!",
            color=discord.Color.green(),
            description=f"Предмет **{self.item.name}** добавлен!"
        ).set_footer(
            text=str(interaction.user),
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(embed=embed)
        self.view.stop() # type: ignore

class AddItemRoleSelectView(ui.View):
    def __init__(self, item: models.GuildItem):
        super().__init__(timeout=120)
        self.item = item
        self.add_item(AddItemRoleSelect(item=item))
    
    @ui.button(label="Пропустить", style=discord.ButtonStyle.blurple, row=1)
    async def skip_role(self, interaction: discord.Interaction, button: ui.Button):
        item = self.item
        item.req_role = None
        db.add_guild_item(item)
        embed = discord.Embed(
            title="Добавление предмета - Успешно!",
            color=discord.Color.green(),
            description=f"Предмет **{item.name}** добавлен!"
        ).set_footer(
            text=str(interaction.user),
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(embed=embed)
        self.stop()

class AddItemModal(ui.Modal, title="Добавление предмета"):
    name = ui.TextInput(
        label="Название предмета",
        placeholder="Котяра",
        min_length=1,
        max_length=50
    )
    cost = ui.TextInput(
        label="Стоимость",
        placeholder="9999999",
        max_length=10
    )
    description = ui.TextInput(
        label="Описание предмета",
        placeholder="Очень классный котяра. Раритет.",
        style=discord.TextStyle.long,
        min_length=10,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value

        try:
            cost = int(self.cost.value)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Стоимость предмета должна быть числом."
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if cost <= 0: # type: ignore
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Стоимость не может быть нулевой или отрицательной."
            ).set_image(url="https://http.cat/400")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        description = self.description.value

        item = models.GuildItem(
            id=None,
            guild_id=interaction.guild.id, # type: ignore
            name=name,
            cost=cost, # type: ignore
            description=description,
            req_role=None
        )

        await interaction.response.send_message(
            "Хорошо, теперь выберите роль, которая необходима для покупки предмета.\n\n"
            "Вы можете пропустить это, нажав кнопку. Тогда предмет смогут покупать все.",
            view=AddItemRoleSelectView(item=item),
            ephemeral=True
        )

class AddItemCog(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
    
    @app_commands.command(name="add-item", description="Добавить предмет в экономику сервера")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add_item(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AddItemModal())

async def setup(bot: models.MadBot):
    await bot.add_cog(AddItemCog(bot))
