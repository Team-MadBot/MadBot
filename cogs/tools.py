# -*- coding: utf-8 -*-
import discord
import datetime
import sys
import typing
import requests
import config
import numexpr
import qrcode
import os

from base64 import b64decode, b64encode
from asyncio import sleep, TimeoutError
from discord import Forbidden, app_commands, ui
from fluent.runtime import FluentLocalization, FluentResourceLoader
from discord.app_commands import Choice
from discord.ext import commands
from typing import Optional

from classes.checks import isPremium, isPremiumServer
from classes import db
from classes import checks
from config import *
from contextlib import suppress


def default_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (isPremium(interaction.client, interaction.user.id) != 'None' or
            isPremiumServer(interaction.client, interaction.guild)):
        return None
    return app_commands.Cooldown(1, 3.0)


def hard_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (isPremium(interaction.client, interaction.user.id) != 'None' or
            isPremiumServer(interaction.client, interaction.guild)):
        return app_commands.Cooldown(1, 2.0)
    return app_commands.Cooldown(1, 10.0)


class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot



        @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
        @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
        class Base64(app_commands.Group):
            """[Полезности] (Де-)кодирует указанный текст в Base64."""

            @app_commands.command(description="[Полезности] Кодирует указанный текст в Base64.")
            @app_commands.checks.dynamic_cooldown(default_cooldown)
            @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
            @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
            @app_commands.describe(text="Текст для кодировки")
            async def encode(self, interaction: discord.Interaction, text: app_commands.Range[str, None, 1024]):
                ans = b64encode(text.encode()).decode()
                if len(text) > 1024 or len(ans) > 1024:
                    embed = discord.Embed(title="Зашифровка:", color=discord.Color.orange(), description=f"**Исходный текст:**\n{text}")
                    embed1 = discord.Embed(title="Полученный текст:", color=discord.Color.orange(), description=ans)
                    return await interaction.response.send_message(embeds=[embed, embed1], ephemeral=True)
                embed = discord.Embed(title="Зашифровка:", color=discord.Color.orange())
                embed.add_field(name="Исходный текст:", value=text, inline=False)
                embed.add_field(name="Полученный текст:", value=ans)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            @app_commands.command(description="[Полезности] Декодирует Base64 в текст.")
            @app_commands.checks.dynamic_cooldown(default_cooldown)
            @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
            @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
            @app_commands.describe(text="Текст для декодировки")
            async def decode(self, interaction: discord.Interaction, text: str):
                try:
                    ans = b64decode(text).decode()
                except Exception:
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Невозможно расшифровать строку!")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                if len(text) > 1024 or len(ans) > 1024:
                    embed = discord.Embed(title="Зашифровка:", color=discord.Color.orange(), description=f"**Исходный текст:**\n{text}")
                    embed1 = discord.Embed(title="Полученный текст:", color=discord.Color.orange(), description=ans)
                    return await interaction.response.send_message(embeds=[embed, embed1], ephemeral=True)
                embed = discord.Embed(title="Расшифровка:", color=discord.Color.orange())
                embed.add_field(name="Исходный текст:", value=text, inline=False)
                embed.add_field(name="Полученный текст:", value=ans)
                await interaction.response.send_message(embed=embed, ephemeral=True)


        class QrCode(app_commands.Group):
            """[Полезности] Создание/чтение QR-кода."""
            @app_commands.command(description='[Полезности] Создать QR-код.')
            @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
            @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
            @app_commands.describe(text="Зашифрованный текст")
            async def create(self, interaction: discord.Interaction, text: str):
                await interaction.response.defer(thinking=True, ephemeral=True)
                qr = qrcode.QRCode()
                qr.add_data(text)
                img = qr.make_image()
                img.save(f'{interaction.user.id}.png')
                file = discord.File(f'{interaction.user.id}.png', filename=f"{interaction.user.id}.png")
                embed = discord.Embed(
                    title="QR-код",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Ваш текст:", value=f"`{text}`")
                embed.set_image(url=f'attachment://{interaction.user.id}.png')
                await interaction.followup.send(embed=embed, file=file)
                await sleep(5)
                os.remove(f'{interaction.user.id}.png')

        self.bot.tree.add_command(Base64())
        # self.bot.tree.add_command(QrCode())
    
    async def cog_load(self):
        thanks_users = {
            754719910256574646: "Второй разработчик бота и лучший бета-тестер. Написал некоторые команды развлечений "
            "и помог выявить более 20-ти багов. Один из спонсоров бота.",
            777140702747426817: "Помимо его работы саппортом, он часто апает бота, чем помогает в распространении его. "
            "Один из первых спонсоров бота."
        }
        self.thanks_user = {}
        for tu in thanks_users:
            u = await self.bot.fetch_user(tu)
            self.thanks_user[str(u)] = thanks_users[tu]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or checks.is_in_blacklist(message.author.id):
            return

        if message.content.startswith("/") and not message.author.bot:
            embed = discord.Embed(title="Команда введена неправильно!", color=discord.Color.red(), description="У бота `/` является не префиксом, а вызовом слеш-команд. Полностью очистите строку сообщений, поставьте `/` и выберите команду из списка.")
            await message.reply(embed=embed, delete_after=20)

        if message.author.id == 963819843142946846: # Триггер на сообщения мониторинга.
            await sleep(3)
            if message.content == "mad.debug ping":
                await message.channel.send(int(round(self.bot.latency, 3)*1000))
            if message.content == "mad.debug status":
                await message.channel.send("OK")

        if 'debug' in message.content:
            return

        if message.content in [
            f"<@!{self.bot.user.id}>",
            f"<@{self.bot.user.id}>",
        ]:
            embed=discord.Embed(title="Привет! Рад, что я тебе чем-то нужен!", color=discord.Color.orange(), description="Бот работает на слеш-командах, поэтому для взаимодействия с ботом следует использовать их. Для большей информации пропишите `/help`.")
            await message.reply(embed=embed, mention_author=False)
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data['component_type'] == 2 and interaction.data['custom_id'].isdigit():
            with suppress(Exception):
                role_id = int(interaction.data['custom_id'])
            with suppress(Exception):
                try:
                    member = await interaction.guild.fetch_member(interaction.user.id)
                except: 
                    return
                role = interaction.guild.get_role(role_id)
                if role is None:
                    return
                if role_id in [role.id for role in member.roles]:
                    try:
                        await member.remove_roles(role, reason="Нажатие на кнопку")
                    except:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    embed = discord.Embed(
                        title="Выбор роли", 
                        color=discord.Color.green(),
                        description=f"Роль {role.mention} успешно убрана!"
                    )
                else:
                    try:
                        await member.add_roles(role, reason="Нажатие на кнопку")
                    except:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    embed = discord.Embed(
                        title="Выбор роли", 
                        color=discord.Color.green(),
                        description=f"Роль {role.mention} успешно добавлена!"
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        elif interaction.type == discord.InteractionType.component and interaction.data['component_type'] == 3 and interaction.data['values'][0].isdigit():
            await interaction.response.defer(thinking=True, ephemeral=True)
            changes = ""
            for value in interaction.data['values']:
                with suppress(Exception):
                    role_id = int(value)
                with suppress(Exception):
                    try: 
                        member = await interaction.guild.fetch_member(interaction.user.id)
                    except: 
                        return
                    role = interaction.guild.get_role(role_id)
                    if role is None:
                        return
                    if role_id in [role.id for role in member.roles]:
                        try:
                            await member.remove_roles(role, reason="Нажатие на кнопку")
                        except:
                            embed = discord.Embed(
                                title="Ошибка!",
                                color=discord.Color.red(),
                                description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                            )
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        changes += f"Роль {role.mention} успешно убрана!\n"
                    else:
                        try:
                            await member.add_roles(role, reason="Нажатие на кнопку")
                        except:
                            embed = discord.Embed(
                                title="Ошибка!",
                                color=discord.Color.red(),
                                description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                            )
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        changes += f"Роль {role.mention} успешно добавлена!\n"
            embed = discord.Embed(
                title="Выбор ролей:",
                color=discord.Color.green()
            )
            embed.add_field(name="Изменения:", value=changes)
            await interaction.followup.send(embed=embed)
        elif not(interaction.response.is_done()) and interaction.type == discord.InteractionType.component:
            await sleep(4)
            if interaction.response.is_done(): return
            embed = discord.Embed(
                title="Ошибка",
                color=discord.Color.red(),
                description="Похоже, данный компонент больше не работает. Вызовите команду для получения этого компонента снова!"
            )
            with suppress(Exception):
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="[Полезности] Показывает изменения в текущей версии.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(ver="Версия бота")
    @app_commands.choices(ver=[
        Choice(name="Актуальная", value="actual"),
        Choice(name="1.1.1", value='111'),
        Choice(name="1.1", value='11'),
        Choice(name='1.0', value='10')
    ])
    async def version(self, interaction: discord.Interaction, ver: Choice[str] = None):
        embed = None
        if ver is not None:
            ver = ver.name
        if ver is None or ver == settings['curr_version'] or ver == "Актуальная":
            updated_at = datetime.datetime(2023, 5, 29, 22, 0, 0, 0)
            embed = discord.Embed(
                title='Версия `1.1.1`',
                color=discord.Color.orange(),
                timestamp=updated_at,
                description=(
                    f"Это баг-фикс версия, которая содержит лишь исправления багов (нового функционала нет).\n\n"
                    f"- `/userinfo` - работает и отображает актуальную информацию о пользователе (кроме статуса), поддержка \"Pomelo\".\n"
                    f"- `/avatar` - показ серверного аватара.\n"
                    f"- `/serverinfo` - снова работает и показывает владельца сервера, а также исправлено несовпадение дизайна.\n"
                    f"- `/debug` - бот теперь правильно отображает, является ли инициатор команды владельцем сервера.\n"
                    f"- SDC - отправка статистики.\n"
                    f"- Библиотеки - переход снова на альфа-версию discord.py (для реализации работы с Pomelo).\n"
                    f"- Политика конфиденциальности - обновлены пункты 1.2, 1.2.1, 3, 4. Просьба ознакомиться с изменениями."
                ),
            )
            embed.set_footer(text="Обновлено:")
        if ver == '1.1':
            updated_at = datetime.datetime(2022, 12, 4, 14, 0, 0, 0)
            embed = discord.Embed(
                title='Версия `1.1`',
                color=discord.Color.orange(),
                timestamp=updated_at,
                description=(
                    f"`1.` Свадьбы. Подробнее: `/help` > Свадьбы.\n"
                    f"`2.` Статистика. На данный момент, она может не обновляться. В ближайшее время она начнет обновляться.\n"
                    f"`3.` Обновление `/kiss`. Если целоваться при наличии брака, будет измененное сообщение."
                    f"`4.` Премиум. Теперь в бота будут постепенно добавляться премиум возможности. Одна из них: принудительная свадьба и развод. Управление подпиской: `/premium`.\n"
                ),
            )
            embed.set_footer(text="Обновлено:")
        if ver == '1.0':
            updated_at = datetime.datetime(2022, 7, 31, 15, 0, 0, 0)
            embed = discord.Embed(
                title='Версия `1.0`',
                color=discord.Color.orange(),
                timestamp=updated_at,
                description=f"1) Фиксы многих багов.\n2) Поддержка ограничения длины аргументов в слеш-командах.\n3) Переезд кастомизации эмбеда в формы (`/buttonrole`).\n4) Небольшие изменения дизайна.\n5) Можно указать цвет для эмбеда в `/buttonrole`.",
            )
            embed.set_footer(text="Обновлено:")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="errors", description="[Полезности] Список ошибок и решения их")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def errors(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Ошибки бота:", color=discord.Color.orange())
        embed.add_field(name="Ошибка: Forbidden", value="Бот не может совершить действие. Убедитесь, что бот имеет право(-а) на совершение действия.", inline=False)
        embed.add_field(name="Ошибка: NotFound", value="Боту не удалось найти объект (пользователя, сервер и т.д.).", inline=False)
        embed.add_field(name="Ошибка: HTTPException", value="Бот отправил некорректный запрос на сервера Discord, из-за чего получил ошибку. Убедитесь, что вы ввели всё верно.", inline=False)
        embed.set_footer(text="В случае, если вашей ошибки нет в списке, обратитесь в поддержку.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="[Полезности] Показывает основную информацию о боте.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def help(self, interaction: discord.Interaction):
        commands = self.bot.tree.get_commands(type=discord.AppCommandType.chat_input)
        #mod_commands = ""
        tools_commands = ""
        ent_commands = ""
        react_commands = ""
        stats_commands = ""
        marry_commands = ""
        premium_commands = ""
        for command in commands:
            if command.description.startswith("[Модерация]"):
                mod_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Модерация]')}\n"
            if command.description.startswith("[Полезности]"):
                tools_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Полезности]')}\n"
            if command.description.startswith("[Развлечения]") or command.description.startswith("[NSFW]"):
                ent_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Развлечения]').removeprefix('[NSFW]')}\n"
            if command.description.startswith("[Реакции]"):
                react_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Реакции]')}\n"
            if command.description.startswith("[Статистика]"):
                stats_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Статистика]')}\n"
            if command.description.startswith("[Свадьбы]"):
                marry_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Свадьбы]')}\n"
            if command.qualified_name.startswith("premium"):
                premium_commands += f"`/{command.qualified_name}` - {command.description}\n"

        #moderation = discord.Embed(
        #    title=f"{self.bot.user.name} - Модерация", 
        #    color=discord.Color.orange(), 
        #    description=mod_commands
        #)
        tools = discord.Embed(
            title=f"{self.bot.user.name} - Полезности",
            color=discord.Color.orange(), 
            description=tools_commands
        )
        entartaiment = discord.Embed(
            title=f"{self.bot.user.name} - Развлечения",
            color=discord.Color.orange(), 
            description=ent_commands
        )
        reactions = discord.Embed(
            title=f"{self.bot.user.name} - Реакции",
            color=discord.Color.orange(),
            description=react_commands
        )
        stats = discord.Embed(
            title=f"{self.bot.user.name} - Свадьбы",
            color=discord.Color.orange(),
            description=stats_commands
        )
        marry = discord.Embed(
            title=f"{self.bot.user.name} - Статистика",
            color=discord.Color.orange(),
            description=marry_commands
        )
        premium = discord.Embed(
            title=f"{self.bot.user.name} - Премиум",
            color=discord.Color.orange(),
            description=premium_commands
        )
        embed = discord.Embed(
            title=f"{self.bot.user.name} - Главная", 
            color=discord.Color.orange(), 
            description=f"""Спасибо за использование {self.bot.user.name}! Я использую слеш-команды, поэтому для настройки доступа к ним можно использовать настройки Discord.
            
**Что я умею?**
- **Развлекать**. Если Вам скучно, то посмотрите, как можно развлечься.
- **Реагировать**. Хотите показать свои эмоции? Пожалуйста!
- **Прочее**. Узнать погоду, подсчитать пример или получить аватар пользователя можно в одном боте!
            
Выберите категорию команд для их просмотра.""")
        embed.add_field(
            name="Поддержать разработку",
            value=f"""Поддержка - не всегда означает необходимость платить. Если у Вас нету денег, просто оцените бота на Boticord и SDC Monitoring. Так Вы поможете продвинуть бота. Можете ещё написать свой отзыв - обязательно прочтем и учтем.
            
**СКОРО:** Если у Вас есть деньги, Вы можете связаться с разработчиком для покупки MadBot Premium. Так мы сможет продолжать разработку, а Вы получите уникальные функции."""
        )

        class DropDownCommands(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Главная", value="embed", description="Главное меню.", emoji="🐱"),
                    #discord.SelectOption(label="Модерация", value="moderation", description="Команды модерации.", emoji="🛑"),
                    discord.SelectOption(label="Полезности", value="tools", description="Полезные команды.", emoji="⚒️"),
                    discord.SelectOption(label="Развлечения", value="entartaiment", description="Развлекательные команды.", emoji="🎉"),
                    discord.SelectOption(label="Реакции", value="reactions", description="Команды реакций.", emoji="🎭"),
                    discord.SelectOption(label="Статистика", value="stats", description="Настройка статистики сервера.", emoji="📊"),
                    discord.SelectOption(label="Свадьбы", value="marry", description="Женитесь и разводитесь.", emoji="❤️"),
                    discord.SelectOption(label="Премиум", value="premium", description="Управление премиум-подпиской.", emoji="👑")
                ]
                super().__init__(placeholder="Команды", options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if interaction.user.id != viewinteract.user.id:
                    if self.values[0] == "embed":
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                    #elif self.values[0] == "moderation":
                    #    return await viewinteract.response.send_message(embed=moderation, ephemeral=True)
                    elif self.values[0] == "tools":
                        return await viewinteract.response.send_message(embed=tools, ephemeral=True)
                    elif self.values[0] == "reactions":
                        return await viewinteract.response.send_message(embed=reactions, ephemeral=True)
                    elif self.values[0] == "entartaiment":
                        return await viewinteract.response.send_message(embed=entartaiment, ephemeral=True)
                    elif self.values[0] == "marry":
                        return await viewinteract.response.send_message(embed=marry, ephemeral=True)
                    elif self.values[0] == "premium":
                        return await viewinteract.response.send_message(embed=premium, ephemeral=True)
                    else:
                        return await viewinteract.response.send_message(embed=stats, ephemeral=True)
                if self.values[0] == "embed":
                    await viewinteract.response.edit_message(embed=embed)
                #elif self.values[0] == "moderation":
                #    await viewinteract.response.edit_message(embed=moderation)
                elif self.values[0] == "tools":
                    await viewinteract.response.edit_message(embed=tools)
                elif self.values[0] == "reactions":
                    return await viewinteract.response.edit_message(embed=reactions)
                elif self.values[0] == "entartaiment":
                    return await viewinteract.response.edit_message(embed=entartaiment)
                elif self.values[0] == "marry":
                    return await viewinteract.response.edit_message(embed=marry)
                elif self.values[0] == "premium":
                    return await viewinteract.response.edit_message(embed=premium)
                else:
                    return await viewinteract.response.edit_message(embed=stats)

        class DropDownHelp(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Я нашел баг!", value="bugreport", description="Заполните форму, и мы исправим баг как можно скорее!", emoji='🐞'),
                    discord.SelectOption(label="У меня вопрос!", value="question", description="Заполните форму, и вам ответят на вопрос!", emoji='❓')
                ]
                super().__init__(placeholder='Обратная связь', options=options)

            class BugReport(discord.ui.Modal, title="Сообщить о баге"):
                main = discord.ui.TextInput(label="Тема:", placeholder="Команда /команда выдаёт ошибку.", max_length=50)
                description = discord.ui.TextInput(label="Подробности:", placeholder="При таком-то действии бот выдает ошибку, хотя должен был сделать совсем другое.", style=discord.TextStyle.paragraph, max_length=2048)
                links = discord.ui.TextInput(label="Ссылки на док-ва:", required=False, style=discord.TextStyle.paragraph, max_length=1024, placeholder="https://imgur.com/RiCkROLl")

                async def on_submit(self, viewinteract: discord.Interaction):
                    log_channel = viewinteract.client.get_channel(settings['report_channel'])
                    embed = discord.Embed(title=f"Сообщение о баге: {str(self.main)}", color=discord.Color.red(), description=str(self.description))
                    embed.set_author(name=str(viewinteract.user), icon_url=viewinteract.user.display_avatar.url)
                    if str(self.links) != "":
                        embed.add_field(name="Ссылки:", value=str(self.links))
                    await log_channel.send(embed=embed)
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Сообщение о баге успешно отправлено!")
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                
            class AskQuestion(discord.ui.Modal, title="Задать вопрос"):
                main = discord.ui.TextInput(label="Тема:", placeholder="Как сделать так-то.", max_length=50)
                description = discord.ui.TextInput(label="Подробности:", placeholder="Я хочу сделать так. Как так сделать?", style=discord.TextStyle.paragraph, max_length=2048)
                links = discord.ui.TextInput(label="Ссылки на док-ва:", required=False, style=discord.TextStyle.paragraph, max_length=1024, placeholder="https://imgur.com/RiCkROLl")

                async def on_submit(self, viewinteract: discord.Interaction):
                    log_channel = viewinteract.client.get_channel(settings['report_channel'])
                    q_embed = discord.Embed(title=f"Вопрос: {str(self.main)}", color=discord.Color.red(), description=str(self.description))
                    q_embed.set_author(name=str(viewinteract.user), icon_url=viewinteract.user.display_avatar.url)
                    if str(self.links) != "":
                        q_embed.add_field(name="Ссылки:", value=str(self.links))

                    class Buttons(discord.ui.View):
                        def __init__(self, main: str):
                            super().__init__(timeout=None)
                            self.main = main
                        
                        @discord.ui.button(label="Ответить", style=discord.ButtonStyle.primary, emoji="✏️")
                        async def answer(self, buttinteract: discord.Interaction, button: discord.ui.Button):
                            if not (buttinteract.user.id in supports):
                                return await buttinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True) 
                            class AnswerQuestion(discord.ui.Modal, title="Ответ на вопрос"):
                                def __init__(self, main: str):
                                    super().__init__(custom_id="MadBotAnswerQuestion")
                                    self.main = main
                                answer = discord.ui.TextInput(label="Ответ:", placeholder="Сделайте вот так:", style=discord.TextStyle.paragraph, max_length=2048)

                                async def on_submit(self, ansinteract: discord.Interaction):
                                    nonlocal q_embed
                                    embed = discord.Embed(title=f'Ответ на вопрос "{self.main}"!', color=discord.Color.green(), description=str(self.answer))
                                    embed.set_author(name=str(ansinteract.user), icon_url=ansinteract.user.display_avatar.url)
                                    try:
                                        await viewinteract.user.send(embed=embed)
                                    except:
                                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не смог отправить ответ на вопрос в личные сообщения пользователя!")
                                        await ansinteract.response.send_message(embed=embed, ephemeral=True)
                                    else:
                                        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ответ отправлен пользователю.")
                                        await ansinteract.response.send_message(embed=embed, ephemeral=True)
                                    q_embed.add_field(name=f"Ответ от {ansinteract.user}:", value=str(self.answer))
                                    await buttinteract.edit_original_response(embed=q_embed, view=None)
                                
                            await buttinteract.response.send_modal(AnswerQuestion(self.main))

                    await log_channel.send(embed=q_embed, view=Buttons(self.main))
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Вопрос успешно отправлен!")
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)

            async def callback(self, viewinteract: discord.Interaction):
                if checks.is_in_blacklist(viewinteract.user.id):
                    embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.now())
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                    return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                modals = {
                    'bugreport': self.BugReport(),
                    'question': self.AskQuestion()
                }
                await viewinteract.response.send_modal(modals[self.values[0]])
           
        class DropDownView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(DropDownCommands())
                self.add_item(DropDownHelp())
                self.add_item(discord.ui.Button(label="Поддержка", url=settings['support_invite']))
                self.add_item(discord.ui.Button(label="Добавить бота", url=f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands"))
                self.add_item(discord.ui.Button(label="Апнуть бота: BotiCord.top", url=f"https://boticord.top/bot/{settings['app_id']}", emoji="<:bc:947181639384051732>"))
                self.add_item(discord.ui.Button(label="Апнуть бота: SDC Monitoring", url=f"https://bots.server-discord.com/{settings['app_id']}", emoji="<:favicon:981586173204000808>"))

        await interaction.response.send_message(embed=embed, view=DropDownView())

    @app_commands.command(name="userinfo", description="[Полезности] Показывает информацию о пользователе")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member='Участник')
    async def userinfo(self, interaction: discord.Interaction, member: discord.User = None):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(member, discord.User):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Пользователь должен находиться на сервере для использования команды на нём!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        badges = ''
        if member is None: member = interaction.user
        else:
            try:
                member = await interaction.guild.fetch_member(member.id)
            except:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Участник должен находиться на сервере для использования команды!")
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            member = await interaction.guild.fetch_member(member.id)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description=(
                    "Странно, но нам не удалось найти Вас как участника этого сервера. Так быть не должно. "
                    "Обратитесь в поддержку по ссылке в \"обо мне\" бота или по кнопке в `/help` или `/botinfo`."
                )
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        member_color = member.color
        if member_color.value == 0:
            member_color = discord.Color.orange()
        
        embed = discord.Embed(color=member_color, description=f"[Скачать]({member.display_avatar.replace(static_format='png', size=2048)})")
        embed.set_author(name=f"Аватар {member}")
        embed.set_image(url=member.display_avatar.replace(static_format="png", size=2048))
        embed.set_footer(text=f"Формат: png | Размер: 2048 | Тип аватара: Серверный.")

        if checks.is_in_blacklist(member.id):
            badges += '<:ban:946031802634612826> '
        if isPremium(self.bot, member.id) != 'None':
            badges += '<a:premium:988735181546475580> '
        if member.is_timed_out():
            badges += '<:timeout:950702768782458893> '
        if member.id == settings['owner_id']:
            badges += '<:botdev:977645046188871751> '
        if member.id in coders:
            badges += '<:code:946056751646638180> '
        if member.id in supports:
            badges += '<:support:946058006641143858> '
        if member.id in bug_hunters:
            badges += '<:bug_hunter:955497457020715038> '
        if member.id in bug_terminators:
            badges += '<:bug_terminator:955891723152801833> '
        if member.id in verified:
            badges += '<:verified:946057332389978152> '
        if member.bot:
            badges += '<:bot:946064625525465118> '
        emb: discord.Embed
        global_name = member.global_name or member.name
        username = str(member)
        if member.nick is None:
            emb = discord.Embed(
                title=f"`{global_name} "
                f"({username})` {badges}", 
                color=member_color
            )
        else:
            emb = discord.Embed(
                title=f"`{global_name} "
                f"({username})` | `{member.nick}` {badges}", 
                color=member_color
            )
        emb.add_field(name="Упоминание:", value=member.mention, inline=False)
        if self.bot.intents.presences:
            if member.status == discord.Status.online:
                emb.add_field(name="Статус:", value="🟢 В сети", inline=False)
            elif member.status == discord.Status.idle:
                emb.add_field(name="Статус:", value="🌙 Нет на месте", inline=False)
            elif member.status == discord.Status.dnd:
                emb.add_field(name="Статус:", value="🔴 Не беспокоить", inline=False)
            else:
                emb.add_field(name="Статус:", value="🔘 Не в сети", inline=False)
        emb.add_field(name="Ссылка на профиль:", value=f"[Тык](https://discord.com/users/{member.id})", inline=False)
        if member.bot:
            emb.add_field(name="Бот?:", value="Да", inline=False)
        else:
            emb.add_field(name="Бот?:", value="Нет", inline=False)
        if member.guild_permissions.administrator:
            emb.add_field(name="Администратор?:", value=f'Да', inline=False)
        else:
            emb.add_field(name="Администратор?:", value='Нет', inline=False)
        emb.add_field(name="Самая высокая роль на сервере:", value=f"{member.top_role.mention}", inline=False)
        emb.add_field(name="Акаунт был создан:", value=f"{discord.utils.format_dt(member.created_at, 'D')} ({discord.utils.format_dt(member.created_at, 'R')})", inline=False)
        emb.add_field(name="Присоединился:", value=f"{discord.utils.format_dt(member.joined_at, 'D')} ({discord.utils.format_dt(member.joined_at, 'R')})", inline=False)
        emb.set_thumbnail(url=member.display_avatar.replace(static_format="png", size=1024))
        member = await self.bot.fetch_user(member.id)
        if member.banner is not None:
            emb.set_image(url=member.banner.url)
        emb.set_footer(text=f'ID: {member.id}')

        if member.banner is not None:
            banner = discord.Embed(color=member_color, description=f"[Скачать]({member.banner.url})")
            banner.set_author(name=f"Баннер {member}")
            banner.set_image(url=member.banner.url)
        else:
            banner = discord.Embed(title="Ошибка", color=discord.Color.red(), description="У пользователя отсутствует баннер!")

        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Аватар", value="avatar", description="Получить аватар пользователя.", emoji="🖼️"),
                    discord.SelectOption(label="Баннер", value="banner", description="Получить баннер пользователя (при наличии).", emoji="🏙️"),
                    discord.SelectOption(label="Информация", value="main", description="Информация об пользователе.", emoji="📙")
                ]
                super().__init__(placeholder="Информация...", min_values=1, max_values=1, options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if self.values[0] == "main":
                    await viewinteract.response.send_message(embed=emb, ephemeral=True)
                elif self.values[0] == "avatar":
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                else:
                    await viewinteract.response.send_message(embed=banner, ephemeral=True)

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(SelectMenu())

        await interaction.response.send_message(embed=emb, view=View())

    @app_commands.command(name="avatar", description="[Полезности] Присылает аватар пользователя")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(
        member='Участник, чью аватарку вы хотите получить', 
        format="Формат изображения", 
        size="Размер изображения", 
        type="Тип аватара"
    )
    @app_commands.choices(
        format=[
            Choice(name="PNG (прозрачный фон)", value="png"),
            Choice(name="JPEG (черный фон)", value="jpeg"),
            Choice(name="JPG (как JPEG)", value='jpg'),
            Choice(name="WEBP (веб-картинка)", value='webp')
        ],
        size=[
            Choice(name="16x16 пикселей", value=16),
            Choice(name="32x32 пикселей", value=32),
            Choice(name="64x64 пикселей", value=64),
            Choice(name="128x128 пикселей", value=128),
            Choice(name="256x256 пикселей", value=256),
            Choice(name="512x512 пикселей", value=512),
            Choice(name="1024x1024 пикселей", value=1024),
            Choice(name="2048x2048 пикселей", value=2048),
            Choice(name="4096x4096 пикселей", value=4096)
        ],
        type=[
            Choice(name="Стандартная", value='standart'),
            Choice(name="Серверная", value='server')
        ]
    )
    async def avatar(
        self, 
        interaction: discord.Interaction, 
        member: discord.User = None, 
        format: Choice[str] = "png", 
        size: Choice[int] = 2048, 
        type: Choice[str] = 'standart'
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member is None: member = interaction.user
        try:
            member: discord.Member = await interaction.guild.fetch_member(member.id)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда работает только на участниках этого сервера"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if format != 'png': format = format.value
        if size != 2048: size = size.value
        if type != 'standart': type = type.value
        user_avatar = member.avatar or member.default_avatar
        if type == 'server': 
            if member.guild_avatar is None:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Ошибка!",
                        color=discord.Color.red(),
                        description="Пользователь не имеет серверного аватара."
                    ),
                    ephemeral=True
                )
            user_avatar = member.guild_avatar
        embed = discord.Embed(
            color=discord.Color.orange() if member.color == discord.Color.default() else member.color,
            description=f"[Скачать]({user_avatar.replace(static_format=format, size=size)})"
        )
        embed.set_author(name=f"Аватар {member}")
        embed.set_image(url=user_avatar.replace(static_format=format, size=size))
        type = "Серверный" if type == "server" else "Стандартный"
        embed.set_footer(text=f"Запросил: {str(interaction.user)} | Формат: {format} | Размер: {size} | Тип аватара: {type}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="[Полезности] Информация о сервере")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def serverinfo(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        badges = ''
        if checks.is_in_blacklist(interaction.guild.id):
            badges += '<:ban:946031802634612826> '
        if interaction.guild.id in verified:
            badges += '<:verified:946057332389978152> '
        if isPremiumServer(self.bot, interaction.guild):
            badges += '<a:premium:988735181546475580> '
        if interaction.guild.id in beta_testers:
            badges += '<:beta:946063731819937812> '
        embed = discord.Embed(
            title=f"{interaction.guild.name} {badges}", 
            color=discord.Color.orange()
        )
        embed.add_field(name="Владелец:", value=f"<@!{interaction.guild.owner_id}>", inline=True)
        if interaction.guild.default_notifications == "all_messages":
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Все сообщения", inline=True)
        else:
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Только @упоминания", inline=True)
        embed.add_field(name="Кол-во каналов:", value=len(interaction.guild.channels) - len(interaction.guild.categories), inline=True)
        embed.add_field(name="Кол-во категорий:", value=len(interaction.guild.categories), inline=True)
        embed.add_field(name="Текстовых каналов:", value=len(interaction.guild.text_channels), inline=True)
        embed.add_field(name="Голосовых каналов:", value=len(interaction.guild.voice_channels), inline=True)
        embed.add_field(name="Трибун:", value=len(interaction.guild.stage_channels), inline=True)
        embed.add_field(name="Кол-во эмодзи:", value=f"{len(interaction.guild.emojis)}/{interaction.guild.emoji_limit * 2}", inline=True)
        temp = interaction.guild.verification_level
        if temp == discord.VerificationLevel.none:
            embed.add_field(name="Уровень проверки:", value="Отсутствует", inline=True)
        elif temp == discord.VerificationLevel.low:
            embed.add_field(name="Уровень проверки:", value="Низкий", inline=True)
        elif temp == discord.VerificationLevel.medium:
            embed.add_field(name="Уровень проверки:", value="Средний", inline=True)
        elif temp == discord.VerificationLevel.high:
            embed.add_field(name="Уровень проверки:", value="Высокий", inline=True)
        elif temp == discord.VerificationLevel.highest:
            embed.add_field(name="Уровень проверки:", value="Очень высокий", inline=True)
        embed.add_field(name="Дата создания:", value=f"{discord.utils.format_dt(interaction.guild.created_at, 'D')} ({discord.utils.format_dt(interaction.guild.created_at, 'R')})", inline=True)
        if interaction.guild.rules_channel is not None:
            embed.add_field(name="Канал с правилами:", value=interaction.guild.rules_channel.mention)
        else:
            embed.add_field(name="Канал с правилами:", value="Недоступно (сервер не является сервером сообщества)")
        embed.add_field(name="Веток:", value=f"{len(interaction.guild.threads)}")
        roles = ""
        counter = 0
        guild_roles = await interaction.guild.fetch_roles()
        guild_roles = list(guild_roles)
        guild_roles.sort(key=lambda x: x.position, reverse=True)
        for role in guild_roles:
            if counter <= 15: roles += f"{role.mention}, "
            else:
                roles += f"и ещё {len(guild_roles) - 16}..."
                break
            counter += 1
        embed.add_field(name=f"Роли ({len(interaction.guild.roles) - 1}):", value=roles)
        if interaction.guild.icon is not None: embed.set_thumbnail(url=interaction.guild.icon.replace(static_format="png", size=1024))
        if interaction.guild.banner is not None: embed.set_image(url=interaction.guild.banner.replace(static_format="png"))
        embed.set_footer(text=f"ID: {interaction.guild.id}")

        if interaction.guild.banner is not None:
            banner = discord.Embed(color=discord.Color.orange(), description=f"[Скачать]({interaction.guild.banner.url})")
            banner.set_author(name=f"Баннер {interaction.guild.name}")
            banner.set_image(url=interaction.guild.banner.url)
        else:
            banner = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У сервера отсутствует баннер!")

        if interaction.guild.icon is not None:
            icon = discord.Embed(color=discord.Color.orange(), description=f"[Скачать]({interaction.guild.icon.url})")
            icon.set_author(name=f"Аватар {interaction.guild.name}")
            icon.set_image(url=interaction.guild.icon.url)
        else:
            icon = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У сервера отсутствует аватар!")

        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Аватар", value="avatar", description="Получить аватар сервера.", emoji="🖼️"),
                    discord.SelectOption(label="Баннер", value="banner", description="Получить баннер сервера (при наличии).", emoji="🏙️"),
                    discord.SelectOption(label="Информация", value="main", description="Информация об сервере.", emoji="📙")
                ]
                super().__init__(placeholder="Информация...", min_values=1, max_values=1, options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if self.values[0] == "main":
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                elif self.values[0] == "avatar":
                    await viewinteract.response.send_message(embed=icon, ephemeral=True)
                else:
                    await viewinteract.response.send_message(embed=banner, ephemeral=True)

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(SelectMenu())

        await interaction.response.send_message(embed=embed, view=View())

    @app_commands.command(name="botinfo", description="[Полезности] Информация о боте")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def botinfo(self, interaction: discord.Interaction):
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.now())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(title=f"{self.bot.user.name} - v{settings['curr_version']}", color=discord.Color.orange(), description=f"Для выбора категории используйте меню снизу.\n\n**Основная информация:**")
        embed.add_field(name="Разработчик:", value=f"<@!{settings['owner_id']}>")
        embed.add_field(name="ID разработчика:", value=f"`{settings['owner_id']}`")
        embed.add_field(name="ID бота:", value=f"`{self.bot.user.id}`")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"©️ 2021 - 2023 MadBot. Все права защищены.")

        bot_stats = db.get_bot_stats()
        stats = discord.Embed(title=f"{self.bot.user.name} - Статистика", color=discord.Color.orange())
        stats.add_field(name="Пинг:", value=f"{int(round(self.bot.latency, 3)*1000)}ms")
        stats.add_field(name="Запущен:", value=f"<t:{started_at}:R>")
        stats.add_field(name="Кол-во серверов:", value=f"{len(self.bot.guilds):,}")
        stats.add_field(name="Кол-во участников:", value=f"{len(self.bot.users):,}")
        stats.add_field(name="Последняя использованная команда:", value=bot_stats['last_command'])
        stats.add_field(name="Кол-во команд/контекстных меню:", value=f"{len(self.bot.tree.get_commands(type=discord.AppCommandType.chat_input)):,}/{len(self.bot.tree.get_commands(type=discord.AppCommandType.user)) + len(self.bot.tree.get_commands(type=discord.AppCommandType.message)):,}")
        stats.add_field(name="Обработано команд:", value=f"{bot_stats['used_commands']:,}")
        stats.set_thumbnail(url=self.bot.user.display_avatar.url)
        stats.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        versions = discord.Embed(title=f"{self.bot.user.name} - Версии", color=discord.Color.orange())
        versions.add_field(name="Версия:", value=settings['curr_version'])
        versions.add_field(name="Версия discord.py:", value=f"{discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro} `{discord.version_info.releaselevel.upper()}`")
        versions.add_field(name="Версия Python:", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        ver_info = sys.platform
        if ver_info.startswith("win32"):
            ver_info = "Windows"
        if ver_info.startswith("linux"):
            ver_info = "Linux"
        if ver_info.startswith("aix"):
            ver_info = "AIX"
        if ver_info.startswith("darwin"):
            ver_info = "MacOS"
        versions.add_field(name="Операционная система:", value=ver_info)
        versions.set_thumbnail(url=self.bot.user.display_avatar.url)
        versions.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        thanks = discord.Embed(
            title = f"{self.bot.user.name} - Благодарности",
            color = discord.Color.orange(),
            description="Этим людям я очень благодарен. Благодаря им, MadBot поднимается и улучшается."
        )
        thanks.set_thumbnail(url=self.bot.user.display_avatar.url)
        thanks.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)

        for tu in self.thanks_user:
            thanks.add_field(
                name=tu,
                value=self.thanks_user[tu],
                inline=False
            )

        embeds = {
            'embed': embed,
            'stats': stats,
            'versions': versions,
            'thanks': thanks
        }

        class DropDown(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Главная", value="embed", description="Главное меню.", emoji="🐱"),
                    discord.SelectOption(label="Статистика", value='stats', description="Статистика бота.", emoji="📊"),
                    discord.SelectOption(label="Версии", value="versions", description="Версии библиотек и Python.", emoji="⚒️"),
                    discord.SelectOption(label="Благодарности", value="thanks", description="Эти люди сделали многое для бота.", emoji="❤️")
                ]
                super().__init__(placeholder="Выбор...", options=options, row=1)

            async def callback(self, viewinteract: discord.Interaction):
                if interaction.user != viewinteract.user:
                    return await viewinteract.response.send_message(embed=embeds[self.values[0]], ephemeral=True)
                else:
                    await interaction.edit_original_response(embed=embeds[self.values[0]])
                    await viewinteract.response.defer()

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(discord.ui.Button(label="Поддержка", url=settings['support_invite']))
                self.add_item(discord.ui.Button(label="Добавить бота", url=f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands"))
                self.add_item(discord.ui.Button(label="Апнуть бота: BotiCord.top", url=f"https://boticord.top/bot/{settings['app_id']}", emoji="<:bc:947181639384051732>"))
                self.add_item(discord.ui.Button(label="Апнуть бота: SDC Monitoring", url=f"https://bots.server-discord.com/{settings['app_id']}", emoji="<:favicon:981586173204000808>"))
                self.add_item(DropDown())

        await interaction.response.send_message(embed=embed, view=View())

    @app_commands.command(name="badgeinfo", description="[Полезности] Информация о значках пользователей и серверов в боте.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def badgeinfo(self, interaction: discord.Interaction):
        embed=discord.Embed(title="Виды значков:", color=discord.Color.orange())
        embed.add_field(name="Значки пользователя:", value=f"<:ban:946031802634612826> - пользователь забанен в системе бота.\n<a:premium:988735181546475580> - пользователь имеет MadBot Premium.\n<:timeout:950702768782458893> - пользователь получил тайм-аут на сервере.\n<:botdev:977645046188871751> - разработчик бота.\n<:code:946056751646638180> - помощник разработчика.\n<:support:946058006641143858> - поддержка бота.\n<:bug_hunter:955497457020715038> - охотник на баги (обнаружил и сообщил о 3-х и более багах).\n<:bug_terminator:955891723152801833> - уничтожитель багов (обнаружил и сообщил о 10-ти и более багах).\n<:verified:946057332389978152> - верифицированный пользователь.\n<:bot:946064625525465118> - участник является ботом.", inline=False)
        embed.add_field(name="Значки сервера:", value=f"<:verified:946057332389978152> - верифицированный сервер.\n<a:premium:988735181546475580> - сервер имеет MadBot Premium.\n<:ban:946031802634612826> - сервер забанен в системе бота.\n<:beta:946063731819937812> - сервер, имеющий доступ к бета-командам.", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='outages', description="[Полезности] Показывает актуальные сбои в работе бота.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def outages(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(settings['outages'])
        outage = None
        async for message in channel.history(limit=1):
            outage = message
        if message.content.find("<:outage_fixed:958778052136042616>") == -1 and message.content is not None:
            embed = discord.Embed(title="Обнаружено сообщение о сбое!", color=discord.Color.red(), description=outage.content, timestamp=outage.created_at)
            embed.set_author(name=outage.author, icon_url=outage.author.display_avatar.url)
            embed.set_footer(text="Актуально на")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Актуальные сбои отсутствуют", color=discord.Color.green(), description="Спасибо, что пользуетесь MadBot!", timestamp=datetime.datetime.now())
            embed.set_footer(text="Актуально на")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nick", description="[Полезности] Изменяет ваш ник.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(argument="Ник, на который вы хотите поменять. Оставьте пустым для сброса ника")
    async def nick(self, interaction: discord.Interaction, argument: str = None):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not self.bot.intents.members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="На данный момент, команда недоступна."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        bot_member = await interaction.guild.fetch_member(self.bot.user.id)
        if not bot_member.guild_permissions.manage_nicknames or bot_member.top_role < interaction.user.top_role:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не может изменить Вам никнейм!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if argument is not None and len(argument) > 32:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Длина ника не должна превышать `32 символа`!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.guild_permissions.change_nickname:
            if interaction.user.id == interaction.guild.owner.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не может изменять никнейм владельцу сервера!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            try:
                await interaction.user.edit(nick=argument, reason="Самостоятельная смена ника")
            except Forbidden:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не смог изменить вам никнейм!\nТип ошибки: `Forbidden`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = None
                if argument is not None:
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Ваш ник успешно изменён на `{argument}`!", timestamp=datetime.datetime.now())
                else:
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ваш ник успешно сброшен!", timestamp=datetime.datetime.now())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            string = None
            string = "Вы желаете сбросить никнейм." if argument is None else f"Ваш желаемый ник: `{argument}`."
            embed = discord.Embed(title="Запрос разрешения", color=discord.Color.orange(), description=f"Вы не имеете права на `изменение никнейма`. Попросите участника с правом на `управление никнеймами` разрешить смену ника.\n{string}")
            embed.set_footer(text="Время ожидания: 5 минут.")
            
            class NickButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                    self.value = None

                @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
                async def confirm(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if viewinteract.user.guild_permissions.manage_nicknames:
                        self.value = True
                        try:
                            await interaction.user.edit(nick=argument, reason=f"Одобрено // {viewinteract.user}")
                        except Forbidden:
                            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права `управление никнеймами`.\nКод ошибки: `Forbidden`.")
                            return await interaction.edit_original_response(embed=embed, view=None)
                        else:
                            embed = None
                            if argument is not None:
                                embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Ваш ник успешно изменён на `{argument}`!", timestamp=datetime.datetime.now())
                                embed.set_author(name=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                            else:
                                embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ваш ник успешно сброшен!", timestamp=datetime.datetime.now())
                                embed.set_author(name=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                            await interaction.edit_original_response(embed=embed, view=None)
                    else:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управлять никнеймами` для использования кнопки!")
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)

                @discord.ui.button(emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red)
                async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    if viewinteract.user.guild_permissions.manage_nicknames:
                        self.value = False
                        embed = discord.Embed(title="Отказ", color=discord.Color.red(), description="Вам отказано в смене ника!")
                        embed.set_author(name=viewinteract.user, icon_url=viewinteract.user.display_avatar.url)
                        return await interaction.edit_original_response(embed=embed, view=None)
                    else:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управлять никнеймами` для использования кнопки!")
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
            
            await interaction.response.send_message(embed=embed, view=NickButtons())
            await NickButtons().wait()
            if NickButtons().value is None:
                embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
                await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(name="getemoji", description="[Полезности] Выдает эмодзи картинкой.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(emoji_name="Название, ID либо сам эмодзи.", is_registry="Стоит ли учитывать регистр имени?")
    async def getemoji(self, interaction: discord.Interaction, emoji_name: str, is_registry: bool = False):
        if emoji_name.startswith("<") and emoji_name.endswith(">"):
            emoji_id = int(emoji_name.removesuffix(">").split(":")[2])
            emoji = self.bot.get_emoji(emoji_id)
            if emoji is None:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Данный эмодзи не обнаружен! Убедитесь, что бот есть на сервере, на котором есть эмодзи!"
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            embed = discord.Embed(title="🤪 Информация об эмодзи", color=discord.Color.orange(), description=f"[Скачать]({emoji.url})")
            embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
            embed.add_field(name="Вид без форматирования:", value=f"```\n{str(emoji)}```")
            embed.set_footer(text=f"ID: {emoji.id}")
            embed.set_thumbnail(url=emoji.url)
            return await interaction.response.send_message(embed=embed)
        if emoji_name.isdigit():
            emoji_id = int(emoji_name)
            emoji = self.bot.get_emoji(emoji_id)
            if emoji is None:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Данный эмодзи не обнаружен! Убедитесь, что бот есть на сервере, на котором есть эмодзи!"
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            embed = discord.Embed(title="🤪 Информация об эмодзи", color=discord.Color.orange(), description=f"[Скачать]({emoji.url})")
            embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
            embed.add_field(name="Вид без форматирования:", value=f"```\n{str(emoji)}```")
            embed.set_footer(text=f"ID: {emoji.id}")
            embed.set_thumbnail(url=emoji.url)
            return await interaction.response.send_message(embed=embed)
        embeds = []
        for emoji in interaction.guild.emojis:
            x = emoji.name
            y = emoji_name
            z = str(emoji)
            if not is_registry:
                x = x.lower()
                y = y.lower()
                z = z.lower()
            if x == y or str(emoji.id) == y or z == y:
                try:
                    embed = discord.Embed(title="🤪 Информация об эмодзи", color=discord.Color.orange(), description=f"[Скачать]({emoji.url})")
                    embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
                    embed.add_field(name="Вид без форматирования:", value=f"```\n{str(emoji)}```")
                    embed.set_footer(text=f"ID: {emoji.id}")
                    embed.set_thumbnail(url=emoji.url)
                    if len(embeds) == 9:
                        embed.set_footer(text="Это максимальное кол-во эмодзи, которое может быть выведено за раз.")
                    if len(embeds) != 10:
                        embeds.append(embed)
                except Forbidden:
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет доступа к файлу эмодзи.\nТип ошибки: `Forbidden`.")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Эмодзи с данным именем не был обнаружен!\nТип ошибки: `NotFound`.")
        if not len(embeds): return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(embeds=embeds)

    @app_commands.command(name="send", description="[Полезности] Отправляет сообщение в канал от имени вебхука")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(message="Сообщение, которое будет отправлено")
    async def send(self, interaction: discord.Interaction, message: app_commands.Range[str, None, 2000]):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.Thread):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда недоступна в ветках!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.channel.permissions_for(interaction.guild.get_member(self.bot.user.id)).manage_webhooks == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на управление вебхуками!\nТип ошибки: `Forbidden`.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        webhook = None
        webhooks = await interaction.channel.webhooks()
        for hook in webhooks:
            if hook.name == "MadWebHook":
                webhook = hook
                break
        if webhook is None: webhook = await interaction.channel.create_webhook(name="MadWebHook")
        await webhook.send(
            message, 
            username=interaction.user.display_name, 
            avatar_url=interaction.user.display_avatar.url,
            allowed_mentions=discord.AllowedMentions.none()
        )
        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Сообщение успешно отправлено!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="getaudit", description="[Полезности] Получает информацию о кол-ве модерационных действий пользователя.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, чьё кол-во действий вы хотите увидить")
    async def getaudit(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.guild_permissions.view_audit_log:
            member_bot = interaction.guild.get_member(self.bot.user.id)
            if not member_bot.guild_permissions.view_audit_log:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет доступа к журналу аудита!\nТип ошибки: `Forbidden`.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            embed = discord.Embed(title="В процессе...", color=discord.Color.yellow(), description=f"Собираем действия участника {member.mention}...")
            await interaction.response.send_message(embed=embed)
            entries = [entry async for entry in interaction.guild.audit_logs(limit=None, user=member)]
            embed = discord.Embed(title="Готово!", color=discord.Color.green(), description=f"Бот смог насчитать `{len(entries)}` действий от участника {member.mention}.")
            await interaction.edit_original_response(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `просмотр журнала аудита` для выполнения этой команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="weather", description="[Полезности] Узнать погоду в городе.")
    @app_commands.describe(city="Город, где надо узнать погоду")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def weather(self, interaction: discord.Interaction, city: str):
        city = city.replace(' ', '%20')
        embed = discord.Embed(title="Поиск...", color=discord.Color.yellow(), description="Ищем ваш город...")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={settings['weather_key']}&units=metric&lang=ru")
        json = response.json()
        if response.status_code > 400:
            if json['message'] == "city not found":
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Город не найден!")
                return await interaction.edit_original_response(embed=embed)
            else:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось узнать погоду! Код ошибки: `{json['cod']}`")
                print(f"{json['cod']}: {json['message']}")
                return await interaction.edit_original_response(embed=embed)
        else:
            embed = discord.Embed(title=f"Погода в {json['name']}", color=discord.Color.orange(), description=f"{json['weather'][0]['description']}", url=f"https://openweathermap.org/city/{json['id']}")
            embed.add_field(name="Температура:", value=f"{int(json['main']['temp'])}°С ({int(json['main']['temp_min'])}°С / {int(json['main']['temp_max'])}°С)")
            embed.add_field(name="Ощущается как:", value=f"{int(json['main']['feels_like'])}°С")
            embed.add_field(name="Влажность:", value=f"{json['main']['humidity']}%")
            embed.add_field(name="Скорость ветра:", value=f"{json['wind']['speed']}м/сек")
            embed.add_field(name="Облачность:", value=f"{json['clouds']['all']}%")
            embed.add_field(name="Рассвет/Закат:", value=f"<t:{json['sys']['sunrise']}> / <t:{json['sys']['sunset']}>")
            embed.set_footer(text="В целях конфиденциальности, ответ виден только вам. Бот не сохраняет информацию о запрашиваемом городе.")
            embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{json['weather'][0]['icon']}@2x.png")
            await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="stopwatch", description="[Полезности] Секундомер.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def stopwatch(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Секундомер", color=discord.Color.orange(), description=f"Время пошло!\nСекундомер запущен {discord.utils.format_dt(datetime.datetime.now(), 'R')}")
        embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)\

        class Button(discord.ui.View):
            def __init__(self, start):
                super().__init__(timeout=None)
                self.start = start

            @discord.ui.button(label="Стоп", style=discord.ButtonStyle.danger)
            async def callback(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != viewinteract.user.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                stop = time.time() - self.start
                embed = discord.Embed(title="Секундомер остановлен!", color=discord.Color.red(), description=f"Насчитанное время: `{round(stop, 3)}s`.")
                embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                button.disabled = True
                await viewinteract.response.edit_message(embed=embed, view=self)

        start = time.time()
        await interaction.response.send_message(embed=embed, view=Button(start))

    @app_commands.command(name="debug", description="[Полезности] Запрос основной информации о боте.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.checks.dynamic_cooldown(lambda i: app_commands.Cooldown(1, 300.0))
    async def debug(self, interaction: discord.Interaction):
        def get_permissions(perms: discord.Permissions):
            ans = ""
            ans += f"✅ Отправка сообщений\n" if perms.send_messages else f"❌ Отправка сообщений\n"
            ans += f"✅ Добавление ссылок\n" if perms.embed_links else f"❌ Добавление ссылок\n"
            ans += f"✅ Использование внешних эмодзи\n" if perms.use_external_emojis else f"❌ Использование внешних эмодзи\n"
            ans += f"✅ Управление каналами\n" if perms.manage_channels else f"❌ Управление каналами\n"
            ans += f"✅ Исключение участников\n" if perms.kick_members else f"❌ Исключение участников\n"
            ans += f"✅ Блокировка участников\n" if perms.ban_members else f"❌ Блокировка участников\n"
            ans += f"✅ Чтение истории сообщений\n" if perms.read_message_history else f"❌ Чтение истории сообщений\n"
            ans += f"✅ Чтение сообщений\n" if perms.read_messages else f"❌ Чтение сообщений\n"
            ans += f"✅ Управление участниками\n" if perms.moderate_members else f"❌ Управление участниками\n"
            ans += f"✅ Управление никнеймами\n" if perms.manage_nicknames else f"❌ Управление никнеймами\n"
            ans += f"✅ Управление сообщениями\n" if perms.manage_messages else f"❌ Управление сообщениями\n"
            ans += f"✅ Создание приглашений\n" if perms.create_instant_invite else f"❌ Создание приглашений\n"
            ans += f"✅ Управление сервером\n" if perms.manage_guild else f"❌ Управление сервером\n"
            ans += f"✅ Управление вебхуками\n" if perms.manage_webhooks else f"❌ Управление вебхуками\n"
            ans += f"✅ Журнал аудита\n" if perms.view_audit_log else f"❌ Журнал аудита\n"
            return ans

        embed = discord.Embed(title="Отладка", color=discord.Color.orange())
        bot_member = await interaction.guild.fetch_member(self.bot.user.id)
        user = await interaction.guild.fetch_member(interaction.user.id)
        embed.add_field(
            name="Права бота",
            value=get_permissions(bot_member.guild_permissions)
        )
        embed.add_field(
            name="Права в этом канале",
            value=get_permissions(interaction.channel.permissions_for(bot_member))
        )
        embed.add_field(
            name="Информация о сервере",
            value=(f"Имя канала:\n`{interaction.channel.name}`\nID канала:\n`{interaction.channel.id}`\n" +
                f"Кол-во каналов:\n`{len(interaction.guild.channels)}/500`\n" + 
                f"Название сервера:\n`{interaction.guild.name}`\nID сервера:\n`{interaction.guild.id}`"
            )
        )
        ans = ''
        ans += f"✅ Создатель\n" if interaction.guild.owner_id == interaction.user.id else f"❌ Создатель\n"
        ans += f"✅ Администратор\n" if user.guild_permissions.administrator else f"❌ Администратор\n"
        embed.add_field(
            name="Информация о пользователе",
            value=f"Пользователь:\n`{interaction.user}`\nID пользователя:\n`{interaction.user.id}`\nПрава:\n`{ans}`"
        )
        channel = self.bot.get_channel(settings['debug_channel'])
        message = await channel.send(embed=embed)
        await interaction.response.send_message(content=f"Если поддержка запросила ссылку с команды, отправьте ей это: {message.jump_url}",embed=embed)

    @app_commands.command(name="buttonrole", description="[Полезности] Настроить выдачу ролей по нажатию кнопки.")
    @app_commands.checks.dynamic_cooldown(hard_cooldown)
    @app_commands.describe(
        role1='Роль для выдачи', 
        role2='Роль для выдачи',
        role3='Роль для выдачи',
        role4='Роль для выдачи',
        role5='Роль для выдачи',
        role6='Роль для выдачи',
        role7='Роль для выдачи',
        role8='Роль для выдачи',
        role9='Роль для выдачи',
        role10='Роль для выдачи',
        role11='Роль для выдачи',
        role12='Роль для выдачи',
        role13='Роль для выдачи',
        role14='Роль для выдачи',
        role15='Роль для выдачи',
        role16='Роль для выдачи',
        role17='Роль для выдачи',
        role18='Роль для выдачи',
        role19='Роль для выдачи',
        role20='Роль для выдачи',
        role21='Роль для выдачи',
        role22='Роль для выдачи',
        role23='Роль для выдачи',
        role24='Роль для выдачи',
        role25='Роль для выдачи'
    )
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    async def buttonrole(
        self, 
        interaction: discord.Interaction,
        role1: discord.Role, 
        role2: typing.Optional[discord.Role],
        role3: typing.Optional[discord.Role],
        role4: typing.Optional[discord.Role],
        role5: typing.Optional[discord.Role],
        role6: typing.Optional[discord.Role],
        role7: typing.Optional[discord.Role],
        role8: typing.Optional[discord.Role],
        role9: typing.Optional[discord.Role],
        role10: typing.Optional[discord.Role],
        role11: typing.Optional[discord.Role],
        role12: typing.Optional[discord.Role],
        role13: typing.Optional[discord.Role],
        role14: typing.Optional[discord.Role],
        role15: typing.Optional[discord.Role],
        role16: typing.Optional[discord.Role],
        role17: typing.Optional[discord.Role],
        role18: typing.Optional[discord.Role],
        role19: typing.Optional[discord.Role],
        role20: typing.Optional[discord.Role],
        role21: typing.Optional[discord.Role],
        role22: typing.Optional[discord.Role],
        role23: typing.Optional[discord.Role],
        role24: typing.Optional[discord.Role],
        role25: typing.Optional[discord.Role]
    ):
        if interaction.guild is None:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True) 
        if interaction.user.guild_permissions.manage_roles:
            bot_member = interaction.guild.get_member(self.bot.user.id)
            if not(bot_member.guild_permissions.manage_roles):
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Бот не имеет права `управлять ролями`, что необходимо для работы команды!"
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            title = ""
            description = ""
            color = discord.Color.orange()
            roles = [
                role1, role2, role3, role4, role5,
                role6, role7, role8, role9, role10,
                role11, role12, role13, role14, role15,
                role16, role17, role18, role19, role20,
                role21, role22, role23, role24, role25
            ]
            class View(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
            view = View()
            options = []
            for role in roles:
                role: discord.Role
                if role is not None:
                    if role.position == 0:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Ты кому собираешься выдавать @everyone?)"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    if bot_member.top_role <= role:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description=f"Роль {role.mention} выше роли бота, поэтому бот не сможет выдать её кому-либо."
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    if not role.is_assignable():
                        embed = discord.Embed(
                            title="Ошибка!", 
                            color=discord.Color.red(),
                            description=f"Роль {role.mention} является ролью интеграции, поэтому выдать её кому-либо нельзя!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    options.append(
                        discord.SelectOption(
                            label=f"{role.name}",
                            value=str(role.id),
                            description="Выберите это пункт, чтобы взять/убрать роль."
                        )
                    )
            if len(options) == 1:
                view.add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.green, 
                        label=role1.name,
                        custom_id=str(role1.id)
                    )
                )
            else:
                view.add_item(
                    discord.ui.Select(
                        custom_id=str(interaction.guild.id),
                        placeholder="Выберите роли",
                        max_values=len(options),
                        options=options
                    )
                )
            
            class Input(discord.ui.Modal, title="Кастомизация эмбеда"):
                main = discord.ui.TextInput(label="Заголовок эмбеда:", max_length=256)
                description = discord.ui.TextInput(label="Описание:", max_length=4000, style=discord.TextStyle.long)
                color = discord.ui.TextInput(label="Цвет (по умолчанию - оранжевый):", min_length=7, max_length=7, required=False, placeholder="#FFFFFF")
                async def on_submit(self, viewinteract: discord.Interaction) -> None:
                    nonlocal title, description, color
                    await viewinteract.response.defer()
                    title = str(self.main)
                    description = str(self.description)
                    if str(self.color) != "": color = str(self.color)
            modal = Input()
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.main is None or modal.description is None: return
            if isinstance(color, str):
                try:
                    color = discord.Color.from_str(color)
                except:
                    embed = discord.Embed(
                        title="Ошибка!",
                        color=discord.Color.red(),
                        description="Цвет введён неверно!"
                    )
                    return await interaction.followup.send(embed=embed, ephemeral=True)

            class AcceptRules(discord.ui.View):
                def __init__(self, bot: commands.Bot):
                    super().__init__(timeout=60)
                    self.value = None
                    self.bot = bot
                
                @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
                async def accept(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    nonlocal view
                    self.value = True
                    embed = discord.Embed(
                        title=title,
                        color=color,
                        description=description
                    )
                    embed.set_footer(text=f"Создал: {interaction.user}", icon_url=interaction.user.display_avatar.url)
                    try:
                        await viewinteract.channel.send(embed=embed, view=view)
                    except:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не имеет права на отправку сообщения в этом канале!")
                        return await viewinteract.response.edit_message(embed=embed, view=None)
                    log_channel = self.bot.get_channel(settings['log_channel'])
                    await log_channel.send(content=f"`{interaction.user}` на сервере `{interaction.guild.name}` создал выдачу ролей! Их эмбед:", embed=embed)
                    embed = discord.Embed(
                        title="Успешно!",
                        color=discord.Color.green(),
                        description="Выдача ролей успешно настроена!"
                    )
                    await viewinteract.response.edit_message(embed=embed, view=None)
                
                @discord.ui.button(style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>")
                async def deny(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                    self.value = False
                    embed = discord.Embed(title="Отмена!", color=discord.Color.red(), description="Выдача ролей по реакциям отменена!")
                    await viewinteract.response.edit_message(embed=embed, view=None)
            
            embed = discord.Embed(
                title="Обязательно к прочтению!",
                color=discord.Color.orange(),
                description=f"Мы, простые разработчики бота, просим не использовать в кастомизированном эмбеде что-либо, нарушающее правила Discord. В противном случае, Ваш сервер и Ваш аккаунт будут занесены в черный список бота.\nВы согласны с требованиями?"
            )
            waiting = AcceptRules(bot=self.bot)
            msg_bot = await interaction.followup.send(embed=embed, ephemeral=True, view=waiting)
            await waiting.wait()
            if waiting.value is None:
                embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
                await msg_bot.edit(embed=embed, view=None)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управлять ролями` для использования команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="calc", description="[Полезности] Калькулятор в Discord.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(problem="Пример для решения")
    async def calc(self, interaction: discord.Interaction, problem: app_commands.Range[str, None, 30]):
        if "**" in problem:
            embed = discord.Embed(
                title='Ошибка!',
                color=discord.Color.red(),
                description="Использование степени запрещено!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            answer = numexpr.evaluate(problem)
        except ZeroDivisionError:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(),
                description="Расскажу-ка тебе секрет. На ноль делить нельзя."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Пример введён некорректно!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Калькулятор",
                color=discord.Color.orange(),
                description=f"Ваш пример: `{problem}`\nОтвет: `{answer}`"
            )
            embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="autorole", description="Настроить выдачу одной роли при входе на сервер")
    @app_commands.describe(role="Роль для выдачи. Не указывайте её для удаления.")
    @app_commands.checks.dynamic_cooldown(hard_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def autorole(self, interaction: discord.Interaction, role: typing.Optional[discord.Role]):
        loader = FluentResourceLoader("locales/{locale}")
        l10n = FluentLocalization(["ru"], ["main.ftl", "texts.ftl", "commands.ftl"], loader)
        if interaction.guild is None:
            embed = discord.Embed(title=l10n.format_value("error_title"), color=discord.Color.red(), description=l10n.format_value("guild_only_error"))
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True) 
        if not self.bot.intents.members:
            embed = discord.Embed(
                title=l10n.format_value("error_title"),
                color=discord.Color.red(),
                description=l10n.format_value("intents_are_not_enabled")
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.guild_permissions.manage_guild:
            role_info = db.get_guild_autorole(interaction.guild.id)
            if role is None:
                if role_info is None:
                    embed = discord.Embed(
                        title=l10n.format_value("error_title"),
                        color=discord.Color.red(),
                        description=l10n.format_value("autorole_no_active_role")
                    )
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                class Buttons(ui.View):
                    def __init__(self):
                        super().__init__(timeout=180)
                        self.value = None

                    @ui.button(label=l10n.format_value("yes"), style=discord.ButtonStyle.green)
                    async def yes(self, viewinteract: discord.Interaction, button: ui.Button):
                        if viewinteract.user.id != interaction.user.id:
                            return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                        await viewinteract.response.defer()
                        self.value = True
                        self.stop()

                    @ui.button(label=l10n.format_value("no"), style=discord.ButtonStyle.red)
                    async def no(self, viewinteract: discord.Interaction, button: ui.Button):
                        if viewinteract.user.id != interaction.user.id:
                            return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                        await viewinteract.response.defer()
                        self.value = True
                        self.stop()

                embed = discord.Embed(
                    title=l10n.format_value("autorole_confirm_title"),
                    color=discord.Color.orange(),
                    description=l10n.format_value("autorole_confirm_deletion", {"role": f"<@&{role_info}>"})
                )
                view = Buttons()
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await view.wait()
                if view.value is None:
                    embed = discord.Embed(
                        title=l10n.format_value("time_exceeded"),
                        color=discord.Color.red()
                    )
                    return await interaction.edit_original_response(embed=embed, view=None)
                if not view.value:
                    return await interaction.delete_original_response()
                db.delete_guild_autorole(interaction.guild.id)
                embed = discord.Embed(
                    title=l10n.format_value("success"),
                    color=discord.Color.green(),
                    description=l10n.format_value("autorole_deletion_success", {"role": f"<@&{role_info}>"})
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if role_info is None:
                db.add_guild_autorole(interaction.guild.id, role.id)
                embed = discord.Embed(
                    title=l10n.format_value("success"),
                    color=discord.Color.green(),
                    description=l10n.format_value("autorole_add_success", {"role": f"<@&{role.id}>"})
                )
                return await interaction.response.send_message(embed=embed)
            class Buttons(ui.View):
                def __init__(self):
                    super().__init__(timeout=180)
                    self.value = None

                @ui.button(label=l10n.format_value("yes"), style=discord.ButtonStyle.green)
                async def yes(self, viewinteract: discord.Interaction, button: ui.Button):
                    if viewinteract.user.id != interaction.user.id:
                        return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                    await viewinteract.response.defer()
                    self.value = True
                    self.stop()

                @ui.button(label=l10n.format_value("no"), style=discord.ButtonStyle.red)
                async def no(self, viewinteract: discord.Interaction, button: ui.Button):
                    if viewinteract.user.id != interaction.user.id:
                        return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                    await viewinteract.response.defer()
                    self.value = True
                    self.stop()

            embed = discord.Embed(
                title=l10n.format_value("autorole_confirm_title"),
                color=discord.Color.orange(),
                description=l10n.format_value("autorole_confirm_update", {"role1": f"<@&{role_info}>", "role2": f"<@&{role.id}>"})
            )
            view = Buttons()
            await interaction.response.send_message(embed=embed, view=view)
            await view.wait()
            if view.value is None:
                embed = discord.Embed(
                    title=l10n.format_value("time_exceeded"),
                    color=discord.Color.red()
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if not view.value:
                return await interaction.delete_original_response()
            db.update_guild_autorole(interaction.guild.id, role.id)
            embed = discord.Embed(
                title=l10n.format_value("success"),
                color=discord.Color.green(),
                description=l10n.format_value("autorole_update_success", {"role1": f"<@&{role_info}>", "role2": f"<@&{role.id}>"})
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title=l10n.format_value("error_title"),
                color=discord.Color.red(),
                description=l10n.format_value("perms_required_error", {"perm": l10n.format_value("perms_manage_server").lower()})            
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tools(bot))
    print('Cog "Tools" запущен!')
