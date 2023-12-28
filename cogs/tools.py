# -*- coding: utf-8 -*-
import discord
import datetime
import typing
import aiohttp
import numexpr  # type: ignore
import logging

from discord import Forbidden, app_commands, ui
from fluent.runtime import FluentLocalization, FluentResourceLoader
from discord.ext import commands
from typing import Optional

from classes.checks import isPremium, isPremiumServer
from classes import db
from classes import checks
import config
import time

logger = logging.getLogger('discord')


async def default_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (await isPremium(interaction.client, interaction.user.id) != 'None' or  # type: ignore
            await isPremiumServer(interaction.client, interaction.guild)):  # type: ignore
        return None
    return app_commands.Cooldown(1, 3.0)


async def hard_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if (await isPremium(interaction.client, interaction.user.id) != 'None' or  # type: ignore
            await isPremiumServer(interaction.client, interaction.guild)):  # type: ignore
        return app_commands.Cooldown(1, 2.0)
    return app_commands.Cooldown(1, 10.0)


class Tools(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
    
    @app_commands.command(name="badgeinfo", description="[Полезности] Информация о значках пользователей и серверов в боте.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def badgeinfo(self, interaction: discord.Interaction):
        embed=discord.Embed(title="Виды значков:", color=discord.Color.orange())
        embed.add_field(name="Значки пользователя:", value=f"<:ban:946031802634612826> - пользователь забанен в системе бота.\n<a:premium:988735181546475580> - пользователь имеет MadBot Premium.\n<:timeout:950702768782458893> - пользователь получил тайм-аут на сервере.\n<:botdev:977645046188871751> - разработчик бота.\n<:code:946056751646638180> - помощник разработчика.\n<:support:946058006641143858> - поддержка бота.\n<:bug_hunter:955497457020715038> - охотник на баги (обнаружил и сообщил о 3-х и более багах).\n<:bug_terminator:955891723152801833> - уничтожитель багов (обнаружил и сообщил о 10-ти и более багах).\n<:verified:946057332389978152> - верифицированный пользователь.\n<:bot:946064625525465118> - участник является ботом.", inline=False)
        embed.add_field(name="Значки сервера:", value=f"<:verified:946057332389978152> - верифицированный сервер.\n<a:premium:988735181546475580> - сервер имеет MadBot Premium.\n<:ban:946031802634612826> - сервер забанен в системе бота.\n<:beta:946063731819937812> - сервер, имеющий доступ к бета-командам.", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nick", description="[Полезности] Изменяет ваш ник.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(argument="Ник, на который вы хотите поменять. Оставьте пустым для сброса ника")
    async def nick(self, interaction: discord.Interaction, argument: str | None = None):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not self.bot.intents.members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="На данный момент, команда недоступна."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert self.bot.user is not None
        bot_member = await interaction.guild.fetch_member(self.bot.user.id)
        assert isinstance(interaction.user, discord.Member)
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
            if interaction.user.id == interaction.guild.owner_id:
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
                async def confirm(self, viewinteract: discord.Interaction, button: discord.ui.Button):  # type: ignore
                    assert isinstance(viewinteract.user, discord.Member)
                    assert isinstance(interaction.user, discord.Member)
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
                async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):  # type: ignore
                    assert isinstance(viewinteract.user, discord.Member)
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
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
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
        embeds: list[discord.Embed] = []
        assert interaction.guild is not None
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
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(message="Сообщение, которое будет отправлено")
    async def send(self, interaction: discord.Interaction, message: app_commands.Range[str, None, 2000]):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.Thread):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда недоступна в ветках!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert interaction.channel is not None
        assert self.bot.user is not None
        if interaction.channel.permissions_for(interaction.guild.get_member(self.bot.user.id)).manage_webhooks == False:  # type: ignore
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на управление вебхуками!\nТип ошибки: `Forbidden`.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        webhook = None
        assert isinstance(interaction.channel, discord.TextChannel)
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
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, чьё кол-во действий вы хотите увидить")
    async def getaudit(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if interaction.user.guild_permissions.view_audit_log:
            assert self.bot.user is not None
            member_bot = await interaction.guild.fetch_member(self.bot.user.id)
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
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def weather(self, interaction: discord.Interaction, city: str):
        city = city.replace(' ', '%20')
        embed = discord.Embed(title="Поиск...", color=discord.Color.yellow(), description="Ищем ваш город...")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        response = await aiohttp.ClientSession().get(
            "https://api.openweathermap.org/data/2.5/weather?q={city}&APPID={settings['weather_key']}&units=metric&lang=ru"
        )
        json = await response.json()
        if response.status > 400:
            if json.get('message', "") == "city not found":
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Город не найден!")
                return await interaction.edit_original_response(embed=embed)
            else:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось узнать погоду! Код ошибки: `{json['cod']}`")
                logger.error(f"{json['cod']}: {json['message']}")
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
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def stopwatch(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Секундомер", color=discord.Color.orange(), description=f"Время пошло!\nСекундомер запущен {discord.utils.format_dt(datetime.datetime.now(), 'R')}")
        embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)\

        class Button(discord.ui.View):
            def __init__(self, start: float):
                super().__init__(timeout=None)
                self.start = start

            @discord.ui.button(label="Стоп", style=discord.ButtonStyle.danger)
            async def callback(self, viewinteract: discord.Interaction, button: discord.ui.Button):  # type: ignore
                if interaction.user.id != viewinteract.user.id:
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                stop = time.time() - self.start
                embed = discord.Embed(title="Секундомер остановлен!", color=discord.Color.red(), description=f"Насчитанное время: `{stop:.3f}s`.")
                embed.set_footer(text=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                button.disabled = True
                await viewinteract.response.edit_message(embed=embed, view=self)

        start = time.time()
        await interaction.response.send_message(embed=embed, view=Button(start))

    @app_commands.command(name="debug", description="[Полезности] Запрос основной информации о боте.")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.checks.dynamic_cooldown(lambda i: app_commands.Cooldown(1, 300.0))
    async def debug(self, interaction: discord.Interaction):
        def get_permissions(perms: discord.Permissions) -> str:
            perms_: tuple[tuple[bool, str], ...] = (
                (perms.send_messages, "Отправка сообщений"),
                (perms.embed_links, "Добавление ссылок"),
                (perms.use_external_emojis, "Использование внешних эмодзи"),
                (perms.manage_channels, "Управление каналами"),
                (perms.kick_members, "Исключение участников"),
                (perms.ban_members, "Блокировка участников"),
                (perms.read_message_history, "Чтение истории сообщений"),
                (perms.read_messages, "Чтение сообщений"),
                (perms.moderate_members, "Управление участниками"),
                (perms.manage_nicknames, "Управление никнеймами"),
                (perms.manage_messages, "Управление сообщениями"),
                (perms.create_instant_invite, "Создание приглашений"),
                (perms.manage_guild, "Управление сервером"),
                (perms.manage_webhooks, "Управление вебхуками"),
                (perms.view_audit_log, "Журнал аудита")
            )

            #? It can be done in a oneline, but I think it's too messy and unreadable
            output: list[str] = []
            for i in perms_:
                output.append(("✅ " if i[0] else "❌ ") + i[1])
            return "\n".join(output)

        def get_vals() -> str:  # TODO rename
            assert interaction.guild is not None
            perms_ = (
                (interaction.guild.owner_id == interaction.user.id, "Создатель"),
                (user.guild_permissions.administrator, "Администратор")
            )

            #? It can be done in a oneline, but I think it's too messy and unreadable
            output: list[str] = []
            for i in perms_:
                output.append(("✅ " if i[0] else "❌ ") + i[1])
            return "\n".join(output)

        assert interaction.guild is not None
        assert isinstance(interaction.channel, discord.TextChannel)
        assert self.bot.user is not None
        bot_member = await interaction.guild.fetch_member(self.bot.user.id)
        user = await interaction.guild.fetch_member(interaction.user.id)
        embed = discord.Embed(title="Отладка", color=discord.Color.orange()).add_field(
            name="Права бота",
            value=get_permissions(bot_member.guild_permissions)
        ).add_field(
            name="Права в этом канале",
            value=get_permissions(interaction.channel.permissions_for(bot_member))
        ).add_field(
            name="Информация о сервере",
            value=(f"Имя канала:\n`{interaction.channel.name}`\nID канала:\n`{interaction.channel.id}`\n" +
                f"Кол-во каналов:\n`{len(interaction.guild.channels)}/500`\n" + 
                f"Название сервера:\n`{interaction.guild.name}`\nID сервера:\n`{interaction.guild.id}`"
            )
        ).add_field(
            name="Информация о пользователе",
            value=f"Пользователь:\n`{interaction.user}`\nID пользователя:\n`{interaction.user.id}`\nПрава:\n`{get_vals()}`"
        )
        channel = self.bot.get_channel(config.settings['debug_channel'])
        assert isinstance(channel, discord.TextChannel)
        message = await channel.send(embed=embed)
        await interaction.response.send_message(content=f"Если поддержка запросила ссылку с команды, отправьте ей это: {message.jump_url}",embed=embed)

    @app_commands.command(name="calc", description="[Полезности] Калькулятор в Discord.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
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
            answer = numexpr.evaluate(problem)  # type: ignore
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
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def autorole(self, interaction: discord.Interaction, role: typing.Optional[discord.Role]):
        loader = FluentResourceLoader("locales/{locale}")
        l10n = FluentLocalization(["ru"], ["main.ftl", "texts.ftl", "commands.ftl"], loader)
        if interaction.guild is None:
            embed = discord.Embed(title=l10n.format_value("error_title"), color=discord.Color.red(), description=l10n.format_value("guild_only_error"))
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True) 
        if not self.bot.intents.members:
            embed = discord.Embed(
                title=l10n.format_value("error_title"),
                color=discord.Color.red(),
                description=l10n.format_value("intents_are_not_enabled")
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if interaction.user.guild_permissions.manage_guild:
            role_info = await db.get_guild_autorole(interaction.guild.id)
            if role is None:
                if role_info is None:
                    embed = discord.Embed(
                        title=l10n.format_value("error_title"),
                        color=discord.Color.red(),
                        description=l10n.format_value("autorole_no_active_role")
                    )
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                class Buttons1(ui.View):  # Error: Объявление класса "Buttons" скрывается объявлением с тем же именем  # TODO rename
                    def __init__(self):
                        super().__init__(timeout=180)
                        self.value = None

                    @ui.button(label=l10n.format_value("yes"), style=discord.ButtonStyle.green)
                    async def yes(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                        if viewinteract.user.id != interaction.user.id:
                            return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                        await viewinteract.response.defer()
                        self.value = True
                        self.stop()

                    @ui.button(label=l10n.format_value("no"), style=discord.ButtonStyle.red)
                    async def no(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
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
                view = Buttons1()
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
                await db.delete_guild_autorole(interaction.guild.id)
                embed = discord.Embed(
                    title=l10n.format_value("success"),
                    color=discord.Color.green(),
                    description=l10n.format_value("autorole_deletion_success", {"role": f"<@&{role_info}>"})
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if role_info is None:
                await db.add_guild_autorole(interaction.guild.id, role.id)
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
                async def yes(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                    if viewinteract.user.id != interaction.user.id:
                        return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                    await viewinteract.response.defer()
                    self.value = True
                    self.stop()

                @ui.button(label=l10n.format_value("no"), style=discord.ButtonStyle.red)
                async def no(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
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
            await db.update_guild_autorole(interaction.guild.id, role.id)
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

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Tools(bot))
