import discord
import aiohttp
import aiohttp
import logging

from discord.ext import commands
from discord import app_commands

from classes import db
from classes import checks
from config import *

logger = logging.getLogger('discord')

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_hit = app_commands.ContextMenu(
            name="Ударить",
            callback=self.context_hit
        )
        self.ctx_kiss = app_commands.ContextMenu(
            name="Поцеловать",
            callback=self.context_kiss
        )
        self.ctx_hug = app_commands.ContextMenu(
            name="Обнять",
            callback=self.context_hug
        )
        self.ctx_pat = app_commands.ContextMenu(
            name="Погладить",
            callback=self.context_pat
        )
        self.ctx_wink = app_commands.ContextMenu(
            name="Подмигнуть",
            callback=self.context_wink
        )
        self.bot.tree.add_command(self.ctx_hit)
        self.bot.tree.add_command(self.ctx_kiss)
        self.bot.tree.add_command(self.ctx_hug)
        self.bot.tree.add_command(self.ctx_pat)
        self.bot.tree.add_command(self.ctx_wink)
    
    @app_commands.command(name="hug", description="[Реакции] Обнять участника")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите обнять")
    async def hug(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота обнять нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя обнять самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/hug")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: обнятие", color=discord.Color.orange(), description=f"{interaction.user.mention} обнял(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_hug(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота обнять нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя обнять самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/hug")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: обнятие", color=discord.Color.orange(), description=f"{interaction.user.mention} обнял(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="pat", description="[Реакции] Погладить участника")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите погладить")
    async def pat(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота погладить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя погладить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/pat")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: погладить", color=discord.Color.orange(), description=f"{interaction.user.mention} погладил(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_pat(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота погладить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя погладить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/pat")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: погладить", color=discord.Color.orange(), description=f"{interaction.user.mention} погладил(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="wink", description="[Реакции] Подмигнуть. Можно и участнику.")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которому вы хотите подмигнуть.")
    async def wink(self, interaction: discord.Interaction, member: discord.User = None):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member is not None:
            if member.bot:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но боту подмигнуть нельзя")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if member.id == interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя подмигнуть самому себе!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/wink")
        json = await resp.json()
        if resp.status == 200:
            description = ''
            if member is None:
                description = f"{interaction.user.mention} подмигнул(-а)."
            else:
                description = f"{interaction.user.mention} подмигнул(-а) {member.mention}."
            embed = discord.Embed(title="Реакция: подмигивание", color=discord.Color.orange(), description=description)
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_wink(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member is not None:
            if member.bot:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но боту подмигнуть нельзя")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if member.id == interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя подмигнуть самому себе!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/wink")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: подмигивание", color=discord.Color.orange(), description=f"{interaction.user.mention} подмигнул(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="slap", description="[Реакции] Лупит пользователя.")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите отлупить.")
    async def slap(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота отлупить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя отлупить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/slap")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: шлепок", color=discord.Color.orange(), description=f"{interaction.user.mention} отлупил(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="kiss", description="[Реакции] Поцеловать участника")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите поцеловать.")
    async def kiss(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота поцеловать нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя поцеловать самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)



        class KissButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accepted(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user == member:
                    description = f"{interaction.user.mention} поцеловал(-а) {member.mention}."
                    marry = await db.get_marries(viewinteract.guild.id, viewinteract.user.id)
                    marry1 = await db.get_marries(viewinteract.guild.id, interaction.user.id)
                    if (
                        marry is not None
                        and marry['user_id']
                        in [viewinteract.user.id, interaction.user.id]
                        and marry['married_id']
                        in [viewinteract.user.id, interaction.user.id]
                    ):
                        description = fr"{interaction.user.mention} и {member.mention} целуются. Как мило \<3."
                    elif marry is not None and (marry['user_id'] == viewinteract.user.id or marry['married_id'] == viewinteract.user.id):
                        description = f"{viewinteract.user.mention} поцеловал(-а) {interaction.user.mention}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry1 is not None and (marry1['user_id'] == interaction.user.id or marry1['married_id'] == interaction.user.id):
                        description = f"{interaction.user.mention} поцеловал(-а) {viewinteract.user.mention}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry is not None and marry1 is not None:
                        description = f"{interaction.user.mention} и {member.mention} целуются. Интересно, их вторые половинки знают об этом?"
                    resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/kiss")
                    json = await resp.json()
                    if resp.status == 200:
                        embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=description)
                        embed.set_image(url=json['url'])
                    else:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
                    self.value = True
                    return await interaction.edit_original_response(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

            @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.danger)
            async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user == member:
                    embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
                    self.value = False
                    return await interaction.edit_original_response(embed=embed, view=None)
                elif viewinteract.user == interaction.user:
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Инициатор поцелуя отменил поцелуй.")
                    self.value = False
                    return await interaction.edit_original_response(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)


        view = KissButtons()
        embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
            await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_kiss(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота поцеловать нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя поцеловать самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)



        class KissButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accepted(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user == member:
                    description = f"{interaction.user.mention} поцеловал(-а) {member.mention}."
                    marry = await db.get_marries(viewinteract.guild.id, viewinteract.user.id)
                    marry1 = await db.get_marries(viewinteract.guild.id, interaction.user.id)
                    if (
                        marry is not None
                        and marry['user_id']
                        in [viewinteract.user.id, interaction.user.id]
                        and marry['married_id']
                        in [viewinteract.user.id, interaction.user.id]
                    ):
                        description = fr"{interaction.user.mention} и {member.mention} целуются. Как мило \<3."
                    elif marry is not None and (marry['user_id'] == viewinteract.user.id or marry['married_id'] == viewinteract.user.id):
                        description = f"{viewinteract.user.mention} поцеловал(-а) {interaction.user.mention}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry1 is not None and (marry1['user_id'] == interaction.user.id or marry1['married_id'] == interaction.user.id):
                        description = f"{interaction.user.mention} поцеловал(-а) {viewinteract.user.mention}. Надеюсь, его вторая половинка об этом не узнает..."
                    elif marry is not None and marry1 is not None:
                        description = f"{interaction.user.mention} и {member.mention} целуются. Интересно, их вторые половинки знают об этом?"
                    resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/kiss")
                    json = await resp.json()
                    if resp.status == 200:
                        embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=description)
                        embed.set_image(url=json['url'])
                    else:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
                    self.value = True
                    return await interaction.edit_original_response(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

            @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.danger)
            async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user == member:
                    embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
                    self.value = False
                    return await interaction.edit_original_response(embed=embed, view=None)
                elif viewinteract.user == interaction.user:
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Инициатор поцелуя отменил поцелуй.")
                    self.value = False
                    return await interaction.edit_original_response(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)


        view = KissButtons()
        embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
            await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(name="hit", description="[Реакции] Ударить участника")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите ударить.")
    async def hit(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота ударить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя ударить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/slap")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: удар", color=discord.Color.orange(), description=f"{interaction.user.mention} ударил(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def context_hit(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота ударить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя ударить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/slap")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: удар", color=discord.Color.orange(), description=f"{interaction.user.mention} ударил(-а) {member.mention}.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="sad", description="[Реакции] Погрустить")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def sad(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = await aiohttp.ClientSession().get(f"https://api.waifu.pics/sfw/cry")
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Реакция: грусть", color=discord.Color.orange(), description=f"{interaction.user.mention} грустит.")
            embed.set_image(url=json['url'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    

async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))
