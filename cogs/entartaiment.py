"""
MIT License

Copyright (c) 2022 Mad Cat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import discord, datetime, requests, random, config
from asyncio import sleep
from hmtai import useHM
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from random import choice
from config import *
from typing import List

def is_shutted_down(interaction: discord.Interaction):
    return interaction.command.name not in shutted_down

class Entartaiment(commands.Cog):
    def __init__(self, bot: commands.Bot):
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

    @app_commands.command(name="cat", description="[Развлечения] Присылает рандомного котика")
    @app_commands.check(is_shutted_down)
    async def cat(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/cat`'
        resp = requests.get(f"https://some-random-api.ml/animal/cat?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            embed = discord.Embed(title="Мяу!", color=discord.Color.orange())
            embed.set_image(url=json['image'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось совершить запрос на сервер!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="dog", description="[Развлечения] Присылает рандомного пёсика")
    @app_commands.check(is_shutted_down)
    async def dog(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/dog`'
        resp = requests.get(f"https://some-random-api.ml/animal/dog?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            embed = discord.Embed(title="Гав!", color=discord.Color.orange())
            embed.set_image(url=json['image'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось совершить запрос на сервер!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="hug", description="[Реакции] Обнять участника")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите обнять")
    async def hug(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/hug`'
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота обнять нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя обнять самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = requests.get(f"https://some-random-api.ml/animu/hug?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            embed = discord.Embed(title="Реакция: обнятие", color=discord.Color.orange(), description=f"{interaction.user.mention} обнял(-а) {member.mention}.")
            embed.set_image(url=json['link'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(is_shutted_down)
    async def context_hug(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/hug`'
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота обнять нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя обнять самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = requests.get(f"https://some-random-api.ml/animu/hug?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            embed = discord.Embed(title="Реакция: обнятие", color=discord.Color.orange(), description=f"{interaction.user.mention} обнял(-а) {member.mention}.")
            embed.set_image(url=json['link'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="pat", description="[Реакции] Погладить участника")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите погладить")
    async def pat(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/pat`'
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота погладить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя погладить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = requests.get(f"https://some-random-api.ml/animu/pat?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            embed = discord.Embed(title="Реакция: погладить", color=discord.Color.orange(), description=f"{interaction.user.mention} погладил(-а) {member.mention}.")
            embed.set_image(url=json['link'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(is_shutted_down)
    async def context_pat(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/pat`'
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота погладить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя погладить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = requests.get(f"https://some-random-api.ml/animu/pat?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            embed = discord.Embed(title="Реакция: погладить", color=discord.Color.orange(), description=f"{interaction.user.mention} погладил(-а) {member.mention}.")
            embed.set_image(url=json['link'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="wink", description="[Реакции] Подмигнуть. Можно и участнику.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, которому вы хотите подмигнуть.")
    async def wink(self, interaction: discord.Interaction, member: discord.User = None):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/wink`'
        if member != None:
            if member.bot:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но боту подмигнуть нельзя")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if member.id == interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя подмигнуть самому себе!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = requests.get(f"https://some-random-api.ml/animu/wink?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            description = ''
            if member == None:
                description = f"{interaction.user.mention} подмигнул(-а)."
            else:
                description = f"{interaction.user.mention} подмигнул(-а) {member.mention}."
            embed = discord.Embed(title="Реакция: подмигивание", color=discord.Color.orange(), description=description)
            embed.set_image(url=json['link'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(is_shutted_down)
    async def context_wink(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/wink`'
        if member != None:
            if member.bot:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но боту подмигнуть нельзя")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if member.id == interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя подмигнуть самому себе!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        resp = requests.get(f"https://some-random-api.ml/animu/wink?key={settings['key']}")
        json = resp.json()
        if resp.status_code == 200:
            embed = discord.Embed(title="Реакция: подмигивание", color=discord.Color.orange(), description=f"{interaction.user.mention} подмигнул(-а) {member.mention}.")
            embed.set_image(url=json['link'])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="slap", description="[Реакции] Лупит пользователя.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите отлупить.")
    async def slap(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/slap`'
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота отлупить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя отлупить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Реакция: шлёп", color=discord.Color.orange(), description=f"{interaction.user.mention} отлупил(-а) {member.mention}.")
        embed.set_image(url=random.choice(slap_gifs))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kiss", description="[Реакции] Поцеловать участника")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите поцеловать.")
    async def kiss(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/kiss`'
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
                    embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=f"{interaction.user.mention} поцеловал(-а) {member.mention}.")
                    embed.set_image(url=random.choice(kiss_gifs))
                    self.value = True
                    return await interaction.edit_original_message(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

            @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.danger)
            async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user == member:
                    embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
                    self.value = False
                    return await interaction.edit_original_message(embed=embed, view=None)
                elif viewinteract.user == interaction.user:
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Инициатор поцелуя отменил поцелуй.")
                    self.value = False
                    return await interaction.edit_original_message(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

        view = KissButtons()
        embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
            await interaction.edit_original_message(embed=embed, view=None)

    @app_commands.check(is_shutted_down)
    async def context_kiss(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/kiss`'
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
                    embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=f"{interaction.user.mention} поцеловал(-а) {member.mention}.")
                    embed.set_image(url=random.choice(kiss_gifs))
                    self.value = True
                    return await interaction.edit_original_message(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

            @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.danger)
            async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user == member:
                    embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
                    self.value = False
                    return await interaction.edit_original_message(embed=embed, view=None)
                elif viewinteract.user == interaction.user:
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Инициатор поцелуя отменил поцелуй.")
                    self.value = False
                    return await interaction.edit_original_message(embed=embed, view=None)
                else:
                    await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

        view = KissButtons()
        embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
            await interaction.edit_original_message(embed=embed, view=None)

    @app_commands.command(name="hit", description="[Реакции] Ударить участника")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, которого вы хотите ударить.")
    async def hit(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/hit`'
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота ударить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя ударить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Реакция: удар", color=discord.Color.orange(), description=f"{interaction.user.mention} ударил(-а) {member.mention}.")
        embed.set_image(url=random.choice(hit_gifs))
        await interaction.response.send_message(embed=embed)

    @app_commands.check(is_shutted_down)
    async def context_hit(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/hit`'
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота ударить нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя ударить самого себя!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Реакция: удар", color=discord.Color.orange(), description=f"{interaction.user.mention} ударил(-а) {member.mention}.")
        embed.set_image(url=random.choice(hit_gifs))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nsfw", description="[NSFW] Присылает NSFW картинку на тематику (бе).")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(choice="Тематика NSFW картинки", is_ephemeral="Выберите, будет ли картинка отправлена только вам.")
    @app_commands.choices(choice=[
        Choice(name="Ass", value="ass"),
        Choice(name="BDSM", value="bdsm"),
        Choice(name="Cum", value="cum"),
        Choice(name="Creampie", value="creampie"),
        Choice(name="Manga", value="manga"),
        Choice(name="Femdom", value="femdom"),
        Choice(name="Hentai", value="hentai"),
        Choice(name="Public", value="public"),
        Choice(name="Ero", value="ero"),
        Choice(name="Orgy", value="orgy"),
        Choice(name="Yuri", value="yuri"),
        Choice(name="Glasses", value="glasses"),
        Choice(name="Cuckold", value="cuckold"),
        Choice(name="Blowjob", value="blowjob"),
        Choice(name="Boobjob", value="boobjob"),
        Choice(name="Foot", value="foot"),
        Choice(name="Thighs", value="thighs"),
        Choice(name="Vagina", value="pussy"),
        Choice(name="Uniform", value="uniform"),
        Choice(name="Gangbang", value="gangbang"),
        Choice(name="Tentacles", value="tentacles"),
        Choice(name="GIF", value="hnt_gifs"),
        Choice(name="NSFW Neko", value="nsfwNeko")
    ])
    async def nsfw(self, interaction: discord.Interaction, choice: Choice[str], is_ephemeral: bool = False):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/nsfw`'
        if interaction.channel.is_nsfw():
            embed = discord.Embed(title=choice.name, color=discord.Color.orange())
            embed.set_image(url=useHM(29, choice.value))
            await interaction.response.send_message(embed=embed, ephemeral=is_ephemeral)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Данный канал не является NSFW каналом!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="math", description="[Развлечения] Реши несложный пример на сложение/вычитание")
    @app_commands.check(is_shutted_down)
    async def math_cmd(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/math`'
        choice = ['+','-']
        tosolve = f"{random.randint(9,99)} {random.choice(choice)} {random.randint(9,99)}"
        answer = eval(tosolve)
        start = time.time()

        class Button(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=15)
                self.value = None

            @discord.ui.button(label="Ответить", style=discord.ButtonStyle.blurple)
            async def solve(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user != interaction.user:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                class InputText(discord.ui.Modal, title=f"Сколько будет {tosolve}?"):
                    ans = discord.ui.TextInput(label="Ответ", style=discord.TextStyle.short, required=True, placeholder="14", max_length=4)
                    async def on_submit(self, modalinteract: discord.Interaction):
                        try:
                            temp = int(str(self.ans))
                        except:
                            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы ввели не число!")
                            embed1 = discord.Embed(title="Ответ некорректный!", color=discord.Color.red(), description=f"Пример: `{tosolve}`.\nПравильный ответ: `{answer}`.")
                            await interaction.edit_original_message(embed=embed1, view=None)
                            return await modalinteract.response.send_message(embed=embed, ephemeral=True)
                        if int(str(self.ans)) == int(answer):
                            wasted = time.time() - start
                            embed = discord.Embed(title="Правильно!", color=discord.Color.green(), description=f"Ответ: `{answer}`. Время ответа: `{round(wasted, 3)}s`.")
                            embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                            await interaction.edit_original_message(view=None)
                            await modalinteract.response.send_message(embed=embed)
                        else:
                            embed = discord.Embed(title="Неправильно!", color=discord.Color.red(), description=f"Ваш ответ: `{self.ans}`\nПравильный ответ: `{answer}`.")
                            embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                            await interaction.edit_original_message(view=None)
                            await modalinteract.response.send_message(embed=embed)

                await viewinteract.response.send_modal(InputText())

        embed = discord.Embed(title="Реши пример!", color=discord.Color.orange(), description=f"`{tosolve}`\nВремя на решение: `15 секунд`.")
        embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=Button())
        await sleep(15)
        await interaction.edit_original_message(view=None)

    @app_commands.command(name="doors", description="[Развлечения] Угадай дверь.")
    @app_commands.check(is_shutted_down)
    async def doors(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/doors`'

        class DoorsButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=15)
                self.value = None

            @discord.ui.button(label="1", emoji="🚪", style=discord.ButtonStyle.green)
            async def button_one(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if interaction.user == viewinteract.user:
                    answer = random.randint(0,3)
                    if answer == int(button.label):
                        embed = discord.Embed(title="Угадал!", color=discord.Color.green(), description="Правильная дверь: `Первая`.")
                        embed.set_footer(text=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        await interaction.edit_original_message(embeds=[embed], view=None)
                    else:
                        rightans = None
                        if answer == 2:
                            rightans = "Вторая"
                        else:
                            rightans = "Третья"
                        embed = discord.Embed(title="Не угадал!", color=discord.Color.red(), description=f"Вы нажали на `Первую` дверь.\nПравильная дверь: `{rightans}`.")
                        embed.set_footer(text=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        await interaction.edit_original_message(embeds=[embed], view=None)
                    self.value = 1
                else:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

            @discord.ui.button(label="2", emoji="🚪", style=discord.ButtonStyle.green)
            async def button_two(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if interaction.user == viewinteract.user:
                    answer = random.randint(0,3)
                    if answer == int(button.label):
                        embed = discord.Embed(title="Угадал!", color=discord.Color.green(), description="Правильная дверь: `Вторая`.")
                        embed.set_footer(text=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        await interaction.edit_original_message(embeds=[embed], view=None)
                    else:
                        rightans = None
                        if answer == 1:
                            rightans = "Первая"
                        else:
                            rightans = "Третья"
                        embed = discord.Embed(title="Не угадал!", color=discord.Color.red(), description=f"Вы нажали на `Вторую` дверь.\nПравильная дверь: `{rightans}`.")
                        embed.set_footer(text=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        await interaction.edit_original_message(embeds=[embed], view=None)
                    self.value = 2
                else:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

            @discord.ui.button(label="3", emoji="🚪", style=discord.ButtonStyle.green)
            async def button_three(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if interaction.user == viewinteract.user:
                    answer = random.randint(0,3)
                    if answer == int(button.label):
                        embed = discord.Embed(title="Угадал!", color=discord.Color.green(), description="Правильная дверь: `Третья`.")
                        embed.set_footer(text=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        await interaction.edit_original_message(embeds=[embed], view=None)
                    else:
                        rightans = None
                        if answer == 2:
                            rightans = "Вторая"
                        else:
                            rightans = "Первая"
                        embed = discord.Embed(title="Не угадал!", color=discord.Color.red(), description=f"Вы нажали на `Третью` дверь.\nПравильная дверь: `{rightans}`.")
                        embed.set_footer(text=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        await interaction.edit_original_message(embeds=[embed], view=None)
                    self.value = 3
                else:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

        view = DoorsButtons()
        embed = discord.Embed(title="Выбери дверь:", color=discord.Color.orange(), description="Для выбора нажми на одну из кнопок ниже. Время ограничено (`15` секунд).")
        embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
            return await interaction.edit_original_message(embed=embed, view=None)

    @app_commands.command(name="ball", description="[Развлечения] Магический шар.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(question="Вопрос, адресованный шару.")
    async def ball(self, interaction: discord.Interaction, question: str):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/ball`'
        answers = [
            "Бесспорно",
            "Предрешено",
            "Никаких сомнений",
            "Определённо да",
            "Можешь быть уверен в этом",
            "Мне кажется — «да»",
            "Вероятнее всего",
            "Хорошие перспективы",
            "Знаки говорят — «да»",
            "Да",
            "Пока не ясно, попробуй снова",
            "Спроси позже",
            "Лучше не рассказывать",
            "Сейчас нельзя предсказать",
            "Сконцентрируйся и спроси опять",
            "Даже не думай",
            "Мой ответ — «нет»",
            "По моим данным — «нет»",
            "Перспективы не очень хорошие",
            "Весьма сомнительно"
        ]
        embed = discord.Embed(title="Магический шар", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Ваш вопрос:", value=question, inline=False)
        embed.add_field(name="Ответ шара:", value=random.choice(answers), inline=False)
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Magic_eight_ball.png/800px-Magic_eight_ball.png")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='knb', description="[Развлечения] Камень, ножницы, бумага.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, с которым вы хотите поиграть.")
    async def knb(self, interaction: discord.Interaction, member: discord.User = None):
        config.used_commands += 1
        if member == None:
            member = self.bot.user
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/knb`'

        if interaction.user.id == member.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя играть с самим собой!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot and member.id != settings["app_id"]:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Боту не до игр, не тревожь его!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        class Approval(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accept(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user.id != member.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                self.value = True
                await viewinteract.response.edit_message(view=None)
                self.stop()

            @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red)
            async def deny(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id == viewinteract.user.id:
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Инициатор игры отменил её.")
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                elif member.id == viewinteract.user.id:
                    embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description=f"{member.mention} отказался от игры.")
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                else:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
        if member != self.bot.user:
            embed = discord.Embed(title="Камень, ножницы, бумага - Ожидание", color=discord.Color.orange(), description=f"Вы хотите сыграть с {member.mention}. Необходимо получить его/её согласие. Время на ответ: `3 минуты`.")
            embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            appr = Approval()
            await interaction.response.send_message(embed=embed, view=appr)
            await appr.wait()
        if member != self.bot.user and appr.value == None:
            embed = discord.Embed(title="Камень, ножницы, бумага - Время вышло!", color=discord.Color.red())
            return await interaction.edit_original_message(embed=embed, view=None)
        elif member == self.bot.user or appr.value:
            class GamePlay(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                    self.choice_one = None
                    self.choice_two = None
                    choices_one = ['scissors','paper', 'stone']
                    if member == interaction.client.user:
                        self.choice_two = choice(choices_one)

                @discord.ui.button(emoji="🪨", style=discord.ButtonStyle.blurple)
                async def stone(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id == viewinteract.user.id and self.choice_one == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `камень`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_one = "stone"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    elif member.id == viewinteract.user.id and self.choice_two == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `камень`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_two = "stone"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    else:
                        return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                @discord.ui.button(emoji="✂️", style=discord.ButtonStyle.blurple)
                async def scissors(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id == viewinteract.user.id and self.choice_one == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `ножницы`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_one = "scissors"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    elif member.id == viewinteract.user.id and self.choice_two == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `ножницы`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_two = "scissors"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    else:
                        return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                @discord.ui.button(emoji="📜", style=discord.ButtonStyle.blurple)
                async def paper(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id == viewinteract.user.id and self.choice_one == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `бумагу`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_one = "paper"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    elif member.id == viewinteract.user.id and self.choice_two == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `бумагу`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_two = "paper"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    else:
                        return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
            embed = discord.Embed(title="Камень, ножницы, бумага - Игра", color=discord.Color.orange(), description="Игра началась! Выберите камень, ножницы или бумагу. Время на выбор: `30 секунд`.")
            embed.set_footer(text=f"{interaction.user} и {member}", icon_url=interaction.user.display_avatar.url)
            view = GamePlay()
            if member == None:
                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.edit_original_message(embed=embed, view=view)
            await view.wait()

            if view.choice_one == None or view.choice_two == None:
                embed = discord.Embed(title="Камень, ножницы, бумага - Время вышло!", color=discord.Color.red(), description="Один из участников не выбрал(-а) предмет!")
                return await interaction.edit_original_message(embed=embed, view=None)
            else:
                choices = {
                    'scissors': "Ножницы",
                    'paper': "Бумагу",
                    'stone': 'Камень'
                }
                if view.choice_one == view.choice_two:
                    embed = discord.Embed(title="Камень, ножницы, бумага - Ничья", color=discord.Color.yellow(), description=f"{interaction.user.mention} и {member.mention} использовали `{choices[view.choice_one]}`.")
                    embed.set_footer(text="Ничья!")
                    return await interaction.edit_original_message(embed=embed, view=None)

                if view.choice_one == "paper" and view.choice_two == "stone":
                    embed = discord.Embed(title=f"Камень, ножницы, бумага - Победа {interaction.user}!", color=discord.Color.green(), description=f"{interaction.user.mention} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention} выбрал(-а) `{choices[view.choice_two]}`.")
                    embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                    await interaction.edit_original_message(embed=embed, view=None)
                if view.choice_one == "paper" and view.choice_two == "scissors":
                    embed = discord.Embed(title=f"Камень, ножницы, бумага - Победа {member}!", color=discord.Color.green(), description=f"{interaction.user.mention} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention} выбрал(-а) `{choices[view.choice_two]}`.")
                    embed.set_footer(text=str(member), icon_url=member.display_avatar.url)
                    await interaction.edit_original_message(embed=embed, view=None)
                if view.choice_one == "stone" and view.choice_two == "scissors":
                    embed = discord.Embed(title=f"Камень, ножницы, бумага - Победа {interaction.user}!", color=discord.Color.green(), description=f"{interaction.user.mention} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention} выбрал(-а) `{choices[view.choice_two]}`.")
                    embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                    await interaction.edit_original_message(embed=embed, view=None)

                if view.choice_one == "stone" and view.choice_two == "paper":
                    embed = discord.Embed(title=f"Камень, ножницы, бумага - Победа {member}!", color=discord.Color.green(), description=f"{interaction.user.mention} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention} выбрал(-а) `{choices[view.choice_two]}`.")
                    embed.set_footer(text=str(member), icon_url=member.display_avatar.url)
                    await interaction.edit_original_message(embed=embed, view=None)
                if view.choice_one == "scissors" and view.choice_two == "paper":
                    embed = discord.Embed(title=f"Камень, ножницы, бумага - Победа {interaction.user}!", color=discord.Color.green(), description=f"{interaction.user.mention} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention} выбрал(-а) `{choices[view.choice_two]}`.")
                    embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                    await interaction.edit_original_message(embed=embed, view=None)
                if view.choice_one == "scissors" and view.choice_two == "stone":
                    embed = discord.Embed(title=f"Камень, ножницы, бумага - Победа {member}!", color=discord.Color.green(), description=f"{interaction.user.mention} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention} выбрал(-а) `{choices[view.choice_two]}`.")
                    embed.set_footer(text=str(member), icon_url=member.display_avatar.url)
                    await interaction.edit_original_message(embed=embed, view=None)

    @app_commands.command(name='tic-tac-toe', description="[Развлечения] Крестики-нолики.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, с которым вы хотите поиграть.")
    async def tictac(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed = discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/tic-tac-toe`'

        if interaction.user.id == member.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(),
                                  description="Нельзя играть с самим собой!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(),
                                  description="Боту не до игр, не тревожь его!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        emb = discord.Embed(
            title="Игра в крестики-нолики!",
            description=f"{member.mention}, {interaction.user.mention} хочет с вами поиграть",
            color=discord.Color.green()
        )

        class accept(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accept(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user.id != member.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                self.value = True
                await viewinteract.response.edit_message(view=None)
                self.stop()

            @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red)
            async def deny(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id == viewinteract.user.id:
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(),
                                          description="Инициатор игры отменил её.")
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                elif member.id == viewinteract.user.id:
                    embed = discord.Embed(title="Отказ!", color=discord.Color.red(),
                                          description=f"{member.mention} отказался от игры.")
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                else:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)

        acc = accept()
        if not member.bot:
            await interaction.response.send_message(embed=emb, view=acc)
            await acc.wait()
        if acc.value == None:
            await interaction.edit_original_message(
                embed=discord.Embed(
                    title="Время вышло!",
                    color=discord.Color.red()
                ), 
                view=None
            )
        elif acc.value == True:
            class TicTacToeButton(discord.ui.Button['TicTacToe']):
                def __init__(self, x: int, y: int):
                    super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
                    self.x = x
                    self.y = y
                    self.X = interaction.user
                    self.O = member
                async def callback(self, viewinteract: discord.Interaction):
                    assert self.view is not None
                    view: TicTacToe = self.view
                    state = view.board[self.y][self.x]
                    if state in (view.X, view.O):
                        return
                    if view.current_player == view.X and viewinteract.user.id == self.X.id:
                        self.style = discord.ButtonStyle.danger
                        self.label = 'X'
                        self.disabled = True
                        view.board[self.y][self.x] = view.X
                        view.current_player = view.O
                    elif viewinteract.user.id != self.X.id and view.current_player == view.X:
                        await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                    elif view.current_player == view.O and viewinteract.user.id == self.O.id:
                        self.style = discord.ButtonStyle.success
                        self.label = 'O'
                        self.disabled = True
                        view.board[self.y][self.x] = view.O
                        view.current_player = view.X
                    elif viewinteract.user.id != self.O.id:
                        await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                    if view.current_player == view.X:
                        content = f"Теперь очередь {self.X.mention}"
                    elif view.current_player == view.O:
                        content = f"Теперь очередь {self.O.mention}"
                    else:
                        content = f"Первый ход за {self.X.mention}"

                    winner = view.check_board_winner()
                    if winner is not None:
                        if winner == view.X:
                            content = f'{self.X.mention} победил!'
                        elif winner == view.O:
                            content = f'{self.O.mention} победил!'
                        else:
                            content = "Ничья!"

                        for child in view.children:
                            child.disabled = True

                        view.stop()
                    await viewinteract.response.edit_message(content=content, view=view)

            class TicTacToe(discord.ui.View):
                children: List[TicTacToeButton]
                X = -1
                O = 1
                Tie = 2
                def __init__(self):
                    super().__init__()
                    self.current_player = self.X
                    self.board = [
                        [0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0],
                    ]
                    for x in range(3):
                        for y in range(3):
                            self.add_item(TicTacToeButton(x, y))
                def check_board_winner(self):
                    for across in self.board:
                        value = sum(across)
                        if value == 3:
                            return self.O
                        elif value == -3:
                            return self.X
                    for line in range(3):
                        value = self.board[0][line] + self.board[1][line] + self.board[2][line]
                        if value == 3:
                            return self.O
                        elif value == -3:
                            return self.X
                    diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
                    if diag == 3:
                        return self.O
                    elif diag == -3:
                        return self.X

                    diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
                    if diag == 3:
                        return self.O
                    elif diag == -3:
                        return self.X
                    if all(i != 0 for row in self.board for i in row):
                        return self.Tie
                    return None

            tictac=TicTacToe()
            await interaction.edit_original_message(embed=discord.Embed(
                title = f"Крестики-нолики",
                description=f"{interaction.user.mention} (крестик) VS {member.mention} (нолик)",
                color=discord.Color.green()),
                view=tictac
            )
    
    @app_commands.command(name="hangman", description="[Развлечения] Виселица (игра)")
    @app_commands.describe(member="Игрок, с кем вы хотите поиграть")
    @app_commands.check(is_shutted_down)
    async def hangman(self, interaction: discord.Interaction, member: discord.User):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed = discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/hangman`'

        if interaction.user.id == member.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя играть с самим собой!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Боту не до игр, не тревожь его!")
            return await interaction.response.send_message(embed=embed, ephemeral=True) 
        
        class Accept(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
                self.value = None
                self.clicker = None
            
            @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
            async def accept(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                await viewinteract.response.defer()
                self.value = True
                self.stop()
            
            @discord.ui.button(style=discord.ButtonStyle.red, emoji='<:x_icon:975324570741526568>')
            async def deny(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if member.id != viewinteract.user.id and interaction.user.id == viewinteract.user.id:
                    await viewinteract.response.defer()
                    self.value = False
                    self.clicker = interaction.user
                    self.stop()
                elif member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                else:
                    await viewinteract.response.defer()
                    self.value = False
                    self.clicker = member
                    self.stop()
        
        acc = Accept()
        embed = discord.Embed(title="Виселица - Ожидание", color=discord.Color.orange(), description=f"{member.mention}, {interaction.user.mention} хочет с вами поиграть!")
        embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=acc)
        await acc.wait()
        if acc.value == False and acc.clicker == member:
            embed = discord.Embed(title="Отказ", color=discord.Color.red(), description="Участник отказался от игры!")
            return await interaction.edit_original_message(embed=embed, view=None)
        if acc.value == False and acc.clicker == interaction.user:
            embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Инициатор игры отменил её!")
            return await interaction.edit_original_message(embed=embed, view=None)
        if acc.value == None:
            embed = discord.Embed(title="Время вышло!", color=discord.Color.red())
            return await interaction.edit_original_message(embed=embed, view=None)
        
        class Button(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=90)
            
            @discord.ui.button(label="Задать слово", style=discord.ButtonStyle.green)
            async def setword(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if viewinteract.user.id != interaction.user.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                class Input(discord.ui.Modal, title="Виселица - задать слово"):
                    ans = discord.ui.TextInput(label="Слово", max_length=35)
                    async def on_submit(self, modalinteract: discord.Interaction):
                        tryes = 0
                        symbols = []
                        fails = 0
                        word = str(self.ans).lower()
                        game = "-" * len(word)
                        hangman = "Пусто"
                        kirillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
                        for i in range(len(word)):
                            if kirillic.find(word[i]) == -1:
                                return await modalinteract.response.send_message("Строка должна содержать только кириллицу!", ephemeral=True)
                        embed = discord.Embed(
                            title="Виселица - Игра", 
                            color=discord.Color.orange(), 
                            description=f"Слово загадано!\nСлово: `{game}`.\nВиселица: `{hangman}`"
                        )

                        def man(hangman: str):
                            if hangman == "Пусто": return "ツ" 
                            if hangman == "ツ": return "(ツ)"
                            if hangman == "(ツ)": return "_(ツ)"
                            if hangman == "_(ツ)": return "_(ツ)_"
                            if hangman == "_(ツ)_": return "\_(ツ)_"
                            if hangman == "\_(ツ)_": return "\_(ツ)_/"
                            if hangman == "\_(ツ)_/": return "¯\_(ツ)_/"
                            if hangman == "¯\_(ツ)_/": return "¯\_(ツ)_/¯"

                        class Answer(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=None)
                            
                            @discord.ui.button(label="Угадать букву", style=discord.ButtonStyle.primary)
                            async def answer(self, buttinteract: discord.Interaction, button: discord.ui.Button):
                                if buttinteract.user.id != member.id:
                                    return await buttinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                                class Letter(discord.ui.Modal, title="Виселица - ответ"):
                                    ans = discord.ui.TextInput(label="Буква", max_length=1)
                                    async def on_submit(self, modinteract: discord.Interaction):
                                        nonlocal game, hangman, tryes, fails
                                        letter = str(self.ans).lower()
                                        if kirillic.find(letter) == -1:
                                            return await modinteract.response.send_message("Только кириллица!", ephemeral=True)
                                        if letter in symbols:
                                            return await modinteract.response.send_message(f"Буква `{letter}` уже была!", ephemeral=True)
                                        symbols.append(letter)
                                        tryes += 1
                                        if word.find(letter) == -1:
                                            fails += 1
                                            hangman = man(hangman=hangman)
                                            if str(hangman) == "¯\_(ツ)_/¯":
                                                embed = discord.Embed(
                                                    title="Виселица - Поражение",
                                                    color=discord.Color.red(),
                                                    description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."
                                                )
                                                return await modinteract.response.edit_message(embed=embed, view=None)
                                            embed = discord.Embed(
                                                title="Виселица - Игра",
                                                color=discord.Color.orange(),
                                                description=f"Слово: `{game}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."
                                            )
                                            await modinteract.response.edit_message(embed=embed)
                                        else:
                                            indexes = []
                                            for i in range(len(word)):
                                                if word[i] == letter:
                                                    indexes.append(i)
                                            for index in indexes:
                                                game = game[:index] + letter + game[index+1:]
                                            if game.find('-') == -1:
                                                embed = discord.Embed(
                                                    title="Виселица - Победа",
                                                    color=discord.Color.green(),
                                                    description=f"Слово: `{game}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."
                                                )
                                                return await modinteract.response.edit_message(embed=embed, view=None)
                                            embed = discord.Embed(
                                                title="Виселица - Игра", 
                                                color=discord.Color.orange(),
                                                description=f"Слово: `{game}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."
                                            )
                                            await modinteract.response.edit_message(embed=embed)
                                await buttinteract.response.send_modal(Letter())

                            @discord.ui.button(label="Ввести всё слово", style=discord.ButtonStyle.green)
                            async def enterword(self, buttinteract: discord.Interaction, button: discord.ui.Button):
                                nonlocal word
                                if buttinteract.user.id != member.id:
                                    return await buttinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                                class EnterWord(discord.ui.Modal, title="Виселица - ввод слова"):
                                    ans = discord.ui.TextInput(label="Слово:", min_length=len(word), max_length=len(word))
                                    async def on_submit(self, modinteract: discord.Interaction):
                                        nonlocal word, hangman, game, tryes, symbols, fails
                                        tryes += 1
                                        answer = str(self.ans)
                                        letters = f"\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."
                                        if symbols == []:
                                            letters = ""
                                        if answer.lower() != word:
                                            embed = discord.Embed(
                                                title="Виселица - Поражение",
                                                color=discord.Color.red(),
                                                description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.{letters}"
                                            )
                                            await modinteract.response.edit_message(embed=embed, view=None)
                                        else:
                                            embed = discord.Embed(
                                                title="Виселица - Победа",
                                                color=discord.Color.green(),
                                                description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.{letters}"
                                            )
                                            await modinteract.response.edit_message(embed=embed, view=None)
                                await buttinteract.response.send_modal(EnterWord())
                            
                            @discord.ui.button(label="Сдаться", style=discord.ButtonStyle.red)
                            async def giveup(self, buttinteract: discord.Interaction, button: discord.ui.Button):
                                if buttinteract.user.id != member.id:
                                    return await buttinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                                class Sure(discord.ui.View):
                                    def __init__(self):
                                        super().__init__(timeout=30)
                                    
                                    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
                                    async def okey(self, binteract: discord.Interaction, button: discord.ui.Button):
                                        nonlocal word, hangman, tryes, symbols
                                        if buttinteract.user.id != member.id:
                                            return await buttinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                                        letters = f"\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."
                                        if symbols == []:
                                            letters = ""
                                        embed = discord.Embed(
                                            title="Виселица - Поражение",
                                            color=discord.Color.red(),
                                            description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.{letters}"
                                        )
                                        await viewinteract.edit_original_message(embed=embed, view=None)
                                        return await binteract.response.edit_message(view=None)
                                    
                                    @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red)
                                    async def nonono(self, binteract: discord.Interaction, button: discord.ui.Button):
                                        return await binteract.response.edit_message(view=None)
                                
                                embed = discord.Embed(title="Сдаться", color=discord.Color.red(), description="Вы точно хотите сдаться?")
                                await buttinteract.response.send_message(embed=embed, view=Sure(), ephemeral=True)
                            
                        await modalinteract.response.edit_message(embed=embed, view=Answer())
                
                await viewinteract.response.send_modal(Input())
        
        embed = discord.Embed(
            title="Виселица - Задать слово", 
            color=discord.Color.orange(),
            description=f"{interaction.user.mention} должен задать слово, нажав на кнопку."
        )
        await interaction.edit_original_message(embed=embed, view=Button())
    
    @app_commands.command(name="coin", description="[Развлечения] Бросить монетку.")
    @app_commands.check(is_shutted_down)
    async def coin(self, interaction: discord.Interaction):
        config.used_commands += 1
        if interaction.user.id in blacklist:
            embed = discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/coin`'
        ans = choice(["Орёл", "Решка"])
        sel = 'a' if ans == "Решка" else ""
        embed = discord.Embed(title="Бросить монетку", color=discord.Color.orange(), description=f"Вам выпал{sel}: `{ans}`.")
        embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

            
async def setup(bot: commands.Bot):
    await bot.add_cog(Entartaiment(bot))
    print('Cog "Entartaiment" запущен!')
