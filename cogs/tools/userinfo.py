import discord

from discord import app_commands
from discord import utils as dutils
from discord.ext import commands
from discord.utils import escape_markdown

from . import default_cooldown

from tools import enums

from classes import checks

from config import settings
from config import coders
from config import supports
from config import bug_hunters
from config import bug_terminators
from config import verified

class UserInfo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="[Полезности] Показывает информацию о пользователе")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member='Участник')
    async def userinfo(self, interaction: discord.Interaction, member: discord.User | discord.Member = None):
        member = member or interaction.user

        embed = discord.Embed(
            title=f"{escape_markdown(member.global_name or member.name)} ({escape_markdown(member.name)})",
            color=discord.Color.orange()
        ).set_footer(
            text=f"ID: {member.id}"
        ).set_thumbnail(
            url=member.display_avatar.url
        )
        badges = []
        if await checks.is_in_blacklist(member.id):
            badges.append(enums.Badges.BANNED.value)
        if await checks.is_premium(member.id):
            badges.append(enums.Badges.PREMIUM.value)
        if member.id == settings["owner_id"]:
            badges.append(enums.Badges.BOT_OWNER.value)
        if member.id in coders:
            badges.append(enums.Badges.BOT_DEV.value)
        if member.id in supports:
            badges.append(enums.Badges.BOT_SUPPORT.value)
        if member.id in bug_hunters:
            badges.append(enums.Badges.BUG_HUNTER.value)
        if member.id in bug_terminators:
            badges.append(enums.Badges.BUG_TERMINATOR.value)
        if member.id in verified:
            badges.append(enums.Badges.VERIFIED.value)
        if member.bot:
            badges.append(enums.Badges.BOT.value)

        embed.add_field(
            name="Значки",
            value=" ".join(badges) if not interaction.guild or interaction.channel.permissions_for(
                interaction.guild.me).use_external_emojis else "Отсутствуют права на использование сторонних эмодзи!",
            inline=False
        )

        temp_user = await self.bot.fetch_user(member.id)
        if temp_user.banner is not None:
            embed.set_image(url=temp_user.banner.url)

        embed.add_field(
            name="Зарегистрирован в Discord",
            value=f"{dutils.format_dt(member.created_at)} ({dutils.format_dt(member.created_at, 'R')})",
            inline=False
        )        

        if isinstance(member, discord.Member):
            member = await interaction.guild.fetch_member(member.id)
            if member.nick is not None:
                embed.title += f" | {escape_markdown(member.nick)}"
            embed.add_field(
                name="Присоединился к серверу",
                value=f"{dutils.format_dt(member.joined_at)} ({dutils.format_dt(member.joined_at, 'R')})",
                inline=False
            )
            embed.add_field(
                name="Цвет никнейма",
                value=f"{str(member.color).capitalize() if member.color.value != 0 else 'Стандартный'}",
                inline=False
            )
            if member.is_timed_out():
                timeout_until = member.timed_out_until
                embed.add_field(
                    name="Время размута",
                    value=f"{dutils.format_dt(timeout_until)} ({dutils.format_dt(timeout_until, 'R')})",
                    inline=False
                )
            if self.bot.intents.presences:
                status_value = "Оффлайн"
                match member.status:
                    case discord.Status.online:
                        status_value = "Онлайн"
                    case discord.Status.idle:
                        status_value = "Нет на месте"
                    case discord.Status.dnd:
                        status_value = "Не беспокоить"
                    case _:
                        status_value = "Оффлайн"
                embed.add_field(
                    name="Статус",
                    value=status_value,
                    inline=False
                )
            member_roles = list(filter(
                lambda x: x != interaction.guild.default_role, 
                member.roles            
            ))
            member_roles.sort(key=lambda x: x.position, reverse=True)
            member_roles_amount = len(member.roles) - 1 # 'cause @everyone role counts too
            embed.add_field(
                name=f"Роли ({member_roles_amount})",
                value=", ".join([i.mention for i in member_roles]) + "" if len(member_roles) == member_roles_amount else f" и ещё {member_roles_amount - 15} ролей...",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UserInfo(bot))