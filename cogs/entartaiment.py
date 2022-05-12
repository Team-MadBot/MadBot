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
    """
    @app_commands.context_menu(name="Обнять")
    @app_commands.check(is_shutted_down)
    async def context_hug(interaction: discord.Interaction, member: discord.Member):
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
    """
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
    """
    @app_commands.context_menu(name="Погладить")
    @app_commands.check(is_shutted_down)
    async def context_pat(interaction: discord.Interaction, member: discord.Member):
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
    """
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
    """
    @app_commands.context_menu(name="Подмигнуть")
    @app_commands.check(is_shutted_down)
    async def context_wink(interaction: discord.Interaction, member: discord.Member):
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
    """
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
        def check(reaction, user):
            return user == member and reaction.message.author == self.bot.user and (reaction.emoji == "❌" or reaction.emoji == "✅")
        embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
        await interaction.response.send_message(embed=embed)
        bot_message = await interaction.original_message()
        await bot_message.add_reaction("✅")
        await bot_message.add_reaction("❌")
        try:
            reactions = await self.bot.wait_for("reaction_add", check=check, timeout=120)
        except TimeoutError:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red(), description="Участник не ответил на предложение о поцелуе.")
            return await interaction.edit_original_message(embed=embed)
        else:
            if str(reactions).startswith("(<Reaction emoji='❌'"):
                embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
                await bot_message.clear_reactions()
                return await interaction.edit_original_message(embed=embed)
        embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=f"{interaction.user.mention} поцеловал(-а) {member.mention}.")
        embed.set_image(url=random.choice(kiss_gifs))
        await bot_message.clear_reactions()
        await interaction.edit_original_message(embed=embed)
    """
    @app_commands.context_menu(name="Поцеловать")
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
        def check(reaction, user):
            return user == member and reaction.message.author == self.bot.user and (reaction.emoji == "❌" or reaction.emoji == "✅")
        embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
        await interaction.response.send_message(embed=embed)
        bot_message = await interaction.original_message()
        await bot_message.add_reaction("✅")
        await bot_message.add_reaction("❌")
        try:
            reactions = await self.bot.wait_for("reaction_add", check=check, timeout=120)
        except TimeoutError:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red(), description="Участник не ответил на предложение о поцелуе.")
            return await interaction.edit_original_message(embed=embed)
        else:
            if str(reactions).startswith("(<Reaction emoji='❌'"):
                embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
                await bot_message.clear_reactions()
                return await interaction.edit_original_message(embed=embed)
        embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=f"{interaction.user.mention} поцеловал(-а) {member.mention}.")
        embed.set_image(url=random.choice(kiss_gifs))
        await bot_message.clear_reactions()
        await interaction.edit_original_message(embed=embed)
    """
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
    """
    @app_commands.context_menu(name="Ударить")
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
    """
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
        embed = discord.Embed(title="Реши пример!", color=discord.Color.orange(), description=f"`{tosolve}`")
        embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        start = time.time()
        def check(m):
            isint = False
            try:
                temp = int(m.content)
            except:
                isint = False
            else:
                isint = True
            return interaction.user.id == m.author.id and isint
        try:
            ans = await self.bot.wait_for("message", check=check, timeout=15)
        except TimeoutError:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red(), description=f"Правильный ответ: `{answer}`.")
            embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            message = await interaction.original_message()
            await message.reply(embed=embed)
        else:
            if int(ans.content) == int(answer):
                wasted = time.time() - start
                embed = discord.Embed(title="Правильно!", color=discord.Color.green(), description=f"Ответ: `{answer}`. Время ответа: `{round(wasted, 3)}s`.")
                embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                await ans.reply(embed=embed)
            else:
                embed = discord.Embed(title="Неправильно!", color=discord.Color.red(), description=f"Правильный ответ: `{answer}`")
                embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                await ans.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Entartaiment(bot))
    print('Cog "Entartaiment" запущен!')