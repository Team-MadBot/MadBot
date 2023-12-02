# -*- coding: utf-8 -*-
import traceback
import discord
import time
import datetime
import os
import sys
import logging

from discord import app_commands, Forbidden
from discord.ext import commands
from asyncio import sleep

from classes import db
from classes import checks
from cogs.bc_api import LinktoBoticord
from classes.checks import isPremium, isPremiumServer
from config import *

intents = discord.Intents.default()

class MyBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('mad.'), intents=intents,
                         application_id=settings['app_id'])
        logging.getLogger('discord')
    
    async def load_cogs(self):  # Либо pylance сошёл с ума, или он должен быть здесь :sweat_smile:
        for path, _, files in os.walk('cogs'):
            for file in files:
                if not file.endswith(".py"): continue
                egg = os.path.join(path, file)
                try:
                    await self.load_extension(egg.replace(os.sep, '.')[:-3])
                except commands.NoEntryPointError:
                    pass # сделать логирование для debug режима (потому что можно обосраться и гадать часами, почему ког не загружается)
                except Exception as e:
                    print(f"При загрузке модуля {egg} произошла ошибка: {e}")
                    traceback.format_exc()

    async def setup_hook(self):
        await self.load_extension('jishaku')
        await self.load_cogs()

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
        logs = self.get_channel(settings['log_channel'])  # Канал логов.
        
        for guild in self.guilds:
            if checks.is_in_blacklist(guild.id) or checks.is_in_blacklist(guild.owner_id):
                await guild.leave()
                print(f"Бот вышел из {guild.name} ({guild.id})")
        
        print(f"Авторизация успешна! {self.user} готов к работе!")

        embed = discord.Embed(
            title="Бот перезапущен!", 
            color=discord.Color.red(),
            description=f"Пинг: `{int(round(self.latency, 3) * 1000)}ms`\n"
            f"Версия: `{settings['curr_version']}`"
        )
        await logs.send(embed=embed)
    
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
                timestamp=datetime.datetime.now()
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
                timestamp=datetime.datetime.now()
            ).add_field(
                name="ID разработчика:",
                value=blacklist_info['moderator_id']
            ).add_field(
                name="Причина занесения в ЧС:",
                value=blacklist_info['reason'] or "Не указана" 
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
                          timestamp=datetime.datetime.now())
    channel = bot.get_channel(settings['log_channel'])
    await channel.send(
        f"[ОШИБКА!]: Инициатор: `{interaction.user}`\n```\nOn command '{interaction.command.name}'\n{error}```")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.edit_original_response(embeds=[embed], view=None)
    traceback.print_exception(error)

print("Подключение к Discord...")
bot.run(settings['token'])
