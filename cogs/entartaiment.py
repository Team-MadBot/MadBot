from asyncio import sleep
import discord, datetime, requests, random
from hmtai import useHM
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from config_example import *

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
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/cat`'
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
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/dog`'
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
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/hug`'
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
    async def context_hug(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/hug`'
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
    async def pat(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/pat`'
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
    async def context_pat(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/pat`'
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
    async def wink(self, interaction: discord.Interaction, member: discord.Member = None):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/wink`'
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
    async def context_wink(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/wink`'
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
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/slap`'
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
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/kiss`'
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
    async def context_kiss(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/kiss`'
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
    async def hit(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/hit`'
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
    async def context_hit(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/hit`'
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
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/nsfw`'
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
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/math`'
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
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/doors`'

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Entartaiment(bot))
    print('Cog "Entartaiment" запущен!')