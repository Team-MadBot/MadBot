import aiohttp
import discord
import datetime
import time
import logging

from discord.ext import commands
from discord import utils as dutils
from discord import ui

from typing import Any

from config import settings
from classes import db
from classes.bc_api import BoticordClient
from contextlib import suppress

logger = logging.getLogger("discord")


class LinktoBoticord(ui.View):
    def __init__(self, bot_id: int):
        super().__init__(timeout=900)
        self.add_item(
            ui.Button(url=f"https://boticord.top/bot/{bot_id}", label="Апнуть бота")
        )
        self.add_item(
            ui.Button(
                url=f"https://bots.server-discord.com/{bot_id}",
                label="Также апнуть на SDC",
            )
        )


class SetReminderButton(ui.Button):  # type: ignore
    def __init__(self, user_id: int, *, disabled: bool):
        super().__init__(
            style=discord.ButtonStyle.blurple, label="Напомнить", disabled=disabled
        )
        self.user_id = user_id
        self.upped_at = round(time.time())

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "Не для тебя кнопочка!", ephemeral=True
            )

        user = await db.get_user(self.user_id)  # type: ignore
        if user is not None and user["enabled"]:
            embed = discord.Embed(
                title="Напоминание о повышении",
                color=discord.Color.orange(),
                description="Напоминание о повышении бота на мониторинге уже включено. Для отключения напоминания "
                "используйте `/remind disable`.",
            )
            self.view.stop()  # type: ignore
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        elif user is not None:
            await db.update_user(user_id=self.user_id, enabled=True)  # type: ignore
        else:
            await db.add_user(
                user_id=self.user_id,
                enabled=True,
                next_bump=self.upped_at + 3600 * 6,
                reminded=False,
                up_count=1,
            )

        embed = discord.Embed(
            title="Напоминание о повышении",
            color=discord.Color.orange(),
            description="Напоминание о повышении бота на мониторинге включено. Бот напишет Вам в личные сообщения, "
            "когда настанет время. **Убедитесь, что бот сможет это сделать!**",
        ).set_footer(text="Для отключения используйте `/remind disable`")
        self.view.stop()  # type: ignore
        await interaction.response.send_message(embed=embed, ephemeral=True)


class BoticordCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bc_token = settings["bcv2_token"]
        self.session = aiohttp.ClientSession()
        self.bc_client = BoticordClient(self.bc_token)
        self.bc_wh = discord.Webhook.from_url(
            settings["bc_hook_url"],
            session=self.session,
            client=self.bot,
            bot_token=settings["token"],
        )

    async def cog_load(self):
        self.bc_client.ws.register_listener("up_added", self.new_bot_bump)  # type: ignore
        self.bc_client.ws.register_listener("comment_added", self.comment_added)  # type: ignore
        self.bc_client.ws.register_listener("comment_edited", self.comment_edited)  # type: ignore
        self.bc_client.ws.register_listener("comment_removed", self.comment_removed)  # type: ignore

        await self.bc_client.ws.connect()

    async def cog_unload(self):
        if not settings["debug_mode"]:
            self.send_stats.cancel()

        if self.bc_client.ws.not_closed:
            await self.bc_client.ws.close()
            await self.bc_client.session.close()

    async def new_bot_bump(self, data: dict[str, Any]):
        assert self.bot.user is not None
        assert isinstance(data["user"], str)

        if data["id"] != str(self.bot.user.id) and not settings["debug_mode"]:
            return

        bc_ws = self.bc_ws
        user = await self.bot.fetch_user(int(data["user"]))
        next_up = round(time.time()) + 3600 * 6
        view = LinktoBoticord(bot_id=data["id"])

        db_user = await db.get_user(user_id=user.id)  # type: ignore
        view.add_item(SetReminderButton(user.id, disabled=db_user is not None))

        if db_user is not None:
            await db.update_user(  # type: ignore
                user_id=user.id, next_bump=next_up, reminded=False
            )
            await db.increment_user(user_id=user.id, up_count=1)  # type: ignore
        else:
            await db.add_user(
                user_id=user.id,
                next_bump=next_up,
                reminded=False,
                enabled=False,
                up_count=1,
            )

        embed = (
            discord.Embed(
                title="Спасибо за ап бота!",
                color=discord.Color.orange(),
                description=f"В награду, с Вас сняты задержки на команды на 6 часов! Если задержки всё ещё присутствуют - "
                "напишите в <#1214210929844027402> на сервере поддержки.\n\n"
                "Вы также можете апнуть бота на SDC (кнопка ниже), однако никакой награды выдано не будет.",
                timestamp=datetime.datetime.now(),
            )
            .set_footer(text=f"ID пользователя: {user.id}")
            .set_author(
                name=f"{user.display_name} ({user.name})",
                icon_url=user.display_avatar.url,
                url=f"https://discord.com/users/{user.id}"
            )
            .set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
            .add_field(
                name="Кол-во апов теперь:", value=f"**{data['payload']['upCount']:,}**"
            )
            .add_field(name="Следующий бамп:", value=f"<t:{next_up}> (<t:{next_up}:R>)")
        )
        await bc_ws.send(
            embed=embed,
            view=LinktoBoticord(data["id"])
        )
        with suppress(Exception):
            msg = await user.send(
                content=user.mention, embed=embed, view=view, wait=True
            )
            await view.wait()
            for item in view.children:
                if item.url is None:  # type: ignore
                    item.disabled = True  # type: ignore
            await msg.edit(view=view)

    async def comment_added(self, data: dict[str, Any]):
        assert self.bot.user is not None
        if data["id"] != str(self.bot.user.id) and not settings["debug_mode"]:
            return

        bc_wh = self.bc_wh
        user = await self.bot.fetch_user(int(data["user"]))
        embed = (
            discord.Embed(
                title=f"Новый отзыв ({data['payload']['rating']} из 5)",
                color=discord.Color.orange(),
                description=f"**Отзыв:**\n{dutils.escape_markdown(data['payload']['content'])}",
                timestamp=datetime.datetime.now(),
            )
            .set_footer(text=f"ID пользователя: {user.id}")
            .set_author(
                name=f"{user.display_name} ({user.name})",
                icon_url=user.display_avatar.url,
                url=f"https://discord.com/users/{user.id}"
            )
            .set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
        )
        await bc_wh.send(embed=embed, view=LinktoBoticord(bot_id=data["id"]))

    async def comment_removed(self, data: dict[str, Any]):
        assert self.bot.user is not None
        if data["id"] != str(self.bot.user.id) and not settings["debug_mode"]:
            return

        bc_wh = self.bc_wh
        user = await self.bot.fetch_user(int(data["user"]))
        embed = (
            discord.Embed(
                title=f"Удалён отзыв ({data['payload']['rating']} из 5)",
                color=discord.Color.orange(),
                description=f"**Отзыв:**\n{dutils.escape_markdown(data['payload']['content'])}",
                timestamp=datetime.datetime.now(),
            )
            .set_footer(text=f"ID пользователя: {user.id}")
            .set_author(
                name=f"{user.display_name} ({user.name})",
                icon_url=user.display_avatar.url,
                url=f"https://discord.com/users/{user.id}"
            )
            .set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
        )
        await bc_wh.send(embed=embed, view=LinktoBoticord(bot_id=data["id"]))

    async def comment_edited(self, data: dict[str, Any]):
        assert self.bot.user is not None
        if data["id"] != str(self.bot.user.id) and not settings["debug_mode"]:
            return

        bc_wh = self.bc_wh
        user = await self.bot.fetch_user(int(data["user"]))
        embed = (
            discord.Embed(
                title=f"Изменён отзыв ({data['payload']['rating']} из 5)",
                color=discord.Color.orange(),
                description=f"**Новый отзыв:**\n{dutils.escape_markdown(data['payload']['content'])}",
                timestamp=datetime.datetime.now(),
            )
            .set_footer(text=f"ID пользователя: {user.id}")
            .set_author(
                name=f"{user.display_name} ({user.name})",
                icon_url=user.display_avatar.url,
                url=f"https://discord.com/users/{user.id}"
            )
            .set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
        )
        await bc_wh.send(embed=embed, view=LinktoBoticord(bot_id=data["id"]))


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BoticordCog(bot))
