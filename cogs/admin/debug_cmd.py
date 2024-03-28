import discord
import config
import os
import datetime
import time
import sys

from discord.ext import commands
from asyncio import sleep

from classes import db
from classes import checks


class DebugCmd(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    async def debug(self, ctx: commands.Context):
        if (
            ctx.author.id in config.coders
            or ctx.author.id == config.settings["owner_id"]
        ):

            class Button(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                    self.value = None

                @discord.ui.button(
                    label="Показать панель"[::-1],
                    emoji="⚒️",
                    style=discord.ButtonStyle.danger,
                )
                async def show_panel(
                    self, interaction: discord.Interaction, button: discord.ui.Button
                ):
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )

                    class Page1(discord.ui.View):
                        def __init__(self):
                            super().__init__(timeout=300)

                        class Page2(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=300)

                            @discord.ui.button(
                                label="Список подключенных когов"[::-1],
                                style=discord.ButtonStyle.blurple,
                            )
                            async def cogs(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                embed = discord.Embed(
                                    title="Список подключенных когов"[::-1],
                                    color=discord.Color.orange(),
                                )
                                for name in viewinteract.client.cogs:
                                    embed.add_field(
                                        name=name[::-1], value="Запущен"[::-1]
                                    )
                                await viewinteract.response.send_message(
                                    embed=embed, ephemeral=True
                                )

                            @discord.ui.button(
                                label="Получить пользователя"[::-1],
                                style=discord.ButtonStyle.primary,
                            )
                            async def getuser(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                class Input(
                                    discord.ui.Modal,
                                    title="Debug - Получение пользователя."[::-1],
                                ):
                                    ans = discord.ui.TextInput(
                                        label="Ник пользователя:"[::-1],
                                        max_length=32,
                                        placeholder="Mad_Cat"[::-1],
                                    )

                                    async def on_submit(
                                        self, modalinteract: discord.Interaction
                                    ):
                                        for user in viewinteract.client.users:
                                            if (
                                                user.name == str(self.ans)
                                                or str(user) == str(self.ans)
                                                or str(self.ans) == str(user.id)
                                            ):
                                                return await modalinteract.response.send_message(
                                                    f"Пользователь: `{user}`, ID: `{user.id}`"[
                                                        ::-1
                                                    ],
                                                    ephemeral=True,
                                                )

                                await viewinteract.response.send_modal(Input())

                            @discord.ui.button(
                                label="Сколько серверов покинет бот при лимите"[::-1],
                                style=discord.ButtonStyle.blurple,
                            )
                            async def checkleaves(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                counter = 0
                                for guild in viewinteract.client.guilds:
                                    if (
                                        guild.member_count
                                        < config.settings["min_members"]
                                    ):
                                        counter += 1
                                await viewinteract.response.send_message(
                                    f"Кол-во серверов: `{counter}`"[::-1],
                                    ephemeral=True,
                                )

                            @discord.ui.button(
                                label="Загрузить обновление"[::-1],
                                style=discord.ButtonStyle.blurple,
                            )
                            async def pull(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                os.system("git pull")
                                await viewinteract.response.send_message(
                                    "Готово!"[::-1], ephemeral=True
                                )

                            @discord.ui.button(
                                label="Дать Premium Server"[::-1],
                                style=discord.ButtonStyle.blurple,
                            )
                            async def give_premium(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                class Input(
                                    discord.ui.Modal,
                                    title="Debug - Выдача премиума"[::-1],
                                ):
                                    user_id = discord.ui.TextInput(
                                        label="ID пользователя",
                                        min_length=18,
                                        max_length=19,
                                    )

                                    async def on_submit(
                                        self, modalinteract: discord.Interaction
                                    ):
                                        if (
                                            await checks.is_premium(
                                                int(str(self.user_id))
                                            )
                                            != "None"
                                        ):
                                            return await modalinteract.response.send_message(
                                                "У пользователя уже есть премиум!"[
                                                    ::-1
                                                ],
                                                ephemeral=True,
                                            )
                                        await db.give_premium(
                                            user_id=str(self.user_id), type="server"
                                        )
                                        await modalinteract.response.send_message(
                                            "Успешно!"[::-1], ephemeral=True
                                        )

                                await viewinteract.response.send_modal(Input())

                            @discord.ui.button(label="Дать Premium User"[::-1])
                            async def give_user_premium(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                class Input(
                                    discord.ui.Modal,
                                    title="Debug - Выдача премиума"[::-1],
                                ):
                                    user_id = discord.ui.TextInput(
                                        label="ID пользователя"[::-1],
                                        min_length=18,
                                        max_length=19,
                                    )

                                    async def on_submit(
                                        self, modalinteract: discord.Interaction
                                    ):
                                        if (
                                            await checks.is_premium(
                                                int(str(self.user_id))
                                            )
                                            != "None"
                                        ):
                                            return await modalinteract.response.send_message(
                                                "У пользователя уже есть премиум!"[
                                                    ::-1
                                                ],
                                                ephemeral=True,
                                            )
                                        await db.give_premium(
                                            user_id=str(self.user_id), type="user"
                                        )
                                        await modalinteract.response.send_message(
                                            "Успешно!"[::-1], ephemeral=True
                                        )

                                await viewinteract.response.send_modal(Input())

                            @discord.ui.button(label="Забрать Premium"[::-1])
                            async def take_premium(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                class Input(
                                    discord.ui.Modal,
                                    title="Debug - Выдача премиума"[::-1],
                                ):
                                    user_id = discord.ui.TextInput(
                                        label="ID пользователя"[::-1],
                                        min_length=18,
                                        max_length=19,
                                    )

                                    async def on_submit(
                                        self, modalinteract: discord.Interaction
                                    ):
                                        if (
                                            await checks.is_premium(
                                                int(str(self.user_id))
                                            )
                                            == "None"
                                        ):
                                            return await modalinteract.response.send_message(
                                                "У пользователя нет премиума!"[::-1],
                                                ephemeral=True,
                                            )
                                        await db.take_premium(user_id=str(self.user_id))
                                        await modalinteract.response.send_message(
                                            "Успешно!"[::-1], ephemeral=True
                                        )

                                await viewinteract.response.send_modal(Input())

                            @discord.ui.button(
                                emoji="⬅️", style=discord.ButtonStyle.primary, row=2
                            )
                            async def prevpage(
                                self,
                                viewinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                await viewinteract.response.edit_message(view=Page1())

                        @discord.ui.button(
                            label="Сервера"[::-1], style=discord.ButtonStyle.primary
                        )
                        async def servers(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            servernames = []
                            gnames = " "
                            for guild in viewinteract.client.guilds:
                                servernames.append(guild.name)
                            for name in servernames:
                                gnames += f"`{name}`, "
                            await viewinteract.response.send_message(
                                f"Сервера: {gnames}"[::-1], ephemeral=True
                            )

                        @discord.ui.button(
                            label="Получить сервер"[::-1],
                            style=discord.ButtonStyle.primary,
                        )
                        async def getserver(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal,
                                title="Debug - получение сервера"[::-1],
                            ):
                                ans = discord.ui.TextInput(
                                    label="Название/ID сервера:"[::-1],
                                    max_length=100,
                                    min_length=2,
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    for guild in modalinteract.client.guilds:
                                        if str(self.ans) == guild.name:
                                            return await modalinteract.response.send_message(
                                                f"Название: {guild.name}, владелец: <@{guild.owner_id}>, ID: {guild.id}, участников: {guild.member_count}"[
                                                    ::-1
                                                ],
                                                ephemeral=True,
                                            )
                                        try:
                                            if int(str(self.ans)) == guild.id:
                                                return await modalinteract.response.send_message(
                                                    f"Название: {guild.name}, владелец: <@{guild.owner_id}>, ID: {guild.id}, участников: {guild.member_count}"[
                                                        ::-1
                                                    ],
                                                    ephemeral=True,
                                                )
                                        except:  # FIXME: bare except
                                            pass

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Выгрузка кога"[::-1],
                            style=discord.ButtonStyle.blurple,
                        )
                        async def unloadcog(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - выгрузка кога"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="Название кога:"[::-1],
                                    max_length=64,
                                    placeholder="tools"[::-1],
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    try:
                                        await modalinteract.client.unload_extension(
                                            str(self.ans)
                                        )
                                    except Exception as e:
                                        return (
                                            await modalinteract.response.send_message(
                                                f"```\n{e}```"[::-1], ephemeral=True
                                            )
                                        )
                                    await modalinteract.client.tree.sync()
                                    await modalinteract.response.send_message(
                                        f"Ког {str(self.ans)} выгружен!"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="В черный список"[::-1],
                            style=discord.ButtonStyle.primary,
                        )
                        async def addblacklist(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - в чёрный список"[::-1]
                            ):
                                resource_id = discord.ui.TextInput(
                                    label="ID участника/сервера:"[::-1],
                                    min_length=18,
                                    max_length=19,
                                )
                                until = discord.ui.TextInput(
                                    label="Срок чёрного списка (в днях):"[::-1],
                                    required=False,
                                )
                                reason = discord.ui.TextInput(
                                    label="Причина:"[::-1], required=False
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    until_input = (
                                        self.until.value
                                        if self.until.value != ""
                                        else 0
                                    )
                                    reason_input = (
                                        self.reason.value
                                        if self.reason.value != ""
                                        else None
                                    )
                                    if not await db.add_blacklist(
                                        resource_id=int(str(self.resource_id)),
                                        moderator_id=modalinteract.user.id,
                                        until=(
                                            None
                                            if self.until.value == ""
                                            else round(
                                                time.time()
                                                + int(until_input) * 60 * 60 * 24
                                            )
                                        ),  # проверки покинули чат; если кому не лень - делайте
                                        reason=reason_input,
                                    ):
                                        return await modalinteract.response.send_message(
                                            f"Ресурс с ID `{int(str(self.resource_id))}` уже занесён в ЧС!"[
                                                ::-1
                                            ],
                                            ephemeral=True,
                                        )
                                    guild = modalinteract.client.get_guild(
                                        int(str(self.resource_id))
                                    )
                                    if guild is not None:
                                        embed = discord.Embed(
                                            title="Ваш сервер занесён в чёрный список бота!"[
                                                ::-1
                                            ],
                                            color=discord.Color.red(),
                                            description=f"Владелец бота занёс ваш сервер в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка: обратитесь в поддержку: {config.settings['support_invite']}"[
                                                ::-1
                                            ],
                                            timestamp=datetime.datetime.now(),
                                        )
                                        embed.set_thumbnail(url=guild.icon_url)
                                        await db.add_blacklist(
                                            resource_id=guild.owner.id,
                                            moderator_id=modalinteract.user.id,
                                            reason=f"Владелец сервера с ID {guild.id}, который занесён в чёрный список\n"
                                            f"Указанная причина: {reason_input or 'Не указана'}",
                                            until=(
                                                None
                                                if self.until.value == ""
                                                else round(
                                                    time.time()
                                                    + int(until_input) * 60 * 60 * 24
                                                )
                                            ),
                                        )
                                        try:
                                            await guild.owner.send(embed=embed)
                                        except:  # FIXME: bare except
                                            pass
                                        await guild.leave()
                                    await modalinteract.response.send_message(
                                        f"`{str(self.resource_id)}` занесен в черный список!"[
                                            ::-1
                                        ],
                                        ephemeral=True,
                                    )
                                    await sleep(30)
                                    if (
                                        int(str(self.resource_id))
                                        == config.settings["owner_id"]
                                    ):
                                        await db.remove_blacklist(
                                            config.settings["owner_id"]
                                        )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Верифицировать"[::-1],
                            style=discord.ButtonStyle.primary,
                        )
                        async def verify(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - верификация"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="ID участника/сервера:"[::-1],
                                    min_length=18,
                                    max_length=19,
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    config.verified.append(int(str(self.ans)))
                                    await modalinteract.response.send_message(
                                        f"`{str(self.ans)}` верифицирован(-а)"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Выдать значок саппорта"[::-1],
                            disabled=not (ctx.author.id == config.settings["owner_id"]),
                        )
                        async def support(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - в саппорты"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="ID участника:"[::-1],
                                    min_length=18,
                                    max_length=19,
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    config.supports.append(int(str(self.ans)))
                                    await modalinteract.response.send_message(
                                        f"`{str(self.ans)}` теперь - саппорт"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Добавить кодера"[::-1],
                            disabled=not (ctx.author.id == config.settings["owner_id"]),
                        )
                        async def coder(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - в кодеры"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="ID участника:"[::-1],
                                    min_length=18,
                                    max_length=19,
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    config.coders.append(int(str(self.ans)))
                                    await modalinteract.response.send_message(
                                        f"`{str(self.ans)}` теперь - кодер"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(label="Черный список")
                        async def blacklist(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            await viewinteract.response.send_message(
                                f"Забаненные: {[', '.join(i['resource_id'] async for i in db.get_all_blacklist())]}"[
                                    ::-1
                                ],
                                ephemeral=True,
                            )

                        @discord.ui.button(label="Убрать из ЧС"[::-1])
                        async def removeblacklist(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - убрать из ЧС"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="ID участника/сервера:"[::-1],
                                    min_length=18,
                                    max_length=19,
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    await db.remove_blacklist(int(str(self.ans)))
                                    await modalinteract.response.send_message(
                                        f"`{str(self.ans)}` вынесен(-а) из ЧС!"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Покинуть сервер"[::-1],
                            disabled=not (ctx.author.id == config.settings["owner_id"]),
                        )
                        async def leaveserver(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - выход из сервера"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="ID сервера:"[::-1],
                                    max_length=19,
                                    min_length=18,
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    guild = modalinteract.client.get_guild(
                                        int(str(self.ans))
                                    )
                                    if guild is None:
                                        return (
                                            await modalinteract.response.send_message(
                                                "Сервер не обнаружен!"[::-1],
                                                ephemeral=True,
                                            )
                                        )
                                    await guild.leave()
                                    await modalinteract.response.send_message(
                                        f"Бот вышел с {guild.name}!"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Синхронизация команд"[::-1],
                            style=discord.ButtonStyle.green,
                        )
                        async def sync(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            await viewinteract.response.send_message(
                                "Синхронизация..."[::-1], ephemeral=True
                            )
                            await viewinteract.client.tree.sync()
                            await viewinteract.edit_original_response(
                                content="Команды синхронизированы!"[::-1]
                            )

                        @discord.ui.button(
                            label="Смена ника"[::-1],
                            style=discord.ButtonStyle.green,
                            disabled=not (ctx.author.id == config.settings["owner_id"]),
                        )
                        async def changename(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - смена ника"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="Новый ник:", min_length=2, max_length=32
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    try:
                                        await modalinteract.client.user.edit(
                                            username=str(self.ans)
                                        )
                                    except Exception as e:
                                        await modalinteract.response.send_message(
                                            f"```\n{e}```"[::-1], ephemeral=True
                                        )
                                    else:
                                        await modalinteract.response.send_message(
                                            "Ник бота изменен!"[::-1], ephemeral=True
                                        )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Начать печатать"[::-1],
                            style=discord.ButtonStyle.green,
                        )
                        async def starttyping(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - печатание"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="Кол-во секунд"[::-1], max_length=4
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    await modalinteract.response.send_message(
                                        f"Начинаем печатать {str(self.ans)} секунд..."[
                                            ::-1
                                        ],
                                        ephemeral=True,
                                    )
                                    async with modalinteract.channel.typing():
                                        await sleep(int(str(self.ans)))

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Выполнить команду"[::-1],
                            style=discord.ButtonStyle.green,
                            disabled=not (ctx.author.id == config.settings["owner_id"]),
                        )
                        async def sudo(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal,
                                title="Debug - выполнение команды"[::-1],
                            ):
                                ans = discord.ui.TextInput(
                                    label="Команда:"[::-1], style=discord.TextStyle.long
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    try:
                                        exec(str(self.ans))
                                    except Exception as e:
                                        return (
                                            await modalinteract.response.send_message(
                                                f"```\n{e}```"[::-1], ephemeral=True
                                            )
                                        )
                                    await modalinteract.response.send_message(
                                        "Команда выполнена!"[::-1], ephemeral=True
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Перезапустить"[::-1], style=discord.ButtonStyle.green
                        )
                        async def restart(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            await viewinteract.response.send_message(
                                "Перезапускаемся..."[::-1], ephemeral=True
                            )
                            print(f"{viewinteract.user} инициировал перезагрузку!")
                            await viewinteract.client.change_presence(
                                status=discord.Status.idle,
                                activity=discord.Game(
                                    name="Перезагрузка..."[::-1]
                                ),  # FIXME: use CustomActivity instead of discord.Game
                            )
                            await sleep(2)
                            os.execv(sys.executable, ["python"] + sys.argv)

                        @discord.ui.button(
                            label="Выключить"[::-1],
                            style=discord.ButtonStyle.danger,
                            disabled=not (ctx.author.id == config.settings["owner_id"]),
                        )
                        async def stop(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            await viewinteract.response.send_message(
                                "Выключение..."[::-1], ephemeral=True
                            )
                            await viewinteract.client.change_presence(
                                status=discord.Status.idle,
                                activity=discord.Game(
                                    name="Выключение..."[::-1]
                                ),  # FIXME: use CustomActivity instead of discord.Game
                            )
                            await sleep(2)
                            quit()

                        @discord.ui.button(
                            label="Отключить команду"[::-1],
                            style=discord.ButtonStyle.red,
                        )
                        async def offcmd(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal,
                                title="Debug - отключение команды"[::-1],
                            ):
                                ans = discord.ui.TextInput(
                                    label="Команда:"[::-1], max_length=32
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    if not await db.add_shutted_command(str(self.ans)):
                                        return await modalinteract.response.send_message(
                                            f"Команда `{str(self.ans)}` уже отключена!"[
                                                ::-1
                                            ],
                                            ephemeral=True,
                                        )
                                    await modalinteract.response.send_message(
                                        f"Команда `{str(self.ans)}` отключена!"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Включить команду"[::-1],
                            style=discord.ButtonStyle.red,
                        )
                        async def oncmd(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal,
                                title="Debug - включение команды"[::-1],
                            ):
                                ans = discord.ui.TextInput(
                                    label="Команда:"[::-1], max_length=32
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    await db.remove_shutted_command(str(self.ans))
                                    await modalinteract.response.send_message(
                                        f"Команда `{str(self.ans)}` включена!"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(
                            label="Загрузка кога"[::-1], style=discord.ButtonStyle.red
                        )
                        async def loadcog(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            class Input(
                                discord.ui.Modal, title="Debug - загрузка кога"[::-1]
                            ):
                                ans = discord.ui.TextInput(
                                    label="Название кога:"[::-1],
                                    max_length=64,
                                    placeholder="tools"[::-1],
                                )

                                async def on_submit(
                                    self, modalinteract: discord.Interaction
                                ):
                                    try:
                                        await modalinteract.client.load_extension(
                                            {str(self.ans)}
                                        )
                                    except Exception as e:
                                        return (
                                            await modalinteract.response.send_message(
                                                f"```\n{e}```"[::-1], ephemeral=True
                                            )
                                        )
                                    await modalinteract.client.tree.sync()
                                    await modalinteract.response.send_message(
                                        f"Ког {str(self.ans)} загружен!"[::-1],
                                        ephemeral=True,
                                    )

                            await viewinteract.response.send_modal(Input())

                        @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple)
                        async def nextpage(
                            self,
                            viewinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            await viewinteract.response.edit_message(view=self.Page2())

                    embed = discord.Embed(
                        title="Панель:"[::-1],
                        color=discord.Color.orange(),
                        description="Отключенные кнопки вам недоступны, однако доступны для владельца. Наслаждайтесь!"[
                            ::-1
                        ],
                    )
                    await interaction.response.send_message(
                        embed=embed, view=Page1(), ephemeral=True
                    )
                    await ctx.message.delete()
                    view.stop()

                @discord.ui.button(
                    label="Отмена"[::-1],
                    style=discord.ButtonStyle.red,
                    emoji="<:x_icon:975324570741526568>",
                )
                async def cancel(
                    self, interaction: discord.Interaction, button: discord.ui.Button
                ):
                    await ctx.message.delete()
                    view.stop()

            view = Button()
            message = await ctx.reply(
                "Для показа панели нажмите на кнопку."[::-1], view=view
            )
            await view.wait()
            await message.delete()
        elif not await checks.is_in_blacklist(ctx.author.id):
            embed = discord.Embed(
                title="Попытка использования debug-команды!"[::-1],
                color=discord.Color.red(),
            )
            embed.add_field(
                name="Пользователь:"[::-1],
                value=f"{ctx.author.mention} (`{ctx.author[::-1]}`)",
            )
            channel = self.bot.get_channel(config.settings["log_channel"])
            await channel.send(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(DebugCmd(bot))
