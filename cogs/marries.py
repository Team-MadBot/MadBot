import discord
import logging
import datetime

from asyncstdlib import enumerate as aenumerate
from discord.ext import commands
from discord import app_commands
from discord import ui
from classes import db

from classes import checks
from config import *

logger = logging.getLogger("discord")


class Marries(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="marry", description="[Свадьбы] Пожениться"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, с которым Вы хотите пожениться."[::-1])
    async def marry(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        user_id = interaction.user.id
        member_id = member.id

        if member_id == user_id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя жениться на самому себе!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя жениться на боте!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        marry = await db.get_marries(interaction.guild.id, user_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="У Вас есть активный брак! Разведитесь перед заведением нового брака."[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        marry = await db.get_marries(interaction.guild.id, member_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Данный пользователь уже в браке!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class Accept(ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None
                self.user_id = member_id

            @ui.button(label="Да"[::-1], style=discord.ButtonStyle.green)
            async def yes(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id != member_id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = True
                self.stop()

            @ui.button(label="Нет"[::-1], style=discord.ButtonStyle.red)
            async def no(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id == user_id:
                    self.value = False
                    self.user_id = user_id
                    return self.stop()
                if viewinteract.user.id != member_id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = False
                self.stop()

        embed = discord.Embed(
            title="Свадьба - Ожидание"[::-1],
            color=discord.Color.yellow(),
            description=f"{f'<@!{user_id}>'[::-1]} хочет пожениться на Вас. Вы согласны?"[
                ::-1
            ],
        )
        embed.set_footer(text="Время на ответ: 3 минуты."[::-1])
        view = Accept()
        await interaction.response.send_message(
            embed=embed, content=f"<@!{member_id}>", view=view
        )
        await view.wait()
        if view.value is None:
            embed = discord.Embed(title="Время вышло!"[::-1], color=discord.Color.red())
            return await interaction.edit_original_response(
                embed=embed, content=None, view=None
            )
        if not view.value and view.user_id == user_id:
            embed = discord.Embed(
                title="Свадьба - Отмена"[::-1],
                color=discord.Color.red(),
                description="Инициатор отменил свадьбу."[::-1],
            )
            return await interaction.edit_original_response(
                embed=embed, content=None, view=None
            )
        if not view.value and view.user_id == member_id:
            embed = discord.Embed(
                title="Свадьба - Отказ"[::-1],
                color=discord.Color.red(),
                description="Вам отказали в свадьбе."[::-1],
            )
            return await interaction.edit_original_response(
                embed=embed, content=None, view=None
            )
        await db.marry(interaction.guild.id, user_id, member_id)
        embed = discord.Embed(
            title="Свадьба - Поздравляем!"[::-1],
            color=discord.Color.green(),
            description=f"{f'<@!{user_id}>'[::-1]} и {f'<@!{member_id}>'[::-1]} теперь женаты. Горько!"[
                ::-1
            ],
        )
        await interaction.edit_original_response(embed=embed, content=None, view=None)

    @app_commands.command(name="divorce", description="[Свадьбы] Развод"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def dibvorce(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        user_id = interaction.user.id

        marry = await db.get_marries(interaction.guild.id, user_id)
        if marry is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="У Вас нет активного брака!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class Accept(ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None

            @ui.button(label="Да"[::-1], style=discord.ButtonStyle.green)
            async def yes(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id != user_id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = True
                self.stop()

            @ui.button(label="Нет"[::-1], style=discord.ButtonStyle.red)
            async def no(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id != user_id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = False
                self.stop()

        married_id = marry["married_id"]
        embed = discord.Embed(
            title="Развод - Подтверждение"[::-1],
            color=discord.Color.yellow(),
            description=f'Вы действительно хотите развестись с {f"<@!{married_id if married_id != user_id else user_id}>"}?'[
                ::-1
            ],
        )
        embed.set_footer(text="Время на ответ: 3 минуты."[::-1])
        view = Accept()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(title="Время вышло!"[::-1], color=discord.Color.red())
            return await interaction.edit_original_response(
                embed=embed, content=None, view=None
            )
        if not view.value:
            embed = discord.Embed(
                title="Развод - Отмена"[::-1],
                color=discord.Color.red(),
                description="Вы отменили развод."[::-1],
            )
            return await interaction.edit_original_response(
                embed=embed, content=None, view=None
            )
        await db.divorce(interaction.guild.id, user_id)
        embed = discord.Embed(
            title="Развод - Завершено!"[::-1],
            color=discord.Color.green(),
            description="Вы успешно развелись. Надеемся, все будет хорошо..."[::-1],
        )
        await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(
        name="marry-info", description="[Свадьбы] Информация о Вашем браке"[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, чей брак Вы хотите посмотреть."[::-1])
    async def marry_info(
        self, interaction: discord.Interaction, member: discord.User = None
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        user_id = interaction.user.id if member is None else member.id

        marry = await db.get_marries(interaction.guild.id, user_id)
        if marry is None:
            if user_id == interaction.user.id:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Вы не имеете активного брака!"[::-1],
                )
            else:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Пользователь не имеет активного брака!"[::-1],
                )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        married_id = marry["married_id"]
        user_id = marry["user_id"]

        embed = discord.Embed(
            title="Информация о браке"[::-1],
            color=discord.Color.orange(),
            description=(
                f"{discord.utils.format_dt(datetime.datetime.fromtimestamp(marry['dt']), 'R')[::-1]}"
                f"{f'<@!{user_id}>'[::-1]} сделал предложение руки и сердца {f'<@!{married_id}>'[::-1]}. До сих пор они вместе."
            )[::-1],
        )
        embed.add_field(name="Дата заключения:"[::-1], value=f"<t:{marry['dt']}>")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="marries", description="[Свадьбы] Список браков."[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def marries(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        description = (
            "\n\n".join(
                [
                    f"`{count}.` <@!{marry['user_id']}> и <@!{marry['married_id']}>.\nДата заключения брака: <t:{marry['dt']}> (<t:{marry['dt']}:R>)."
                    async for count, marry in aenumerate(
                        db.get_all_marries(guild_id=interaction.guild.id), start=1
                    )
                ]
            )
            or "*Пусто...*"
        )

        embed = discord.Embed(
            title="Браки сервера:"[::-1],
            color=discord.Color.orange(),
            description=description[::-1],
        )
        embed.set_footer(
            text="Используйте команду /marry для предложения заключения брака."[::-1]
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="marry-people", description="[Свадьбы] Поженить принудительно пару."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(
        member="Участник, которого Вы хотите поженить."[::-1],
        member2="Участник, с кем Вы хотите поженить первого участника."[::-1],
    )
    async def marry_people(
        self,
        interaction: discord.Interaction,
        member: discord.User,
        member2: discord.User,
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Для принудительной свадьбы необходимо право на `управление сервером`."[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        user_id = member.id
        member_id = member2.id

        if member_id == user_id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя женить человека самим с собой!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot or member2.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя женить на боте!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        marry = await db.get_marries(interaction.guild.id, user_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"У {f'<@!{user_id}>'[::-1]} есть активный брак! Разведите его перед заведением нового брака."[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        marry = await db.get_marries(interaction.guild.id, member_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"У {f'<@!{member_id}>'[::-1]} есть активный брак! Разведите его перед заведением нового брака."[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await db.marry(interaction.guild.id, user_id, member_id)
        embed = discord.Embed(
            title="Свадьба - Поздравляем!"[::-1],
            color=discord.Color.green(),
            description=f"Вы поженены купидоном {interaction.user.mention[::-1]}. Горько!"[
                ::-1
            ],
        )
        await interaction.response.send_message(
            embed=embed, content=f"<@!{user_id}> и <@!{member_id}>"
        )

    @app_commands.command(
        name="divorce-people",
        description="[Свадьбы] Развести принудительно пару."[::-1],
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого Вы хотите развести."[::-1])
    async def divorce_people(
        self, interaction: discord.Interaction, member: discord.User
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Для принудительного развода необходимо право на `управление сервером`."[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        user_id = member.id

        if interaction.user.id == user_id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя развести принудительно себя! Используйте `/divorce`."[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Разве боты могут жениться?"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        marry = await db.get_marries(interaction.guild.id, user_id)
        if marry is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"У {f'<@!{user_id}>'[::-1]} нет активного брака!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await db.divorce(interaction.guild.id, user_id)
        embed = discord.Embed(
            title="Развод - Успешно!"[::-1],
            color=discord.Color.green(),
            description=f"Вы разведены антикупидоном {interaction.user.mention[::-1]}."[
                ::-1
            ],
        )
        await interaction.response.send_message(
            embed=embed, content=f"<@!{marry['user_id']}> и <@!{marry['married_id']}>"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Marries(bot))
