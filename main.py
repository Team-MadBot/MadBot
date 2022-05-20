# -*- coding: utf-8 -*-
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
import discord, time, datetime, os, sys
from discord import app_commands, Forbidden, NotFound
from pypresence import Presence
from discord.ext import commands
from asyncio import sleep
from config import *

btns=[
    {
        "label": "Добавить бота",
        "url": f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands"
    },
    {
        "label": "Поддержка бота",
        "url": settings['support_invite']
    }
]
try:
    RPC = Presence(f"{settings['app_id']}") # Discord Rich Presence. Будет видно при запуске бота.
except:
    pass
else:
    try:
        RPC.connect()
    except:
        pass
    else:
        RPC.update(
            state=f"Бот запущен.",
            details="Работа над ботом.",
            start=time.time(),
            large_image="mad_cat_default",
            large_text="MadBot - запущен",
            buttons=btns
        )

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='mad.', intents=discord.Intents.all(), application_id=settings['app_id'])

    async def setup_hook(self):
        for ext in cogs:
            try:
                await self.load_extension(ext)
            except:
                print(f"Не удалось подключить {ext}!")
        
        await bot.tree.sync()
    
    async def on_connect(self):
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Перезагрузка..."))
        print("Соединено! Авторизация...")

    async def on_ready(self):
        global started_at
        server = bot.get_guild(settings['server']) # Сервер логов.
        logs = server.get_channel(settings['log_channel']) # Канал логов.
        channel = bot.get_channel(967484036127813713) # Канал "общения" мониторинга. Закомментируйте, если хотите.
        for guild in bot.guilds: # Проверка на нахождение в чёрном списке.
            if guild.id in blacklist:
                await guild.leave()
                print(f"Бот вышел из {guild.name} ({guild.id})")
        print(f"Авторизация успешна! {bot.user} готов к работе!")
        if round(bot.latency, 3)*1000 < 90:
            started_at -= 10800
        embed = discord.Embed(title="Бот перезапущен!", color=discord.Color.red(), description=f"Пинг: `{int(round(bot.latency, 3)*1000)}ms`\nВерсия: `{settings['curr_version']}`")
        await logs.send(embed=embed)
        await channel.send("OK") # Канал "общения" мониторинга. Закомментируйте, если хотите.
        while True:
            await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} серверов | {int(round(bot.latency, 3)*1000)}ms"))
            await sleep(60)
            await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} серверов | v{settings['curr_version']}"))
            await sleep(60)
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        try:
            await ctx.message.add_reaction("❌")
            message = await ctx.message.reply(content=f"```\n{error}```")
        except:
            pass
        channel = bot.get_channel(settings['log_channel'])
        await channel.send(f'```\nOn message "{ctx.message.content}"\n\n{error}```')
        print(error)
        await sleep(30)
        try:
            await message.delete()
            await ctx.message.delete()
        except:
            pass
    
    async def on_guild_join(self, guild: discord.Guild):
        if guild.id in blacklist or guild.owner.id in blacklist: # Проверка на чёрный список.
            embed=discord.Embed(title="Ваш сервер либо вы сами занесён(-ы) в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс ваш сервер либо вас в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=guild.icon_url)
            try:
                await guild.owner.send(embed=embed)
            except:
                pass
            await guild.leave()
            print(f"Бот вышел из {guild.name} ({guild.id})")
        else: 
            await sleep(1)
            embed = discord.Embed(title=f"Спасибо за добавление {bot.user.name} на сервер {guild.name}", color=discord.Color.orange(), description=f"Перед использованием убедитесь, что слеш-команды включены у вас на сервере. Ваш сервер: `{len(bot.guilds)}-ый`.")
            embed.add_field(name="Поддержка:", value=settings['support_invite'])
            embed.set_thumbnail(url=bot.user.avatar.url)
            adder = None
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
                    if entry.target.id == bot.user.id:
                        adder = entry.user
            except Forbidden:
                adder = guild.owner
                embed.set_footer(text="Бот написал вам, так как не смог уточнить, кто его добавил.")
            try:
                await adder.send(embed=embed)
            except:
                pass
            embed = discord.Embed(title="Новый сервер!", color=discord.Color.green())
            embed.add_field(name="Название:", value=f"`{guild.name}`")
            embed.add_field(name="Владелец:", value=f"{guild.owner.mention}")
            embed.add_field(name="ID сервера:", value=f"`{guild.id}`")
            embed.add_field(name="Кол-во участников:", value=f"`{guild.member_count}`")
            try:
                embed.set_thumbnail(url=guild.icon.url)
            except:
                pass
            log_channel = bot.get_channel(settings['log_channel'])
            await log_channel.send(embed=embed)
            await bot.tree.sync()
    

bot=MyBot()

@bot.tree.error
async def on_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        embed = discord.Embed(title="Команда отключена!", color=discord.Color.red(), description="Владелец бота временно отключил эту команду! Попробуйте позже!")
        return await interaction.response.send_message(embed=embed, ephemeral=True) 
    if str(error).startswith("Failed to convert"):
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Данная команда недоступна в личных сообщениях!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Произошла неизвестная ошибка! Обратитесь в поддержку со скриншотом ошибки!\n```\n{error}```", timestamp=discord.utils.utcnow())
    channel = bot.get_channel(settings['log_channel'])
    await channel.send(f"```\nOn command '{interaction.command.name}'\n{error}```")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.edit_original_message(embeds=[embed])
    print(error)

@bot.command()
async def debug(ctx, argument, *, arg1 = None):
    if ctx.author.id == settings['owner_id']:
        if argument == "help":
            message = await ctx.send(f"```\nservers - список серверов бота\nserverid [ID] - узнать о сервере при помощи его ID\nservername [NAME] - узнать о сервере по названию\ncreateinvite [ID] - создать инвайт на сервер\naddblacklist [ID] - добавить в ЧС\nremoveblacklist [ID] - убрать из ЧС\nverify [ID] - выдать галочку\nsupport [ID] - дать значок саппорта\nblacklist - список ЧСников\nleaveserver [ID] - покинуть сервер\nsync - синхронизация команд приложения\nchangename [NAME] - поменять ник бота\nstarttyping [SEC] - начать печатать\nsetavatar [AVA] - поменять аватар\nrestart - перезагрузка\ncreatetemplate - Ctrl+C Ctrl+V сервер\noffcmd - отключение команды\noncmd - включение команды\nreloadcogs - перезагрузка cog'ов\nloadcog - загрузка cog'а\nunloadcog - выгрузка cog'a\nsudo - запуск кода```")
            await message.delete(delay=60)
        if argument == "servers":
            servernames = []
            gnames = " "
            for guild in bot.guilds:
                servernames.append(guild.name)
            for name in servernames:
                gnames += f"`{name}`, "
            await ctx.send(f"Servers: {gnames}", delete_after=120)
        if argument == "serverid":
            try:
                guild = await bot.fetch_guild(int(arg1))
            except NotFound:
                await ctx.message.add_reaction("❌")
                await sleep(30)
            await ctx.send(f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}", delete_after=120)
        if argument == "servername":
            for guild in bot.guilds:
                if str(arg1) == guild.name:
                    await ctx.send(f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}", delete_after=120)
        if argument == "createinvite":
            for guild in bot.guilds:
                if guild.id == int(arg1):
                    for channel in guild.text_channels:
                        invite = await channel.create_invite(max_age=30, reason="Запрос")
                        await ctx.send(invite.url, delete_after=30)
                        return await ctx.message.delete()
        if argument == "addblacklist":
            blacklist.append(int(arg1))
            guild = bot.get_guild(int(arg1))
            if guild != None:
                embed=discord.Embed(title="Ваш сервер занесён в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс ваш сервер в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка: обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
                embed.set_thumbnail(url=guild.icon_url)
                blacklist.append(guild.owner.id)
                try:
                    await guild.owner.send(embed=embed)
                except:
                    pass
                await guild.leave()
            await ctx.message.add_reaction("✅")
            await sleep(30)
            if int(arg1) == settings['owner_id']:
                blacklist.remove(int(arg1))
        if argument == "verify":
            verified.append(int(arg1))
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "support":
            supports.append(int(arg1))
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "blacklist":
            await ctx.send(f"Banned: {blacklist}", delete_after=60)
        if argument == "removeblacklist":
            try:
                blacklist.remove(int(arg1))
            except ValueError:
                await ctx.message.add_reaction("❌")
            else:
                await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "leaveserver":
            guild = bot.get_guild(int(arg1))
            await guild.leave()
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "sync":
            async with ctx.channel.typing():    
                await bot.tree.sync()
                await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "changename":
            await bot.user.edit(username=arg1)
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "starttyping":
            await ctx.message.delete()
            async with ctx.channel.typing():
                await sleep(int(arg1))
        if argument == "createtemplate":
            try:
                template = await ctx.guild.create_template(name="Повiстка")
            except:
                template = ctx.guild.templates
                for templ in template:
                    template = templ
                    break
            owner = ctx.guild.get_member(settings['owner_id'])
            await owner.send(template.url)
        if argument == "restart":
            await ctx.message.add_reaction("🔁")
            await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Перезагрузка..."))
            await sleep(2)
            os.execv(sys.executable, ['python'] + sys.argv)
        if argument == "setavatar":
            bot_avatar = None
            for attachment in ctx.message.attachments:
                bot_avatar = await attachment.read()
            await bot.user.edit(avatar=bot_avatar)
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "stop":
            await ctx.message.add_reaction("🔁")
            await bot.close()
        if argument == "offcmd":
            shutted_down.append(arg1)
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "oncmd":
            shutted_down.remove(arg1)
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "reloadcogs":
            for ext in cogs:
                try:
                    await bot.reload_extension(ext)
                except:
                    print(f"Не удалось перезагрузить {ext}!")
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "loadcog":
            try:
                await bot.load_extension(f'cogs.{arg1}')
            except:
                await ctx.message.add_reaction("❌")
            else:
                await ctx.message.add_reaction("✅")
                await bot.tree.sync()
            await sleep(30)
        if argument == "unloadcog":
            try:
                await bot.unload_extension(f"cogs.{arg1}")
            except:
                await ctx.message.add_reaction("❌")
            else:
                await ctx.message.add_reaction("✅")
                await bot.tree.sync()
            await sleep(30)
        if argument == "sudo":
            exec(arg1)
            await ctx.message.add_reaction("✅")
            await sleep(30)
    await ctx.message.delete()

print("Подключение к Discord...")
bot.run(settings['token'])
