import discord
import aiohttp
import aiohttp
import logging

from discord.ext import commands
from discord import app_commands

from classes import db
from classes import checks
from config import *

logger = logging.getLogger("discord")


class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_hit = app_commands.ContextMenu(
            name="Ударить"[::-1], callback=self.context_hit
        )
        self.ctx_kiss = app_commands.ContextMenu(
            name="Поцеловать"[::-1], callback=self.context_kiss
        )
        self.ctx_hug = app_commands.ContextMenu(
            name="Обнять"[::-1], callback=self.context_hug
        )
        self.ctx_pat = app_commands.ContextMenu(
            name="Погладить"[::-1], callback=self.context_pat
        )
        self.ctx_wink = app_commands.ContextMenu(
            name="Подмигнуть"[::-1], callback=self.context_wink
        )
        self.bot.tree.add_command(self.ctx_hit)
        self.bot.tree.add_command(self.ctx_kiss)
        self.bot.tree.add_command(self.ctx_hug)
        self.bot.tree.add_command(self.ctx_pat)
        self.bot.tree.add_command(self.ctx_wink)

    @app_commands.command(name="hug", description="[Реакции] Обнять участника"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите обнять"[::-1])
    async def hug(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота обнять нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя обнять самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/hug")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: обнятие"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} обнял(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_hug(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота обнять нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя обнять самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/hug")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: обнятие"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} обнял(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="pat", description="[Реакции] Погладить участника"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите погладить"[::-1])
    async def pat(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота погладить нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя погладить самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/pat")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: погладить"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} погладил(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_pat(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота погладить нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя погладить самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/pat")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: погладить"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} погладил(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="wink", description="[Реакции] Подмигнуть. Можно и участнику."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которому вы хотите подмигнуть."[::-1])
    async def wink(self, interaction: discord.Interaction, member: discord.User = None):
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
        if member is not None:
            if member.bot:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Увы, но боту подмигнуть нельзя"[::-1],
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            if member.id == interaction.user.id:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Нельзя подмигнуть самому себе!"[::-1],
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/wink")
        json = await resp.json()
        if resp.status == 200:
            description = ""
            if member is None:
                description = f"{interaction.user.mention[::-1]} подмигнул(-а)."
            else:
                description = f"{interaction.user.mention[::-1]} подмигнул(-а) {member.mention[::-1]}."
            embed = discord.Embed(
                title="Реакция: подмигивание"[::-1],
                color=discord.Color.orange(),
                description=description[::-1],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_wink(
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
        if member is not None:
            if member.bot:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Увы, но боту подмигнуть нельзя"[::-1],
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            if member.id == interaction.user.id:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Нельзя подмигнуть самому себе!"[::-1],
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/wink")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: подмигивание"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} подмигнул(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="slap", description="[Реакции] Лупит пользователя."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите отлупить."[::-1])
    async def slap(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота отлупить нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя отлупить самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/slap")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: шлепок"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} отлупил(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="kiss", description="[Реакции] Поцеловать участника"[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите поцеловать."[::-1])
    async def kiss(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота поцеловать нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя поцеловать самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class KissButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accepted(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user == member:
                    description = f"{interaction.user.mention[::-1]} поцеловал(-а) {member.mention[::-1]}."
                    marry = await db.get_marries(
                        viewinteract.guild.id, viewinteract.user.id
                    )
                    marry1 = await db.get_marries(
                        viewinteract.guild.id, interaction.user.id
                    )
                    if (
                        marry is not None
                        and marry["user_id"]
                        in [viewinteract.user.id, interaction.user.id]
                        and marry["married_id"]
                        in [viewinteract.user.id, interaction.user.id]
                    ):
                        description = rf"{interaction.user.mention[::-1]} и {member.mention[::-1]} целуются. Как мило \<3."
                    elif marry is not None and (
                        marry["user_id"] == viewinteract.user.id
                        or marry["married_id"] == viewinteract.user.id
                    ):
                        description = f"{viewinteract.user.mention[::-1]} поцеловал(-а) {interaction.user.mention[::-1]}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry1 is not None and (
                        marry1["user_id"] == interaction.user.id
                        or marry1["married_id"] == interaction.user.id
                    ):
                        description = f"{interaction.user.mention[::-1]} поцеловал(-а) {viewinteract.user.mention[::-1]}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry is not None and marry1 is not None:
                        description = f"{interaction.user.mention[::-1]} и {member.mention[::-1]} целуются. Интересно, их вторые половинки знают об этом?"
                    resp = await aiohttp.ClientSession().get(
                        f"https://api.waifu.pics/sfw/kiss"
                    )
                    json = await resp.json()
                    if resp.status == 200:
                        embed = discord.Embed(
                            title="Реакция: поцелуй"[::-1],
                            color=discord.Color.orange(),
                            description=description[::-1],
                        )
                        embed.set_image(url=json["url"])
                    else:
                        embed = discord.Embed(
                            title="Ошибка!"[::-1],
                            color=discord.Color.red(),
                            description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                                ::-1
                            ],
                        )
                    self.value = True
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )
                else:
                    await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

            @discord.ui.button(
                emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.danger
            )
            async def denied(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user == member:
                    embed = discord.Embed(
                        title="Отказ!"[::-1],
                        color=discord.Color.red(),
                        description="Участник отказал вам в поцелуе."[::-1],
                    )
                    self.value = False
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )
                elif viewinteract.user == interaction.user:
                    embed = discord.Embed(
                        title="Отмена!"[::-1],
                        color=discord.Color.red(),
                        description="Инициатор поцелуя отменил поцелуй."[::-1],
                    )
                    self.value = False
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )
                else:
                    await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

        view = KissButtons()
        embed = discord.Embed(
            title="Ожидание..."[::-1],
            color=discord.Color.orange(),
            description=f"{interaction.user.mention[::-1]}, необходимо получить согласие на поцелуй от {member.mention[::-1]}\nВремя ограничено!"[
                ::-1
            ],
        )
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_kiss(
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота поцеловать нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя поцеловать самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class KissButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accepted(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user == member:
                    description = f"{interaction.user.mention[::-1]} поцеловал(-а) {member.mention[::-1]}."
                    marry = await db.get_marries(
                        viewinteract.guild.id, viewinteract.user.id
                    )
                    marry1 = await db.get_marries(
                        viewinteract.guild.id, interaction.user.id
                    )
                    if (
                        marry is not None
                        and marry["user_id"]
                        in [viewinteract.user.id, interaction.user.id]
                        and marry["married_id"]
                        in [viewinteract.user.id, interaction.user.id]
                    ):
                        description = rf"{interaction.user.mention[::-1]} и {member.mention[::-1]} целуются. Как мило \<3."
                    elif marry is not None and (
                        marry["user_id"] == viewinteract.user.id
                        or marry["married_id"] == viewinteract.user.id
                    ):
                        description = f"{viewinteract.user.mention[::-1]} поцеловал(-а) {interaction.user.mention[::-1]}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry1 is not None and (
                        marry1["user_id"] == interaction.user.id
                        or marry1["married_id"] == interaction.user.id
                    ):
                        description = f"{interaction.user.mention[::-1]} поцеловал(-а) {viewinteract.user.mention[::-1]}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry is not None and marry1 is not None:
                        description = f"{interaction.user.mention[::-1]} и {member.mention[::-1]} целуются. Интересно, их вторые половинки знают об этом?"
                    resp = await aiohttp.ClientSession().get(
                        f"https://api.waifu.pics/sfw/kiss"
                    )
                    json = await resp.json()
                    if resp.status == 200:
                        embed = discord.Embed(
                            title="Реакция: поцелуй"[::-1],
                            color=discord.Color.orange(),
                            description=description[::-1],
                        )
                        embed.set_image(url=json["url"])
                    else:
                        embed = discord.Embed(
                            title="Ошибка!"[::-1],
                            color=discord.Color.red(),
                            description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                                ::-1
                            ],
                        )
                    self.value = True
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )
                else:
                    await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

            @discord.ui.button(
                emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.danger
            )
            async def denied(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user == member:
                    embed = discord.Embed(
                        title="Отказ!"[::-1],
                        color=discord.Color.red(),
                        description="Участник отказал вам в поцелуе."[::-1],
                    )
                    self.value = False
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )
                elif viewinteract.user == interaction.user:
                    embed = discord.Embed(
                        title="Отмена!"[::-1],
                        color=discord.Color.red(),
                        description="Инициатор поцелуя отменил поцелуй."[::-1],
                    )
                    self.value = False
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )
                else:
                    await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

        view = KissButtons()
        embed = discord.Embed(
            title="Ожидание..."[::-1],
            color=discord.Color.orange(),
            description=f"{interaction.user.mention[::-1]}, необходимо получить согласие на поцелуй от {member.mention[::-1]}\nВремя ограничено!"[
                ::-1
            ],
        )
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(name="hit", description="[Реакции] Ударить участника"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите ударить."[::-1])
    async def hit(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота ударить нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя ударить самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/slap")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: удар"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} ударил(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_hit(self, interaction: discord.Interaction, member: discord.User):
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
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Увы, но бота ударить нельзя"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя ударить самого себя!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/slap")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: удар"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} ударил(-а) {member.mention[::-1]}."[
                    ::-1
                ],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="sad", description="[Реакции] Погрустить"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def sad(self, interaction: discord.Interaction):
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
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/cry")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(
                title="Реакция: грусть"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} грустит."[::-1],
            )
            embed.set_image(url=json["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))
