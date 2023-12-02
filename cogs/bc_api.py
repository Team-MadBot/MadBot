import aiohttp
import discord
import traceback
import datetime
import time
import config
import logging

from boticordpy import BoticordClient
from discord.ext import commands, tasks
from discord import utils as dutils
from discord import ui
from contextlib import suppress
from asyncio import sleep

logger = logging.getLogger('discord')

from classes.bc_websocket import BoticordWS
from config import settings
from classes import db

class LinktoBoticord(ui.View):
    def __init__(self, bot_id: int):
        super().__init__(timeout=900)
        self.add_item(
            ui.Button(
                url=f"https://boticord.top/bot/{bot_id}",
                label="Апнуть бота"
            )
        )
        self.add_item(
            ui.Button(
                url=f"https://bots.server-discord.com/{bot_id}",
                label="Также апнуть на SDC"
            )
        )
    
class SetReminderButton(ui.Button):
    def __init__(self, user_id: int, *, disabled: bool):
        super().__init__(
            style=discord.ButtonStyle.blurple, 
            label="Напомнить",
            disabled=disabled
        )
        self.user_id = user_id
        self.upped_at = round(time.time())
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Не для тебя кнопочка!", ephemeral=True)
        
        user = db.get_user(self.user_id)
        if user is not None and user['enabled']:
            embed = discord.Embed(
                title="Напоминание о повышении",
                color=discord.Color.orange(),
                description="Напоминание о повышении бота на мониторинге уже включено. Для отключения напоминания "
                "используйте `/remind disable`."
            )
            self.view.stop()
            return await interaction.response.send_message(
                embed=embed, 
                ephemeral=True
            )
        elif user is not None:
            db.update_user(
                user_id=self.user_id,
                enabled=True
            )
        else:
            db.add_user(
                user_id=self.user_id,
                enabled=True,
                next_bump=self.upped_at + 3600 * 6,
                reminded=False,
                up_count=1
            )
        
        embed = discord.Embed(
            title="Напоминание о повышении",
            color=discord.Color.orange(),
            description="Напоминание о повышении бота на мониторинге включено. Вы будете упомянуты в этом канале, "
            "когда настанет время. Для отключения используйте `/remind disable`"
        )
        self.view.stop()
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

class Boticord(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bc_token = settings['bcv2_token']
        self.bc_ws = BoticordWS(self.bc_token)
        self.bc_client = BoticordClient(self.bc_token)
        self.session = aiohttp.ClientSession()
        self.bc_wh = discord.Webhook.from_url(
            settings['bc_hook_url'], 
            session=self.session,
            client=self.bot,
            bot_token=settings['token']
        )
    
    async def cog_load(self):
        self.bc_ws.register_listener("up_added", self.new_bot_bump)
        self.bc_ws.register_listener("comment_added", self.comment_added)
        self.bc_ws.register_listener("comment_edited", self.comment_edited)
        self.bc_ws.register_listener("comment_removed", self.comment_removed)
        self.bc_ws.register_closer(self.on_close)
        
        self.stats_task = self.send_stats.start()
        with suppress(Exception):
            await self.bc_ws.connect()
    
    async def cog_unload(self):
        self.stats_task.cancel()
        if self.bc_ws.not_closed:
            await self.bc_ws.close()
    
    async def on_close(self, code: int):
        await sleep(15)
        await self.bot.reload_extension("cogs.bc_api")
    
    async def new_bot_bump(self, data: dict):
        if data['id'] != str(self.bot.user.id):
            return
        bc_wh = self.bc_wh
        user = await self.bot.fetch_user(int(data['user']))
        next_up = round(time.time()) + 3600 * 6
        view = LinktoBoticord(bot_id=self.bot.user.id)

        db_user = db.get_user(user_id=user.id)
        view.add_item(SetReminderButton(user.id, disabled=db_user is not None))

        if db_user is not None:
            db.update_user(
                user_id=user.id,
                next_bump=next_up,
                reminded=False
            )
            db.increment_user(
                user_id=user.id,
                up_count=1
            )
        else:
            db.add_user(
                user_id=user.id,
                next_bump=next_up,
                reminded=False,
                enabled=False,
                up_count=1
            )

        embed = discord.Embed(
            title="Спасибо за ап бота!",
            color=discord.Color.orange(),
            description=f"В награду, Вам выдано **1,500 серверных монет**. Если Вы не получили монет - "
            "напишите в <#981547296275705927>.\n\n"
            "Вы также можете апнуть бота на SDC (кнопка ниже), но для получения награды необходимо прислать скриншот "
            "в <#1128223151264911360>.",
            timestamp=datetime.datetime.now()
        ).set_footer(
            text=f"ID пользователя: {user.id}"
        ).set_author(
            name=f"{user.display_name} ({user.name})", 
            icon_url=user.display_avatar.url
        ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
        ).add_field(
            name="Кол-во апов теперь:",
            value=f"**{data['payload']['upCount']:,}**"
        ).add_field(
            name="Следующий бамп:",
            value=f"<t:{next_up}> (<t:{next_up}:R>)"
        )
        msg = await bc_wh.send(content=user.mention, embed=embed, view=view, wait=True)
        headers = {
            "Authorization": settings['unbelieva_token']
        }
        body = {
            "cash": 1500,
            "reason": "Ап бота"
        }
        await self.session.patch(
            f"https://unbelievaboat.com/api/v1/guilds/{settings['comm_guild']}/users/{user.id}",
            headers=headers,
            json=body
        )
        await view.wait()
        for item in view.children:
            if item.url is None:
                item.disabled = True
        await msg.edit(view=view)
    
    async def comment_added(self, data: dict):
        if data['id'] != str(self.bot.user.id):
            return
        bc_wh = self.bc_wh
        user = await self.bot.fetch_user(int(data['user']))
        embed = discord.Embed(
            title=f"Новый отзыв ({data['payload']['rating']} из 5)",
            color=discord.Color.orange(),
            description=f"**Отзыв:**\n{dutils.escape_markdown(data['payload']['content'])}",
            timestamp=datetime.datetime.now()
        ).set_footer(
            text=f"ID пользователя: {user.id}"
        ).set_author(
            name=f"{user.display_name} ({user.name})", 
            icon_url=user.display_avatar.url
        ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
        )
        await bc_wh.send(embed=embed, view=LinktoBoticord(bot_id=self.bot.user.id))

    async def comment_removed(self, data: dict):
        if data['id'] != str(self.bot.user.id):
            return
        bc_wh = self.bc_wh
        user = await self.bot.fetch_user(int(data['user']))
        embed = discord.Embed(
            title=f"Удалён отзыв ({data['payload']['rating']} из 5)",
            color=discord.Color.orange(),
            description=f"**Отзыв:**\n{dutils.escape_markdown(data['payload']['content'])}",
            timestamp=datetime.datetime.now()
        ).set_footer(
            text=f"ID пользователя: {user.id}"
        ).set_author(
            name=f"{user.display_name} ({user.name})", 
            icon_url=user.display_avatar.url
        ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
        )
        await bc_wh.send(embed=embed, view=LinktoBoticord(bot_id=self.bot.user.id))
    
    async def comment_edited(self, data: dict):
        if data['id'] != str(self.bot.user.id):
            return
        bc_wh = self.bc_wh
        user = await self.bot.fetch_user(int(data['user']))
        embed = discord.Embed(
            title=f"Изменён отзыв ({data['payload']['rating']} из 5)",
            color=discord.Color.orange(),
            description=f"**Новый отзыв:**\n{dutils.escape_markdown(data['payload']['content'])}",
            timestamp=datetime.datetime.now()
        ).set_footer(
            text=f"ID пользователя: {user.id}"
        ).set_author(
            name=f"{user.display_name} ({user.name})", 
            icon_url=user.display_avatar.url
        ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
        )
        await bc_wh.send(embed=embed, view=LinktoBoticord(bot_id=self.bot.user.id))

    @tasks.loop(seconds=300)
    async def send_stats(self):
        try:
            await self.bc_client.post_bot_stats(
                self.bot.user.id,
                servers=len(self.bot.guilds),
                shards=self.bot.shard_count,
                users=len(self.bot.users)
            )
        except Exception as e:
            logger.error("Статистика на Boticord НЕ ОБНОВЛЕНА!!! (V2)")
            logger.error(traceback.format_exc())
            logger.error("============ AutoPost ============")
        else:
            logger.info("Статистика на Boticord обновлена! (V2)")
    
    @send_stats.before_loop
    async def wait_before_loop(self):
        await self.bot.wait_until_ready()
"""
async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(Boticord(bot))
"""