# -*- coding: utf-8 -*-
import traceback
import discord
import time
import datetime
import os
import sys
import asyncio
import aiohttp

from discord import app_commands, Forbidden
from discord.ext import commands
from pypresence import Presence
from asyncio import sleep

from classes import db
from classes import checks
from cogs.bc_api import LinktoBoticord
from classes.checks import isPremium, isPremiumServer
from config import *

intents = discord.Intents.default()

btns = [
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
    RPC = Presence(f"{settings['app_id']}")  # Discord Rich Presence. Будет видно при запуске бота.
except:
    pass
else:
    RPC.connect()
    RPC.update(
        state="Бот запущен.",
        details="Работа над ботом.",
        start=time.time(),
        large_image="mad_cat_new_avatar",
        large_text="MadBot - запущен",
        buttons=btns
    )


class MyBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('mad.'), intents=intents,
                         application_id=settings['app_id'])

    async def setup_hook(self):
        for ext in cogs:
            try:
                await self.load_extension(ext)
            except Exception as err:
                print(f"Не удалось подключить {ext}!\n{err}")
                traceback.print_exc()

        await bot.tree.sync()

    async def on_connect(self):
        await bot.change_presence(
            status=discord.Status.idle, 
            activity=discord.CustomActivity(
                name="Перезагрузка..."
            )
        )
        print("Соединено! Авторизация...")

    async def on_ready(self):
        global started_at
        logs = bot.get_channel(settings['log_channel'])  # Канал логов.
        
        for guild in bot.guilds:
            if checks.is_in_blacklist(guild.id) or checks.is_in_blacklist(guild.owner_id):
                await guild.leave()
                print(f"Бот вышел из {guild.name} ({guild.id})")
        
        print(f"Авторизация успешна! {bot.user} готов к работе!")

        async def update_stats():
            db = client.stats
            coll = db.guilds
            while True:
                guilds = coll.find()
                for guild in guilds:
                    if guild['next_update'] > time.time(): continue
                    for channel_id in guild['channels']:
                        channel = self.get_channel(int(channel_id['id']))
                        if channel is None: continue
                        # if not isPremiumServer(self, channel.guild): continue
                        stat = 0
                        bots = 0
                        voices = 0
                        for voice in channel.guild.voice_channels:
                            voices += len(voice.voice_states)
                        for member in channel.guild.members:
                            if member.bot: bots += 1
                        if channel_id['type'] == 'online':
                            stat = (
                                    len(list(
                                        filter(lambda x: x.status == discord.Status.online, channel.guild.members)))
                                    + len(
                                list(filter(lambda x: x.status == discord.Status.idle, channel.guild.members)))
                                    + len(list(filter(lambda x: x.status == discord.Status.dnd, channel.guild.members)))
                            )
                        if channel_id['type'] == 'members': stat = channel.guild.member_count
                        if channel_id['type'] == 'people': stat = channel.guild.member_count - bots
                        if channel_id['type'] == 'bots': stat = bots
                        if channel_id['type'] == 'emojis': stat = len(channel.guild.emojis)
                        if channel_id['type'] == 'voice': stat = voices
                        try:
                            await channel.edit(name=channel_id['text'].replace('%count%', str(stat)))
                        except Exception as e:
                            print(e)
                    coll.update_one({'id': guild['id']}, {'$set': {'next_update': round(time.time()) + 600}})
                await sleep(1)
        
        async def remind_up():
            db = client.madbot
            coll = db.reminder
            while True:
                users = coll.find()
                for user in users:
                    if user["next_bump"] > time.time(): continue
                    if user["reminded"] or not user["enabled"]: continue
                    bc_wh = discord.Webhook.from_url(
                        settings['bc_hook_url'], 
                        session=aiohttp.ClientSession(),
                        client=self,
                        bot_token=settings['token']
                    )
                    view = LinktoBoticord(self.user.id)
                    embed = discord.Embed(
                        title="Напоминание о повышении!",
                        color=discord.Color.orange(),
                        description="Нажмите на кнопку ниже для перехода на страницу бота "
                        "либо используйте команду `/up` в <@1000051258679373914> (может не работать, "
                        "если уровень буста на Boticord ниже третьего)."
                    ).set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
                    )
                    coll.update_one(
                        {"user_id": user['user_id']},
                        {
                            "$set": {
                                'reminded': True
                            }
                        }
                    )
                    await bc_wh.send(f"<@{user['user_id']}>, время апнуть MadBot на Boticord!", embed=embed, view=view)
                await sleep(1)

        asyncio.get_running_loop().create_task(update_stats())
        asyncio.get_running_loop().create_task(remind_up())

        embed = discord.Embed(title="Бот перезапущен!", color=discord.Color.red(),
                              description=f"Пинг: `{int(round(bot.latency, 3) * 1000)}ms`\nВерсия: `{settings['curr_version']}`")
        await logs.send(embed=embed)
        while True:
            guilds_count = len(self.guilds)
            rounded_count = round(guilds_count / 1000, 1)
            irounded_count = round(guilds_count / 1000)
            for shard in range(len(self.shards)):
                try:
                    await bot.change_presence(
                        activity=discord.CustomActivity(
                            name=f"Шард {shard} | "
                            f"{rounded_count if irounded_count != rounded_count else irounded_count}k серверов"
                        ),
                        status=discord.Status.dnd, 
                        shard_id=shard
                    )
                except:
                    pass
            await sleep(60)
    
    async def is_owner(self, user: discord.User) -> bool:
        if checks.is_in_blacklist(user.id):
            return False

        return True if user.id in coders else await super().is_owner(user)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.NotOwner):
            return await ctx.reply("https://http.cat/403")
        try:
            await ctx.message.add_reaction("❌")
            message = await ctx.message.reply(content=f"```\n{error}```")
        except:
            pass
        print(error)
        await sleep(30)
        try:
            await message.delete()
            await ctx.message.delete()
        except:
            pass

    async def on_guild_join(self, guild: discord.Guild):
        if checks.is_in_blacklist(guild.id) or checks.is_in_blacklist(guild.owner_id):
            embed = discord.Embed(
                title="Данный сервер либо владелец сервера занесен(-ы) в чёрный список бота!",
                color=discord.Color.red(),
                description="Владелец бота занёс этот сервер либо его владельца в чёрный список! "
                f"Бот покинет этот сервер. Если вы считаете, что это ошибка, обратитесь в поддержку: "
                f"{settings['support_invite']}, либо напишите владельцу лично на e-mail: `madcat9958@gmail.com`.",
                timestamp=datetime.datetime.utcnow()
            ).set_thumbnail(url=guild.icon_url)
            try:
                await guild.channels[0].send(embed=embed)
            except:
                pass
            await guild.leave()
            print(f"Бот вышел из {guild.name} ({guild.id})")
        else:
            await sleep(1)
            embed = discord.Embed(title=f"Спасибо за добавление {bot.user.name} на сервер {guild.name}",
                                  color=discord.Color.orange(),
                                  description=f"Перед использованием убедитесь, что слеш-команды включены у вас на сервере. Номер сервера: `{len(bot.guilds)}`.")
            embed.add_field(name="Поддержка:", value=settings['support_invite'])
            embed.set_thumbnail(url=bot.user.avatar.url)
            """adder = None
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
                if guild.system_channel != None:
                    try:
                        await guild.system_channel.send(embed=embed)
                    except:
                        pass"""
            embed = discord.Embed(title="Новый сервер!", color=discord.Color.green())
            embed.add_field(name="Название:", value=f"`{guild.name}`")
            embed.add_field(name="Владелец:", value=f"<@{guild.owner_id}>")
            embed.add_field(name="ID сервера:", value=f"`{guild.id}`")
            if self.intents.members:
                embed.add_field(name="Кол-во участников:", value=f"`{guild.member_count}`")
            if guild.icon != None:
                embed.set_thumbnail(url=guild.icon.url)
            log_channel = bot.get_channel(settings['log_channel'])
            await log_channel.send(embed=embed)
            await bot.tree.sync()

    async def on_guild_remove(self, guild: discord.Guild):
        embed = discord.Embed(title='Минус сервер(((', color=discord.Color.red())
        embed.add_field(name="Название:", value=f"`{guild.name}`")
        embed.add_field(name="Владелец:", value=f"<@{guild.owner_id}>")
        embed.add_field(name="ID сервера:", value=f"`{guild.id}`")
        if self.intents.members:
            embed.add_field(name="Кол-во участников:", value=f"`{guild.member_count}`")
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        log_channel = bot.get_channel(settings['log_channel'])
        await log_channel.send(embed=embed)
        if isPremiumServer(self, guild):
            db.take_guild_premium(guild.id)

    async def on_member_join(self, member: discord.Member):
        if not member.bot and self.intents.members:
            role = db.get_guild_autorole(member.guild.id)
            await member.add_roles(member.guild.get_role(int(role)), reason="Автороль")


bot = MyBot()


@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = discord.Embed(
            title="Ошибка!", 
            color=discord.Color.red(),
            description=f"Задержка на команду `/{interaction.command.qualified_name}`! Попробуйте <t:{round(time.time() + error.retry_after)}:R>!"
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if isinstance(error, app_commands.CheckFailure):
        if checks.is_in_blacklist(interaction.user.id):
            blacklist_info = db.get_blacklist(interaction.user.id)
            embed = discord.Embed(
                title="Вы занесены в чёрный список бота!",
                color=discord.Color.red(),
                description=f"Разработчик бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, "
                f"обратитесь в поддержку: {settings['support_invite']}",
                timestamp=datetime.datetime.utcnow()
            ).add_field(
                name="ID разработчика:",
                value=blacklist_info['moderator_id']
            ).add_field(
                name="Причина занесения в ЧС:",
                value=blacklist_info['reason'] or "Не указана (скорее всего, ЧС выдан до обновления)"
            ).add_field(
                name="ЧС закончится:",
                value="Никогда" if blacklist_info['until'] is None else f"<t:{blacklist_info['until']}:R> (<t:{blacklist_info['until']}>)"
            ).set_thumbnail(
                url=interaction.user.avatar.url
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if checks.is_shutted_down(interaction.command.name):
            embed = discord.Embed(title="Команда отключена!", color=discord.Color.red(),
                                  description="Владелец бота временно отключил эту команду! Попробуйте позже!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    if str(error).startswith("Failed to convert"):
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(),
                              description="Данная команда недоступна в личных сообщениях!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if isinstance(error, discord.NotFound):
        return
    if isinstance(error, Forbidden):
        embed = discord.Embed(
            title="Ошибка!",
            color=discord.Color.red(),
            description="Вы видите это сообщение, потому что бот не имеет прав для совершения действия!"
        )
        try:
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            return await interaction.edit_original_response(embed=embed)
    if isinstance(error, OverflowError):
        embed = discord.Embed(
            title="Ошибка!",
            color=discord.Color.red(),
            description="Введены слишком большие числа! Введите числа поменьше!"
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if interaction.command.name == "calc" and (
        isinstance(error, (SyntaxError, KeyError))
    ):
        embed = discord.Embed(
            title="Ошибка!",
            color=discord.Color.red(),
            description="Введён некорректный пример!"
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(),
                          description=f"Произошла неизвестная ошибка! Обратитесь в поддержку со скриншотом ошибки!\n```\n{error}```",
                          timestamp=discord.utils.utcnow())
    channel = bot.get_channel(settings['log_channel'])
    await channel.send(
        f"[ОШИБКА!]: Инициатор: `{interaction.user}`\n```\nOn command '{interaction.command.name}'\n{error}```")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.edit_original_response(embeds=[embed], view=None)
    traceback.print_exception(error)


@bot.command()
async def debug(ctx: commands.Context):
    if ctx.author.id in coders or ctx.author.id == settings['owner_id']:
        class Button(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None

            @discord.ui.button(label="Показать панель", emoji="⚒️", style=discord.ButtonStyle.danger)
            async def show_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("Не для тебя кнопочка!", ephemeral=True)

                class Page1(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=300)

                    class Page2(discord.ui.View):
                        def __init__(self):
                            super().__init__(timeout=300)

                        @discord.ui.button(label="Список подключенных когов", style=discord.ButtonStyle.blurple)
                        async def cogs(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            embed = discord.Embed(title="Список подключенных когов", color=discord.Color.orange())
                            for name in bot.cogs:
                                embed.add_field(name=name, value="Запущен")
                            await viewinteract.response.send_message(embed=embed, ephemeral=True)

                        @discord.ui.button(label="Получить пользователя", style=discord.ButtonStyle.primary)
                        async def getuser(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            class Input(discord.ui.Modal, title="Debug - Получение пользователя."):
                                ans = discord.ui.TextInput(label="Ник пользователя:", max_length=32,
                                                           placeholder="Mad_Cat")

                                async def on_submit(self, modalinteract: discord.Interaction):
                                    for user in bot.users:
                                        if user.name == str(self.ans) or str(user) == str(self.ans) or str(
                                                self.ans) == str(user.id):
                                            return await modalinteract.response.send_message(
                                                f"Пользователь: `{user}`, ID: `{user.id}`", ephemeral=True)

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(label="Сколько серверов покинет бот при лимите",
                                           style=discord.ButtonStyle.blurple)
                        async def checkleaves(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            counter = 0
                            for guild in bot.guilds:
                                if guild.member_count < settings['min_members']: counter += 1
                            await viewinteract.response.send_message(f"Кол-во серверов: `{counter}`", ephemeral=True)

                        @discord.ui.button(label="Загрузить обновление", style=discord.ButtonStyle.blurple)
                        async def pull(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            os.system("git pull")
                            await viewinteract.response.send_message("Готово!", ephemeral=True)

                        @discord.ui.button(label='Дать Premium Server', style=discord.ButtonStyle.blurple)
                        async def give_premium(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            class Input(discord.ui.Modal, title="Debug - Выдача премиума"):
                                user_id = discord.ui.TextInput(label="ID пользователя", min_length=18, max_length=19)

                                async def on_submit(self, modalinteract: discord.Interaction):
                                    if isPremium(bot, int(str(self.user_id))) != 'None':
                                        return await modalinteract.response.send_message(
                                            "У пользователя уже есть премиум!", ephemeral=True)
                                    db.give_premium(user_id=str(self.user_id), type="server")
                                    await modalinteract.response.send_message("Успешно!", ephemeral=True)

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(label='Дать Premium User')
                        async def give_user_premium(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            class Input(discord.ui.Modal, title="Debug - Выдача премиума"):
                                user_id = discord.ui.TextInput(label="ID пользователя", min_length=18, max_length=19)

                                async def on_submit(self, modalinteract: discord.Interaction):
                                    if isPremium(bot, int(str(self.user_id))) != 'None':
                                        return await modalinteract.response.send_message(
                                            "У пользователя уже есть премиум!", ephemeral=True)
                                    db.give_premium(user_id=str(self.user_id), type="user")
                                    await modalinteract.response.send_message("Успешно!", ephemeral=True)

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(label='Забрать Premium')
                        async def take_premium(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            class Input(discord.ui.Modal, title="Debug - Выдача премиума"):
                                user_id = discord.ui.TextInput(label="ID пользователя", min_length=18, max_length=19)

                                async def on_submit(self, modalinteract: discord.Interaction):
                                    if isPremium(bot, int(str(self.user_id))) == 'None':
                                        return await modalinteract.response.send_message("У пользователя нет премиума!",
                                                                                         ephemeral=True)
                                    db.take_premium(user_id=str(self.user_id))
                                    await modalinteract.response.send_message("Успешно!", ephemeral=True)

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.primary, row=2)
                        async def prevpage(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            await viewinteract.response.edit_message(view=Page1())

                    @discord.ui.button(label="Сервера", style=discord.ButtonStyle.primary)
                    async def servers(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        servernames = []
                        gnames = " "
                        for guild in bot.guilds:
                            servernames.append(guild.name)
                        for name in servernames:
                            gnames += f"`{name}`, "
                        await viewinteract.response.send_message(f"Сервера: {gnames}", ephemeral=True)

                    @discord.ui.button(label="Получить сервер", style=discord.ButtonStyle.primary)
                    async def getserver(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - получение сервера"):
                            ans = discord.ui.TextInput(label="Название/ID сервера:", max_length=100, min_length=2)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                for guild in bot.guilds:
                                    if str(self.ans) == guild.name:
                                        return await modalinteract.response.send_message(
                                            f"Название: {guild.name}, владелец: {guild.owner.mention}, ID: {guild.id}, участников: {guild.member_count}",
                                            ephemeral=True)
                                    try:
                                        if int(str(self.ans)) == guild.id:
                                            return await modalinteract.response.send_message(
                                                f"Название: {guild.name}, владелец: {guild.owner.mention}, ID: {guild.id}, участников: {guild.member_count}",
                                                ephemeral=True)
                                    except:
                                        pass

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Выгрузка кога", style=discord.ButtonStyle.blurple)
                    async def unloadcog(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - выгрузка кога"):
                            ans = discord.ui.TextInput(label="Название кога:", max_length=64, placeholder="tools")

                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    await bot.unload_extension(f'cogs.{str(self.ans)}')
                                except Exception as e:
                                    return await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                await bot.tree.sync()
                                await modalinteract.response.send_message(f"Ког {str(self.ans)} выгружен!",
                                                                          ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="В черный список", style=discord.ButtonStyle.primary)
                    async def addblacklist(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - в чёрный список"):
                            ans = discord.ui.TextInput(label="ID участника/сервера:", min_length=18, max_length=19)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                if not db.add_blacklist(
                                    int(str(self.ans)),
                                    modalinteract.user.id,
                                    None,
                                    None
                                ):
                                    return await modalinteract.response.send_message(
                                        f"Ресурс с ID `{int(str(self.ans))}` уже занесён в ЧС!",
                                        ephemeral=True
                                    )
                                guild = bot.get_guild(int(str(self.ans)))
                                if guild != None:
                                    embed = discord.Embed(title="Ваш сервер занесён в чёрный список бота!",
                                                          color=discord.Color.red(),
                                                          description=f"Владелец бота занёс ваш сервер в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка: обратитесь в поддержку: {settings['support_invite']}",
                                                          timestamp=datetime.datetime.utcnow())
                                    embed.set_thumbnail(url=guild.icon_url)
                                    db.add_blacklist(
                                        guild.owner.id,
                                        modalinteract.user.id,
                                        f"Владелец сервера с ID {guild.id}, который занесён в чёрный список",
                                        None
                                    )
                                    try:
                                        await guild.owner.send(embed=embed)
                                    except:
                                        pass
                                    await guild.leave()
                                await modalinteract.response.send_message(f"`{str(self.ans)}` занесен в черный список!",
                                                                          ephemeral=True)
                                await sleep(30)
                                if int(str(self.ans)) == settings['owner_id']:
                                    db.remove_blacklist(settings['owner_id'])

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Верифицировать", style=discord.ButtonStyle.primary)
                    async def verify(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - верификация"):
                            ans = discord.ui.TextInput(label="ID участника/сервера:", min_length=18, max_length=19)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                verified.append(int(str(self.ans)))
                                await modalinteract.response.send_message(f"`{str(self.ans)}` верифицирован(-а)",
                                                                          ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Выдать значок саппорта",
                                       disabled=not (ctx.author.id == settings['owner_id']))
                    async def support(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - в саппорты"):
                            ans = discord.ui.TextInput(label="ID участника:", min_length=18, max_length=19)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                supports.append(int(str(self.ans)))
                                await modalinteract.response.send_message(f"`{str(self.ans)}` теперь - саппорт",
                                                                          ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Добавить кодера", disabled=not (ctx.author.id == settings['owner_id']))
                    async def coder(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - в кодеры"):
                            ans = discord.ui.TextInput(label="ID участника:", min_length=18, max_length=19)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                coders.append(int(str(self.ans)))
                                await modalinteract.response.send_message(f"`{str(self.ans)}` теперь - кодер",
                                                                          ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Черный список")
                    async def blacklist(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message(
                            f"Забаненные: {', '.join(i['resource_id'] for i in db.get_all_blacklist())}", 
                            ephemeral=True
                        )

                    @discord.ui.button(label="Убрать из ЧС")
                    async def removeblacklist(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - убрать из ЧС"):
                            ans = discord.ui.TextInput(label="ID участника/сервера:", min_length=18, max_length=19)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                db.remove_blacklist(int(str(self.ans)))
                                await modalinteract.response.send_message(f"`{str(self.ans)}` вынесен(-а) из ЧС!", ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Покинуть сервер", disabled=not (ctx.author.id == settings['owner_id']))
                    async def leaveserver(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - выход из сервера"):
                            ans = discord.ui.TextInput(label="ID сервера:", max_length=19, min_length=18)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                guild = await bot.fetch_guild(int(str(self.ans)))
                                if guild == None:
                                    return await modalinteract.response.send_message("Сервер не обнаружен!",
                                                                                     ephemeral=True)
                                await guild.leave()
                                await modalinteract.response.send_message(f"Бот вышел с {guild.name}!", ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Синхронизация команд", style=discord.ButtonStyle.green)
                    async def sync(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message("Синхронизация...", ephemeral=True)
                        await bot.tree.sync()
                        await viewinteract.edit_original_response(content="Команды синхронизированы!")

                    @discord.ui.button(label='Смена ника', style=discord.ButtonStyle.green,
                                       disabled=not (ctx.author.id == settings['owner_id']))
                    async def changename(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - смена ника"):
                            ans = discord.ui.TextInput(label="Новый ник:", min_length=2, max_length=32)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    await bot.user.edit(username=str(self.ans))
                                except Exception as e:
                                    await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                else:
                                    await modalinteract.response.send_message("Ник бота изменен!", ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Начать печатать", style=discord.ButtonStyle.green)
                    async def starttyping(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - печатание"):
                            ans = discord.ui.TextInput(label="Кол-во секунд", max_length=4)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                await modalinteract.response.send_message(
                                    f"Начинаем печатать {str(self.ans)} секунд...", ephemeral=True)
                                async with modalinteract.channel.typing():
                                    await sleep(int(str(self.ans)))

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Выполнить команду", style=discord.ButtonStyle.green,
                                       disabled=not (ctx.author.id == settings['owner_id']))
                    async def sudo(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - выполнение команды"):
                            ans = discord.ui.TextInput(label="Команда:", style=discord.TextStyle.long)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    exec(str(self.ans))
                                except Exception as e:
                                    return await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                await modalinteract.response.send_message("Команда выполнена!", ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Перезапустить", style=discord.ButtonStyle.green)
                    async def restart(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message("Перезапускаемся...", ephemeral=True)
                        print(f"{viewinteract.user} инициировал перезагрузку!")
                        await bot.change_presence(status=discord.Status.idle,
                                                  activity=discord.Game(name="Перезагрузка..."))
                        await sleep(2)
                        os.execv(sys.executable, ['python'] + sys.argv)

                    @discord.ui.button(label="Выключить", style=discord.ButtonStyle.danger,
                                       disabled=not (ctx.author.id == settings['owner_id']))
                    async def stop(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message("Выключение...", ephemeral=True)
                        await bot.change_presence(status=discord.Status.idle,
                                                  activity=discord.Game(name="Выключение..."))
                        await sleep(2)
                        quit()

                    @discord.ui.button(label="Отключить команду", style=discord.ButtonStyle.red)
                    async def offcmd(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - отключение команды"):
                            ans = discord.ui.TextInput(label="Команда:", max_length=32)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                if not db.add_shutted_command(str(self.ans)):
                                    return await modalinteract.response.send_message(
                                        f"Команда `{str(self.ans)}` уже отключена!",
                                        ephemeral=True
                                    )
                                await modalinteract.response.send_message(f"Команда `{str(self.ans)}` отключена!",
                                                                          ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Включить команду", style=discord.ButtonStyle.red)
                    async def oncmd(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - включение команды"):
                            ans = discord.ui.TextInput(label="Команда:", max_length=32)

                            async def on_submit(self, modalinteract: discord.Interaction):
                                db.remove_shutted_command(str(self.ans))
                                await modalinteract.response.send_message(f"Команда `{str(self.ans)}` включена!",
                                                                          ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Перезагрузка когов", style=discord.ButtonStyle.red)
                    async def reloadcogs(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        for ext in cogs:
                            try:
                                await bot.reload_extension(ext)
                            except Exception as e:
                                print(f"Не удалось перезагрузить {ext}!\n{e}")
                        await bot.tree.sync()
                        await viewinteract.response.send_message("Коги перезапущены!", ephemeral=True)

                    @discord.ui.button(label="Загрузка кога", style=discord.ButtonStyle.red)
                    async def loadcog(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - загрузка кога"):
                            ans = discord.ui.TextInput(label="Название кога:", max_length=64, placeholder="tools")

                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    await bot.load_extension(f'cogs.{str(self.ans)}')
                                except Exception as e:
                                    return await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                await bot.tree.sync()
                                await modalinteract.response.send_message(f"Ког {str(self.ans)} загружен!",
                                                                          ephemeral=True)

                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple)
                    async def nextpage(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.edit_message(view=self.Page2())

                embed = discord.Embed(
                    title="Панель:",
                    color=discord.Color.orange(),
                    description="Отключенные кнопки вам недоступны, однако доступны для владельца. Наслаждайтесь!"
                )
                await interaction.response.send_message(embed=embed, view=Page1(), ephemeral=True)
                await ctx.message.delete()
                view.stop()

            @discord.ui.button(label="Отмена", style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>")
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await ctx.message.delete()
                view.stop()

        view = Button()
        message = await ctx.reply("Для показа панели нажмите на кнопку.", view=view)
        await view.wait()
        await message.delete()
    elif not checks.is_in_blacklist(ctx.author.id):
        embed = discord.Embed(title="Попытка использования debug-команды!", color=discord.Color.red())
        embed.add_field(name="Пользователь:", value=f'{ctx.author.mention} (`{ctx.author}`)')
        channel = bot.get_channel(settings['log_channel'])
        await channel.send(embed=embed)

print("Подключение к Discord...")
bot.run(settings['token'])
