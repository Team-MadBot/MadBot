import discord
import aiohttp
import traceback
import time
import datetime
import logging

from discord.ext import commands
from discord import app_commands
from config import settings

logger = logging.getLogger('discord')

class RisticksAPI(commands.Cog):
    RISTICKS_LOGO_URL = "https://i.imgur.com/nMMTavR.png"

    NO_GUILD_ERROR = discord.Embed(
        title="Ошибка!",
        color=discord.Color.red(),
        description="Сервера нет на Risticks. [Добавьте сервер](https://risticks.xyz/add) и попробуйте снова."
    )

    UNKNOWN_RISTICKS_ERROR = discord.Embed(
        title="Неизвестная ошибка!",
        color=discord.Color.red(),
        description="Произошла неизвестная ошибка при отправке запроса для Risticks API. "
        "Проблема сообщена разработчику бота. Попробуйте позже."
    )

    @property
    def BUMP_SUCCESS(self):
        return discord.Embed(
            title="✅ Risticks UP",
            color=discord.Color.orange(),
            description="Следующий бамп <t:{next_bump}:R> (<t:{next_bump}>)",
            timestamp=datetime.datetime.now()
        ).set_thumbnail(
            url=self.RISTICKS_LOGO_URL
        )

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self._token = settings["risticks_token"]
        self.session = aiohttp.ClientSession(
            base_url="https://api.risticks.xyz"
        )
    
    async def _post_guildinfo(
        self, 
        guild_id: int, 
        owner_id: int,
        name: str,
        icon: discord.Asset | None,
        members: int,
        status: bool,
        invite: str | None = None
    ) -> dict:
        headers = {
            'Authorization': self._token
        }
        json = {
            'owner_id': str(owner_id),
            'name': name,
            'icon': icon.key if icon else None,
            'members': members,
            'status': status,
            'invite': invite
        }
        async with self.session.post(
            f"/guildinfo/{guild_id}",
            headers=headers,
            json=json
        ) as response:
            return await response.json()

    async def _get_guildinfo(self, guild_id: int) -> dict:
        headers = {
            'Authorization': self._token
        }

        async with self.session.get(
            f"/guildinfo/{guild_id}",
            headers=headers
        ) as response:
            return await response.json()
    
    async def _bump(self, guild_id: int, user_id: int) -> dict:
        json = {'user_id': str(user_id)}
        headers = {
            'Authorization': self._token
        }
        
        async with self.session.post(
            f'/bump/{guild_id}',
            json=json,
            headers=headers
        ) as response:
            return await response.json()
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._post_guildinfo(
            guild_id=guild.id,
            owner_id=guild.owner_id,
            name=guild.name,
            icon=guild.icon.key if guild.icon else None,
            members=guild.member_count,
            status=True
        )

    @commands.Cog.listener()
    async def on_guild_leave(self, guild: discord.Guild):
        await self._post_guildinfo(
            guild_id=guild.id,
            owner_id=guild.owner_id,
            name=guild.name,
            icon=guild.icon,
            members=guild.member_count,
            status=False
        )
    
    @app_commands.command(name="bump", description="Апнуть сервер на Risticks")
    @app_commands.guild_only()
    async def bump(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            resp = await self._bump(interaction.guild.id, interaction.user.id)
        except:  # FIXME: bare except
            logger.error(traceback.format_exc())
            return await interaction.followup.send(
                embed=self.UNKNOWN_RISTICKS_ERROR
            )

        if resp.get("code") == 404:
            return await interaction.followup.send(
                embed=self.NO_GUILD_ERROR
            )

        if resp.get("code") is None or resp.get("code") >= 400:
            logger.debug(resp)
            return await interaction.followup.send(
                embed=self.UNKNOWN_RISTICKS_ERROR
            )
        
        next_bump = str(round(time.time()) + 3600 * 4)
        embed = self.BUMP_SUCCESS
        embed.description = embed.description.format(next_bump=next_bump)
        
        await interaction.followup.send(
            embed=embed
        )

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(RisticksAPI(bot))
