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
from asyncio import sleep
import discord, datetime, requests, random
from hmtai import useHM
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
import config
from config import *

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
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.PartialMessageable):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/knb`'

        if member != None and interaction.user.id == member.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя играть с самим собой!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member != None and member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Боту не до игр, не тревожь его!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        class Approval(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None
            
            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accept(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if member != None and viewinteract.user.id != member.id:
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
                elif member != None and member.id == viewinteract.user.id:
                    embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description=f"{member.mention} отказался от игры.")
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                else:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
        if member != None:
            embed = discord.Embed(title="Камень, ножницы, бумага - Ожидание", color=discord.Color.orange(), description=f"Вы хотите сыграть с {member.mention}. Необходимо получить его/её согласие. Время на ответ: `3 минуты`.")
            embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            appr = Approval()
            await interaction.response.send_message(embed=embed, view=appr)
            await appr.wait()
        if member != None and appr.value == None:
            embed = discord.Embed(title="Камень, ножницы, бумага - Время вышло!", color=discord.Color.red())
            return await interaction.edit_original_message(embed=embed, view=None)
        elif member == None or appr.value == True:
            class GamePlay(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                    self.choice_one = None
                    self.choice_two = None
                    choices_one = ['scissors','paper', 'stone']
                    if member == None:
                        self.choice_two = random.choice(choices_one)
                
                @discord.ui.button(emoji="🪨", style=discord.ButtonStyle.blurple)
                async def stone(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id == viewinteract.user.id and self.choice_one == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `камень`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_one = "stone"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    elif member != None and member.id == viewinteract.user.id and self.choice_two == None:
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
                    elif member != None and member.id == viewinteract.user.id and self.choice_two == None:
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
                    elif member != None and member.id == viewinteract.user.id and self.choice_two == None:
                        embed = discord.Embed(title="Выбор", color=discord.Color.green(), description="Вы выбрали `бумагу`, ожидайте итогов.")
                        await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        self.choice_two = "paper"
                        if self.choice_one != None and self.choice_two != None:
                            self.stop()
                    else:
                        return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
            
            bot_mention = "<@!{settings['app_id']}>"
            gamer = member if member != None else interaction.client.user
            embed = discord.Embed(title="Камень, ножницы, бумага - Игра", color=discord.Color.orange(), description="Игра началась! Выберите камень, ножницы или бумагу. Время на выбор: `30 секунд`.")
            embed.set_footer(text=f"{interaction.user} и {gamer}", icon_url=interaction.user.display_avatar.url)
            view = GamePlay()
            member = interaction.client.user
            await interaction.response.send_message(embed=embed, view=view)
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
                    embed = discord.Embed(title=f"Камень, ножницы, бумага - Победа {interaction.user}!", color=discord.Color.green(), description=f"{interaction.user.mention} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention if member == None else bot_mention} выбрал(-а) `{choices[view.choice_two]}`.")
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

async def setup(bot: commands.Bot):
    await bot.add_cog(Entartaiment(bot))
    print('Cog "Entartaiment" запущен!')