# -*- coding: utf-8 -*-
import traceback
import discord
import datetime
import os
import argparse
import logging
import config

from discord.ext import commands
from asyncio import sleep
from contextlib import suppress
from logging.handlers import RotatingFileHandler

from classes import db
from classes import checks
from classes.checks import isPremiumServer


logging.getLogger("discord").addHandler(RotatingFileHandler(
    filename="discord.log",
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,
    backupCount=10,
))

intents = discord.Intents.default()
logger = logging.getLogger('discord')

class MyBot(commands.AutoShardedBot):
    def __init__(self, migrate_db: bool = False):
        super().__init__(
            command_prefix=commands.when_mentioned_or('mad.'), 
            intents=intents,
            application_id=config.settings['app_id']
        )
        self.migrate_db = migrate_db
    
    async def load_cogs(self):
        for path, _, files in os.walk('cogs'):
            for file in files:
                if not file.endswith(".py"): continue
                egg = os.path.join(path, file)
                if egg in config.cogs_ignore: continue
                try:
                    await self.load_extension(egg.replace(os.sep, '.')[:-3])
                except commands.NoEntryPointError:
                    pass # сделать логирование для debug режима (потому что можно обосраться и гадать часами, почему ког не загружается)
                except Exception as e:
                    logger.error(f"При загрузке модуля {egg} произошла ошибка: {e}")
                    logger.error(traceback.format_exc())

    async def setup_hook(self):
        with suppress(commands.NoEntryPointError):
            await self.load_extension('jishaku')
        await self.load_cogs()

    async def on_connect(self):
        await bot.change_presence(
            status=discord.Status.idle, 
            activity=discord.CustomActivity(
                name="Перезагрузка..."
            )
        )
        logger.info("Соединено! Авторизация...")

    async def on_ready(self):
        global started_at
        logs = self.get_channel(config.settings['log_channel'])  # Канал логов.
        assert isinstance(logs, discord.TextChannel)
        
        for guild in self.guilds:
            assert guild.owner_id is not None
            if checks.is_in_blacklist(guild.id) or checks.is_in_blacklist(guild.owner_id):
                await guild.leave()
                logger.info(f"Бот вышел из {guild.name} ({guild.id})")
        
        logger.info(f"Авторизация успешна! {self.user} готов к работе!")

        embed = discord.Embed(
            title="Бот перезапущен!", 
            color=discord.Color.red(),
            description=f"Пинг: `{int(round(self.latency, 3) * 1000)}ms`\n"
            f"Версия: `{config.settings['curr_version']}`"
        )
        await logs.send(embed=embed)
    
    async def is_owner(self, user: discord.User) -> bool:
        if checks.is_in_blacklist(user.id):
            return False

        return True if user.id in config.coders else await super().is_owner(user)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.NotOwner):
            return await ctx.reply("https://http.cat/403")
        with suppress(Exception):
            await ctx.message.add_reaction("❌")
            await ctx.message.reply(content=f"```\n{error}```", delete_after=30)
            await ctx.message.delete(delay=30)
        logger.error(error)

    async def on_guild_join(self, guild: discord.Guild):
        assert guild.owner_id is not None
        if checks.is_in_blacklist(guild.id) or checks.is_in_blacklist(guild.owner_id):
            embed = discord.Embed(
                title="Данный сервер либо владелец сервера занесен(-ы) в чёрный список бота!",
                color=discord.Color.red(),
                description="Владелец бота занёс этот сервер либо его владельца в чёрный список! "
                f"Бот покинет этот сервер. Если вы считаете, что это ошибка, обратитесь в поддержку: "
                f"{config.settings['support_invite']}, либо напишите владельцу лично на e-mail: `madcat9958@gmail.com`.",
                timestamp=datetime.datetime.now()
            ).set_thumbnail(url=guild.icon.url if guild.icon is not None else None)
            with suppress(Exception):
                await [c for c in guild.channels if isinstance(c, discord.TextChannel)][0].send(embed=embed)
            await guild.leave()
            logger.info(f"Бот вышел из {guild.name} ({guild.id})")
        else:
            await sleep(1)
            assert bot.user is not None
            assert bot.user.avatar is not None
            embed = discord.Embed(title=f"Спасибо за добавление {bot.user.name} на сервер {guild.name}",
                                  color=discord.Color.orange(),
                                  description=f"Перед использованием убедитесь, что слеш-команды включены у вас на сервере. Номер сервера: `{len(bot.guilds)}`.")
            embed.add_field(name="Поддержка:", value=config.settings['support_invite'])
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
            log_channel = bot.get_channel(config.settings['log_channel'])
            assert isinstance(log_channel, discord.TextChannel)
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
        log_channel = bot.get_channel(config.settings['log_channel'])
        assert isinstance(log_channel, discord.TextChannel)
        await log_channel.send(embed=embed)
        if isPremiumServer(self, guild):
            db.take_guild_premium(guild.id)

    async def on_member_join(self, member: discord.Member):
        if not member.bot and self.intents.members:
            role = db.get_guild_autorole(member.guild.id)
            assert role is not None
            autorole = member.guild.get_role(role)
            assert autorole is not None
            await member.add_roles(autorole, reason="Автороль")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug-mode",
        help="Should bot run with logging.DEBUG level?",
        action="store_true",
        default=False,
        dest="debug_mode"
    )
    parser.add_argument(
        "--migrate-db",
        help="Should bot migrate DB before startup?",
        action="store_true",
        default=False,
        dest="migrate_db"
    )
    args = parser.parse_args()
    logger.info("Подключение к Discord...")
    bot = MyBot()
    bot.run(
        config.settings['token'],
        log_level=logging.DEBUG if args.debug_mode else logging.INFO,
    )
