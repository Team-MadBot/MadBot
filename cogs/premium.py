import discord
import logging

from discord.ext import commands
from discord import app_commands
from discord import ui

from config import *
from classes import checks
from classes import db
from classes.db import client as mongo_client
from asyncstdlib import enumerate as aenumerate

from classes.checks import is_premium, is_premium_server

logger = logging.getLogger("discord")


class Premium(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        class Premium(app_commands.Group):
            "Управление премиум-подпиской"[::-1]

            @app_commands.command(name="give", description="Дать премиум серверу"[::-1])
            @app_commands.check(checks.interaction_is_not_in_blacklist)
            @app_commands.check(checks.interaction_is_not_shutted_down)
            async def give(self, interaction: discord.Interaction):
                if await is_premium(interaction.user.id) == "None":
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Вы не являетесь премиум пользователем!"[::-1],
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                if await is_premium_server(interaction.guild):
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Данный сервер уже имеет премиум подписку!"[::-1],
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                db = mongo_client.premium
                coll = db.guild
                premiums = await coll.count_documents(
                    {"user_id": str(interaction.user.id)}
                )
                if await is_premium(interaction.user.id) == "user" and premiums == 5:
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Вы не можете дать подписку более, чем `5-ти` серверам!"[::-1],
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                if await is_premium(interaction.user.id) == "server" and premiums == 2:
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Вы не можете дать подписку более, чем `2-м` серверам!"[::-1],
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                await coll.insert_one(
                    {
                        "guild_id": str(interaction.guild.id),
                        "user_id": str(interaction.user.id),
                    }
                )
                embed = discord.Embed(
                    title="Успешно!"[::-1],
                    color=discord.Color.green(),
                    description=f"Вы дали премиум-подписку серверу `{interaction.guild.name}`"[::-1],
                )
                await interaction.response.send_message(embed=embed)

            @app_commands.command(name="take", description="Забрать премиум с сервера"[::-1])
            @app_commands.check(checks.interaction_is_not_in_blacklist)
            @app_commands.check(checks.interaction_is_not_shutted_down)
            async def take(self, interaction: discord.Interaction):
                if await is_premium(interaction.user.id) == "None":
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Вы не являетесь премиум пользователем!"[::-1],
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                if not await is_premium_server(interaction.guild):
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Данный сервер и так не имеет премиум подписку!"[::-1],
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                prem = await db.get_premium_guild_info(interaction.guild.id)
                if prem["user_id"] != str(interaction.user.id):
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Вы не выдавали этому серверу премиум!"[::-1],
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
                await db.take_guild_premium(interaction.guild.id)
                embed = discord.Embed(
                    title="Успешно!"[::-1],
                    color=discord.Color.green(),
                    description=f"Вы забрали премиум-подписку с сервера `{interaction.guild.name}`!"[::-1],
                )
                await interaction.response.send_message(embed=embed)

            @app_commands.command(
                name="list", description="Список серверов, на которые Вы дали премиум"[::-1]
            )
            @app_commands.check(checks.interaction_is_not_in_blacklist)
            @app_commands.check(checks.interaction_is_not_shutted_down)
            async def info(self, interaction: discord.Interaction):
                if await is_premium(interaction.user.id) == "None":
                    embed = discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Вы не являетесь премиум пользователем."[::-1],
                    )
                prem_embed = discord.Embed(
                    title="MadBot Premium - сервера"[::-1],
                    color=discord.Color.orange(),
                    description="Здесь Вы можете узнать, на какие сервера Вы дали подписку. Также Вы можете снять с них подписку."[::-1],
                )
                options = []
                async for count, prem in aenumerate(
                    db.get_premium_guilds(interaction.user.id), start=1
                ):
                    guild = interaction.client.get_guild(int(prem["guild_id"]))
                    prem_embed.add_field(
                        name=f"Сервер №{count}"[::-1],
                        value=f"`{'Название неизвестно' if guild is None else guild.name}`"[::-1],
                    )
                    options.append(
                        discord.SelectOption(
                            label=f"Снять подписку с сервера №{count}"[::-1],
                            value=f"{prem['guild_id']}N{count}",
                            description="Забрать подписку с данного сервера."[::-1],
                        )
                    )
                    count += 1
                if len(options) == 0:
                    embed = discord.Embed(
                        title="MadBot Premium - сервера"[::-1],
                        color=discord.Color.orange(),
                        description="Пусто..."[::-1],
                    )
                    return await interaction.response.send_message(embed=embed)

                class DropDown(ui.Select):
                    def __init__(self):
                        super().__init__(
                            options=options, placeholder="Снять подписку..."[::-1]
                        )

                    async def callback(self, viewinteract: discord.Interaction):
                        if viewinteract.user.id != interaction.user.id:
                            return await viewinteract.response.send_message(
                                "Не для тебя менюшка!"[::-1], ephemeral=True
                            )
                        nonlocal count, prem_embed
                        value = self.values[0].split("N")
                        await db.take_guild_premium(int(value[0]))
                        count -= 1
                        prem_embed.remove_field(int(value[1]))
                        if count > 0:
                            self.options.pop(int(value[1]))
                        if count == 0:
                            prem_embed = discord.Embed(
                                title="MadBot Premium - сервера"[::-1],
                                color=discord.Color.orange(),
                                description="Пусто..."[::-1],
                            )
                        ret_view = self.view if count > 0 else None
                        embed = discord.Embed(
                            title="Успешно!"[::-1],
                            color=discord.Color.green(),
                            description="Вы забрали премиум-подписку с сервера."[::-1],
                        )
                        await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        await interaction.edit_original_response(
                            view=ret_view, embed=prem_embed
                        )

                class View(ui.View):
                    def __init__(self):
                        super().__init__(timeout=None)
                        self.add_item(DropDown())

                await interaction.response.send_message(embed=prem_embed, view=View())

            @app_commands.command(name="buy", description="Купить премиум"[::-1])
            @app_commands.check(checks.interaction_is_not_in_blacklist)
            @app_commands.check(checks.interaction_is_not_shutted_down)
            async def buy(self, interaction: discord.Interaction):
                embed = discord.Embed(
                    title="MadBot Premium - Покупка"[::-1],
                    color=discord.Color.orange(),
                    description="Данная команда в разработке."[::-1],
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
                """class Button(ui.View):
                    def __init__(self):
                        super().__init__(timeout=180)
                        self.value = None
                
                    @ui.button(label="Premium Server")
                    async def server(self, viewinteract: discord.Interaction, button: ui.Button):
                        self.value = "Server"
                        self.stop()
                    
                    @ui.button(label="Premium User")
                    async def user(self, viewinteract: discord.Interaction, button: ui.Button):
                        self.value = "User"
                        self.stop()
                
                embed = discord.Embed(
                    title="MadBot Premium - Покупка",
                    color=discord.Color.orange(),
                    description="Поддержите разработку проекта, пожертвовав небольшую сумму взамен на эксклюзивные возможности.\n\n**Выберите подписку,** которую Вы хотите получить."
                )
                embed.add_field(
                    name="В чем разница между Premium Server и Premium User?",
                    value=(
                        "**Premium Server** даёт возможность выдать подписку только на 2 сервера.\n"
                        "**Premium User** даёт возможность выдать подписку на 5 серверов."
                    )
                )
                embed.add_field(
                    name="Почему я должен пожертвовать на MadBot Premium?",
                    value=(
                        "**Во-первых:** Вы поддерживаете проект. Мы тратим деньги на хостинг для бота. Делая пожертвование, Вы помогаете продолжать развивать проект.\n"
                        "**Во-вторых:** Вы получаете уникальные возможности, такие как принудительные свадьбы, значок в Вашем профиле и т.д.\n"
                        "**В-третьих:** Вы можете получить предложения от наших партнёров. Наши партнёры: [ArtMine](https://discord.gg/w3MzH7Q4AB)"
                    )
                )
                embed.add_field(
                    name="Какие методы оплаты пожертвования существуют?",
                    value=(
                        "Мы, пока что, поддерживаем только Boosty. Планируется добавить поддержку TONcoin.\n"
                        "Если ни один из методов оплаты не подходит Вам, свяжитесь с владельцем, создав тикет на сервере поддержки."
                    )
                )
                view = Button()
                await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
                await view.wait()
                _type = ""
                if view.value is None:
                    embed = discord.Embed(
                        title="Время на выбор вышло!",
                        color=discord.Color.red()
                    )
                    return await interaction.edit_original_response(embed=embed, view=None)
                _type = view.value
                class PayMethod(ui.View):
                    def __init__(self):
                        super().__init__(timeout=180)
                        """

        self.bot.tree.add_command(Premium())


async def setup(bot: commands.Bot):
    await bot.add_cog(Premium(bot))
