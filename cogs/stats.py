import discord
import logging

from discord.ext import commands
from discord import app_commands
from discord import ui
from typing import Optional

from classes.checks import isPremiumServer, isPremium
from classes import checks
from classes import db
from config import *

logger = logging.getLogger('discord')

async def default_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    assert interaction.guild is not None
    if (await isPremium(interaction.user.id) != 'None' or
            await isPremiumServer(interaction.guild)):
        return None
    return app_commands.Cooldown(1, 3.0)


async def hard_cooldown(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    assert interaction.guild is not None
    if (await isPremium(interaction.user.id) != 'None' or
            await isPremiumServer(interaction.guild)):
        return app_commands.Cooldown(1, 2.0)
    return app_commands.Cooldown(1, 10.0)


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stats-setup", description="[Статистика] Настройка статистики")
    @app_commands.checks.dynamic_cooldown(hard_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def stats_setup(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(),
                                  description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У Вас отсутствует право `управление каналами` для использования этой команды!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        """if not isPremiumServer(self.bot, interaction.guild):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда доступна только премиум серверам!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)"""
        guild = await db.get_guild_stats(guild_id=interaction.guild.id)  # type: ignore
        if guild is not None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Статистика уже создана! Используйте `/stats-edit` или `/stats-delete` для редактирования или удаления статистики."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(
            title="Выбор статистики",
            color=discord.Color.orange(),
            description="Пожалуйста, выберите, какую статистику Вы хотите видеть."
        )

        class Select(ui.Select):  # type: ignore
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label="Кол-во эмодзи",
                        value="emojis",
                        description="Показ кол-ва эмодзи на сервере.",
                        emoji="🤣"
                    ),
                    discord.SelectOption(
                        label="Кол-во участников в войсах",
                        value="voice",
                        description="Показ кол-ва участников в войсах сервера.",
                        emoji="🗣️"
                    )
                ]
                intent_options = [
                    discord.SelectOption(
                        label="Онлайн",
                        value="online",
                        description="Показ кол-ва людей онлайн.",
                        emoji="🟢"
                    ),
                    discord.SelectOption(
                        label="Кол-во участников",
                        value="members",
                        description="Показ кол-ва людей и ботов на сервере.",
                        emoji="👥"
                    ),
                    discord.SelectOption(
                        label="Кол-во людей",
                        value="people",
                        description="Показ кол-ва людей на сервере.",
                        emoji="👪"
                    ),
                    discord.SelectOption(
                        label="Кол-во ботов",
                        value="bots",
                        description="Показ кол-ва ботов на сервере.",
                        emoji="🤖"
                    )
                ]
                if interaction.client.intents.members and interaction.client.intents.presences: options = intent_options + options
                super().__init__(placeholder="Выберите статистику", max_values=len(options), options=options)

            async def callback(self, viewinteract: discord.Interaction):  # type: ignore
                assert viewinteract.guild is not None
                await viewinteract.response.defer(thinking=True, ephemeral=True)
                values = self.values
                channels: list[dict[str, str]] = []
                for value in values:
                    message = "%count%"
                    stat = 0
                    voices = sum(
                        len(voice.voice_states)
                        for voice in viewinteract.guild.voice_channels
                    )
                    bot = sum(bool(member.bot) for member in viewinteract.guild.members)
                    if value == 'bots':
                        message = "Ботов: %count%"
                        stat = bot
                    elif value == 'emojis':
                        message = "Эмодзи: %count%"
                        stat = len(viewinteract.guild.emojis)
                    elif value == 'members':
                        message = "Участников: %count%"
                        stat = viewinteract.guild.member_count
                    elif value == 'online':
                        message = "Онлайн: %count%"
                        stat = (
                                len(list(
                                    filter(lambda x: x.status == discord.Status.online, viewinteract.guild.members)))
                                + len(
                            list(filter(lambda x: x.status == discord.Status.idle, viewinteract.guild.members)))
                                + len(
                            list(filter(lambda x: x.status == discord.Status.dnd, viewinteract.guild.members)))
                        )
                    elif value == 'people':
                        message = "Людей: %count%"
                        stat = viewinteract.guild.member_count or 0 - bot
                    elif value == 'voice':
                        message = "В войсах: %count%"
                        stat = voices
                    try:
                        channel = await viewinteract.guild.create_voice_channel(
                            name=message.replace("%count%", str(stat)), position=0,
                            overwrites={viewinteract.guild.default_role: discord.PermissionOverwrite(connect=False)})
                    except:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права на `управление каналами`, которое нужно для бота."
                        )
                        return await viewinteract.followup.send(embed=embed)
                    channels.append({'type': value, 'id': str(channel.id), 'text': message})
                await db.add_guild_stats(
                    guild_id=viewinteract.guild.id,
                    next_update=int(time.time()) + 600,
                    channels=channels
                )
                embed = discord.Embed(
                    title="Успешно!",
                    color=discord.Color.green(),
                    description="Статистика создана!\n\n**Инструкция по дальнейшему использованию:**\n- Вы можете передвигать созданные каналы или перемещать их в категории, но Вы не можете переименовать их через Discord. Используйте для этого команду `/stats-edit`.\n- При удалении канала, он будет также удалён из обновления статистики.\n- При завершении премиум подписки у человека, давшего её Вам, бот перестанет обновлять статистику. Как только сервер снова получит премиум подписку, бот продолжить обновлять статистику."
                )
                await viewinteract.followup.send(embed=embed)
                await interaction.edit_original_response(view=None)


        class View(ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(Select())

        await interaction.response.send_message(embed=embed, view=View(), ephemeral=True)

    async def es_autocomplete(self, interaction: discord.Interaction, current: str):
        assert interaction.guild is not None
        channels = await db.get_guild_stats(  # type: ignore
            guild_id=interaction.guild.id,
            channels=1, 
            _id=0
        )['channels']
        return [app_commands.Choice(name=channel['text'].replace("%count%", ''), value=str(channel['id'])) for channel  # type: ignore
                in channels if current.lower() in channel['type']]

    @app_commands.command(
        name='stats-edit',
        description="[Статистика] Изменение названия канала, добавление или удаление одного из каналов"
    )
    @app_commands.autocomplete(channel=es_autocomplete)
    @app_commands.checks.dynamic_cooldown(hard_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(channel="Канал, который Вы хотите изменить или удалить.")
    async def edit_stats(self, interaction: discord.Interaction, channel: Optional[str]):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"
            ).set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы не имеете права на `управление каналами`, чтобы использовать эту команду!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        """if not await isPremiumServer(self.bot, interaction.guild):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Ваш сервер не имеет премиум подписки!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)"""
        guild = await db.get_guild_stats(guild_id=interaction.guild.id)  # type: ignore
        if guild is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Статистика отсутствует! Используйте `/stats-setup` для создания статистики."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if channel is not None:
            channel_: discord.abc.GuildChannel = self.bot.get_channel(int(channel))  # type: ignore
            channels: list[dict[str, str | int]] = guild['channels']  # type: ignore
            channel_it: dict[str, str | int] | None = None
            text = ''
            for ch in channels:  # type: ignore
                if int(ch['id']) == channel_.id:  # type: ignore
                    text = ch['text']  # type: ignore
                    channel_it = ch  # type: ignore
                    break
            embed = discord.Embed(
                title="Изменение канала",
                color=discord.Color.orange(),
                description="Пожалуйста, выберите действие с каналом.\n\n**Инструкция по переименованию:**\n- Необходимо указать `%count%`. Данный аргумент указывает боту, где должно стоять число статистики.\n- Запрещено ставить названия, нарушающие правила Discord. В случае попытки установки такого имени, Вам может быть выдан ЧС бота."
            )

            class Buttons(ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @ui.button(label="Переименовать", style=discord.ButtonStyle.green)
                async def rename(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                    class Input(ui.Modal, title="Переименование канала"):
                        txt = ui.TextInput(label="Название канала:", default=text, max_length=100, min_length=7)  # type: ignore

                        async def on_submit(self, minteract: discord.Interaction):
                            if str(self.txt).find("%count%") == -1:  # type: ignore
                                embed = discord.Embed(
                                    title="Ошибка!",
                                    color=discord.Color.red(),
                                    description="Необходимо указать `%count%`, которое будет показывать боту, куда ставить число со статистикой."
                                )
                                return await minteract.response.send_message(embed=embed, ephemeral=True)
                            channels.remove(channel_it)  # type: ignore
                            channel_it['text'] = str(self.txt)  # type: ignore
                            channels.append(channel_it)  # type: ignore
                            await db.update_guild_stats(guild_id=minteract.guild.id, channels=channels)  # type: ignore
                            embed = discord.Embed(
                                title="Успешно!",
                                color=discord.Color.green(),
                                description=f"Название канала изменено на `{str(self.txt).replace('%count%', '[число]')}`. Название изменится вместе со статистикой."  # type: ignore
                            )
                            await minteract.response.send_message(embed=embed, ephemeral=True)

                    await viewinteract.response.send_modal(Input())

                @ui.button(label="Удалить", style=discord.ButtonStyle.red)
                async def delete(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                    channels.remove(channel_it)  # type: ignore
                    await db.update_guild_stats(guild_id=viewinteract.guild.id, channels=channels)  # type: ignore
                    try:
                        await channel_.delete()
                    except:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права на `управление каналами`, которое нужно для бота.\n"
                            "Обратите внимание: канал, который Вы хотели удалить, больше не будет обновляться."
                        )
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                    embed = discord.Embed(
                        title="Успешно!",
                        color=discord.Color.green(),
                        description=f"Канал `{channel_.name}` удалён!"
                    )
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                    self.stop()

            return await interaction.response.send_message(embed=embed, ephemeral=True, view=Buttons())
        embed = discord.Embed(
            title="Статистика - Добавление канала",
            color=discord.Color.orange(),
            description=(
                "Вы собираетесь добавить новые каналы. Если Вы хотите изменить/удалить один канал - укажите его как аргумент. "
                "Если Вы хотите удалить статистику, используйте команду `/stats-delete`.")
        )

        class Select(ui.Select):  # type: ignore
            def __init__(self, guild_channels: list):  # type: ignore
                options = [
                    discord.SelectOption(
                        label="Кол-во эмодзи",
                        value="emojis",
                        description="Показ кол-ва эмодзи на сервере.",
                        emoji="🤣"
                    ),
                    discord.SelectOption(
                        label="Кол-во участников в войсах",
                        value="voice",
                        description="Показ кол-ва участников в войсах сервера.",
                        emoji="🗣️"
                    )
                ]
                intent_options = [
                    discord.SelectOption(
                        label="Онлайн",
                        value="online",
                        description="Показ кол-ва людей онлайн.",
                        emoji="🟢"
                    ),
                    discord.SelectOption(
                        label="Кол-во участников",
                        value="members",
                        description="Показ кол-ва людей и ботов на сервере.",
                        emoji="👥"
                    ),
                    discord.SelectOption(
                        label="Кол-во людей",
                        value="people",
                        description="Показ кол-ва людей на сервере.",
                        emoji="👪"
                    ),
                    discord.SelectOption(
                        label="Кол-во ботов",
                        value="bots",
                        description="Показ кол-ва ботов на сервере.",
                        emoji="🤖"
                    )
                ]
                if interaction.client.intents.members and interaction.client.intents.presences: options = intent_options + options
                channels = guild_channels  # type: ignore
                for channel in channels:  # type: ignore
                    for option in options:
                        if option.value == channel['type']: options.remove(option)
                super().__init__(placeholder="Выберите статистику", max_values=len(options), options=options)

            async def callback(self, viewinteract: discord.Interaction):  # type: ignore
                await viewinteract.response.defer(thinking=True, ephemeral=True)
                values = self.values
                channels = await db.get_guild_stats(guild_id=viewinteract.guild.id)['channels']  # type: ignore
                for value in values:
                    message = "%count%"
                    stat = 0
                    bot = 0
                    voices = 0
                    assert viewinteract.guild is not None
                    for voice in viewinteract.guild.voice_channels:
                        voices += len(voice.voice_states)
                    for member in viewinteract.guild.members:
                        if member.bot: bot += 1
                    if value == 'online':
                        message = "Онлайн: %count%"
                        stat = (
                                len(list(
                                    filter(lambda x: x.status == discord.Status.online, viewinteract.guild.members)))
                                + len(
                            list(filter(lambda x: x.status == discord.Status.idle, viewinteract.guild.members)))
                                + len(
                            list(filter(lambda x: x.status == discord.Status.dnd, viewinteract.guild.members)))
                        )
                    match value:
                        case 'members':
                            message = "Участников: %count%"
                            stat = viewinteract.guild.member_count
                    
                        case 'people': 
                            message = "Людей: %count%"
                            stat = viewinteract.guild.member_count or 0 - bot
                        case 'bots': 
                            message = "Ботов: %count%"
                            stat = bot
                        case 'emojis': 
                            message = "Эмодзи: %count%"
                            stat = len(viewinteract.guild.emojis)
                        case 'voice': 
                            message = "В войсах: %count%"
                            stat = voices
                        case _:
                            pass
                    try:
                        channel = await viewinteract.guild.create_voice_channel(
                            name=message.replace("%count%", str(stat)), position=0,
                            overwrites={viewinteract.guild.default_role: discord.PermissionOverwrite(connect=False)})
                    except:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права на `управление каналами`, которое нужно для бота."
                        )
                        return await viewinteract.followup.send(embed=embed)
                    channels.append({'type': value, 'id': str(channel.id), 'text': message})  # type: ignore
                await db.update_guild_stats(guild_id=viewinteract.guild.id, channels=channels)  # type: ignore
                embed = discord.Embed(
                    title="Успешно!",
                    color=discord.Color.green(),
                    description="Статистика добавлена!"
                )
                await viewinteract.followup.send(embed=embed)
                await interaction.edit_original_response(view=None)

        class View(ui.View):
            def __init__(self, guild_channels: list):  # type: ignore
                super().__init__(timeout=None)
                self.add_item(Select(guild_channels))

        guild_channels = await db.get_guild_stats(guild_id=interaction.guild.id)['channels']  # type: ignore
        await interaction.response.send_message(embed=embed, view=View(guild_channels), ephemeral=True)  # type: ignore

    @app_commands.command(name="stats-delete", description="[Статистика] Удалить статистику")
    @app_commands.checks.dynamic_cooldown(hard_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def stats_delete(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"
            ).set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы не имеете права `управлять каналами`, которое необходимо для использования команды!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        doc = await db.get_guild_stats(guild_id=interaction.guild.id)  # type: ignore
        if doc is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У Вас нету статистики! Для её создания пропишите `/stats-setup`."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.defer(thinking=True)
        for channel in doc['channels']:  # type: ignore
            ch = self.bot.get_channel(int(channel['id']))  # type: ignore
            if ch is None: continue
            assert isinstance(ch, discord.TextChannel)
            try:
                await ch.delete()
            except:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Бот не имеет права на `управление каналами`, которое нужно для бота."
                )
                return await interaction.followup.send(embed=embed)
        await db.delete_guild_stats(guild_id=interaction.guild.id)
        embed = discord.Embed(
            title="Успешно!",
            color=discord.Color.green(),
            description="Статистика удалена!"
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="stats-info", description='[Статистика] Показывает информацию о статистике.')
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def stats_info(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"
            ).set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы не имеете права `управлять каналами`, которое необходимо для использования команды!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        doc = await db.get_guild_stats(guild_id=interaction.guild.id)  # type: ignore
        if doc is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У Вас нету статистики! Для её создания пропишите `/stats-setup`."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        description = "Здесь Вы можете увидеть все каналы статистики, а также узнать, когда бот обновит статистику.\n\n**__Статистика:__**\n"
        count = 1
        for channel in doc['channels']:  # type: ignore
            ch = self.bot.get_channel(int(channel['id']))  # type: ignore
            if ch is None: continue
            assert isinstance(ch, discord.TextChannel)
            description += f"> `{count}.` {ch.name}.\n"
            count += 1
        embed = discord.Embed(
            title="Статистика - Информация",
            color=discord.Color.orange(),
            description=description
        )
        embed.add_field(name="Следующее обновление:", value=f"<t:{doc['next_update']}:R> (<t:{doc['next_update']}>)")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
