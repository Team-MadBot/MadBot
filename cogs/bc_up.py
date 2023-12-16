import discord
import aiohttp
import base64
import datetime
import time

from discord.ext import commands
from discord import app_commands
from discord import ui
from typing import List, Union
from io import BytesIO

from config import *
from classes import checks
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
        
        user = await db.get_user(user_id=self.user_id)
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
            await db.update_user(
                user_id=self.user_id,
                enabled=True
            )
        else:
            await db.add_user(
                user_id=self.user_id,
                enabled=True,
                next_bump=self.upped_at + 3600 * 6,
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

class CaptchaButton(ui.Button):
    def __init__(self, emoji: str):
        super().__init__(label=emoji)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            return await interaction.response.send_message("Не для тебя кнопочка!", ephemeral=True)
        self.view.value = self.view.ans[self.label]
        self.view.interaction = interaction
        self.view.stop()

class CaptchaButtonsView(ui.View):
    def __init__(self, options: list, user_id: int):
        super().__init__()
        self.ans = {}
        self.value = None
        self.user_id = user_id
        self.interaction: discord.Interaction = None
        for count, option in enumerate(options):
            self.ans[option] = count
            b = CaptchaButton(option)
            self.add_item(b)

class BoticordBotUp(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.token = settings['bcv2_token']
        
    async def cog_load(self):
        self.session = aiohttp.ClientSession(
            base_url="https://api.boticord.top",
            headers={
                "Authorization": self.token,
                "User-Agent": f"MadBot v.{settings['curr_version']} (aiohttp v.{aiohttp.__version__})",
                "Content-Type": "application/json"
            }
        )

    async def cog_unload(self):
        await self.session.close()
    
    async def get_captcha(self, user_id: int) -> List[Union[aiohttp.ClientResponse, dict]]:
        async with self.session.post(
            "/v3/resources/ups/service/prepare",
            json={
                "token": self.token,
                "resource": str(self.bot.user.id),
                "user": str(user_id)
            }
        ) as resp:
            if resp.content_type.lower() != "application/json":
                data = await resp.read()
                return [resp, {"error": data}]
            json = await resp.json()
            return [resp, json]

    async def submit_captcha(
        self, 
        captcha_id: str,
        user_id: int,
        answer: int
    ) -> List[Union[aiohttp.ClientResponse, dict]]:
        async with self.session.post(
            "/v3/resources/ups/service/proceed",
            json={
                "token": self.token,
                "resource": str(self.bot.user.id),
                "user": str(user_id),
                "captchaId": captcha_id,
                "captchaAnswer": answer
            }
        ) as resp:
            json = await resp.json()
            return [resp, json]
        
    @app_commands.command(name="up", description="[Boticord] Апнуть бота на мониторинге")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.checks.cooldown(1, 5.0)
    async def bump_bot(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        resp, resp_json = await self.get_captcha(interaction.user.id)

        if resp.status == 403:
            embed = discord.Embed(
                title="Бамп бота - Запрещено",
                color=discord.Color.red(),
                description="Боту необходимо иметь 3 уровень буста на сайте. Вы можете помочь в этом, "
                "совершив покупку буста [здесь](https://boticord.top/boost) и выдав его на странице бота, "
                r"нажав на кнопку перехода на страницу бота снизу \:)"
            ).set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
            view = ui.View().add_item(
                ui.Button(
                    label="Бот на Boticord.top",
                    emoji="<:boticord_logo:1140272903934455821>",
                    url="https://boticord.top/bot/madbot"
                )
            )
            return await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        if resp.status == 429:
            next_bump = round(time.time()) + resp_json['result']['cd'] // 1000
            embed = discord.Embed(
                title="Бамп бота - Время ещё не прошло",
                color=discord.Color.orange(),
                description=f"Вы сможете апнуть бота только <t:{next_bump}:R> (<t:{next_bump}>)"
            ).set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            db_user = await db.get_user(user_id=interaction.user.id)
            if db_user is not None:
                await db.update_user(
                    user_id=interaction.user.id,
                    next_bump=next_bump,
                    reminded=False
                )
            else:
                await db.add_user(
                    user_id=interaction.user.id,
                    next_bump=next_bump
                )
            return
        
        if resp.status == 404:
            embed = discord.Embed(
                title="Бамп бота - Неизвестный пользователь",
                color=discord.Color.orange(),
                description="Вам необходимо авторизоваться на сайте для бампа бота."
            ).set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
            view = ui.View().add_item(
                ui.Button(
                    label="Boticord.top",
                    emoji="<:boticord_logo:1140272903934455821>",
                    url="https://boticord.top"
                )
            )
            return await interaction.followup.send(embed=embed, ephemeral=True, view=view)
        
        if not resp.ok:
            embed = discord.Embed(
                title="Бамп бота - Необработанная ошибка",
                color=discord.Color.red(),
                description="Что-то пошло не так при получении капчи. Попробуйте снова."
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        captcha_id = resp_json['result']['captcha']['id']
        captcha_bytes = base64.b64decode(resp_json['result']['captcha']['image'])
        captcha_choices = resp_json['result']['captcha']['choices']
        captcha_file = discord.File(
            BytesIO(captcha_bytes), 
            filename="captcha.png", 
            description="Boticord.top captcha"
        )
        embed = discord.Embed(
            title="Бамп бота - Капча",
            color=discord.Color.orange(),
            description="Для того, чтобы апнуть бота, Вам необходимо решить капчу. Нажмите на кнопку с эмодзи, "
            "который соответствует тексту на изображении."
        ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
        ).set_image(
            url="attachment://captcha.png"
        )
        view = CaptchaButtonsView(captcha_choices, interaction.user.id)
        msg = await interaction.followup.send(
            embed=embed, 
            file=captcha_file, 
            view=view, 
            wait=True
        )
        await view.wait()

        if view.value is None:
            return await msg.edit(
                view=None,
                attachments=[],
                embed=discord.Embed(
                    title="Бамп бота - Время решения капчи вышло!",
                    color=discord.Color.red()
                ) 
            )
        
        resp, resp_json = await self.submit_captcha(
            captcha_id=captcha_id,
            user_id=interaction.user.id,
            answer=view.value
        )

        if not resp.ok:
            embed = discord.Embed(
                title="Бамп бота - Неверный ответ",
                color=discord.Color.red(),
                description="Вы ответили на капчу неверно. Напишите команду снова."
            ).set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
            return await view.interaction.response.edit_message(
                embed=embed,
                attachments=[],
                view=None
            )

        embed = discord.Embed(
            title="Бамп бота - Успешно",
            color=discord.Color.orange(),
            description="Вы успешно апнули бота!"
        ).set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
        ).add_field(
            name="Оценка истечёт",
            value=f"<t:{resp_json['result']['up']['expires'] // 1000}> (<t:{resp_json['result']['up']['expires'] // 1000}:R>)"
        ).add_field(
            name="Текущее кол-во апов",
            value=f"**{resp_json['result']['upCount']}**"
        )
        await view.interaction.response.edit_message(
            embed=embed,
            view=None,
            attachments=[]
        )

        # Выдача награды (убрать, когда мирдук сделает фиксика)
        bc_wh = discord.Webhook.from_url(
            settings['bc_hook_url'], 
            session=aiohttp.ClientSession(),
            client=self.bot,
            bot_token=settings['token']
        )
        user = interaction.user

        next_up = round(time.time()) + 3600 * 6
        view = LinktoBoticord(bot_id=self.bot.user.id)

        db_user = await db.get_user(user_id=user.id)
        view.add_item(SetReminderButton(user.id, disabled=db_user is not None))

        if db_user is not None:
            await db.update_user(
                user_id=user.id,
                next_bump=next_up,
                reminded=False
            )
            await db.increment_user(
                user_id=user.id,
                up_count=1
            )
        else:
            await db.add_user(
                user_id=user.id,
                next_bump=next_up,
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
            value=f"**{resp_json['result']['upCount']:,}**"
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
        session = aiohttp.ClientSession()
        await session.patch(
            f"https://unbelievaboat.com/api/v1/guilds/{settings['comm_guild']}/users/{user.id}",
            headers=headers,
            json=body
        )
        await view.wait()
        for item in view.children:
            if item.url is None:
                item.disabled = True
        await msg.edit(view=view)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BoticordBotUp(bot))
