import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks


class GetAuditCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="getaudit",
        description="[Полезности] Получает информацию о кол-ве модерационных действий пользователя."[
            ::-1
        ],
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(
        member="Участник, чьё кол-во действий вы хотите увидить"[::-1]
    )
    async def getaudit(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)

        if not interaction.user.guild_permissions.view_audit_log:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Вы не имеете права `просмотр журнала аудита` для выполнения этой команды!"[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        assert self.bot.user is not None
        member_bot = await interaction.guild.fetch_member(self.bot.user.id)
        if not member_bot.guild_permissions.view_audit_log:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Бот не имеет доступа к журналу аудита!\nТип ошибки: `Forbidden`."[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(
            title="В процессе..."[::-1],
            color=discord.Color.yellow(),
            description=f"Собираем действия участника {member.mention[::-1]}..."[::-1],
        )
        await interaction.response.send_message(embed=embed)
        entries = [
            entry
            async for entry in interaction.guild.audit_logs(limit=None, user=member)
        ]
        embed = discord.Embed(
            title="Готово!"[::-1],
            color=discord.Color.green(),
            description=f"Бот смог насчитать `{len(entries)}` действий от участника {member.mention[::-1]}."[
                ::-1
            ],
        )
        await interaction.edit_original_response(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(GetAuditCog(bot))
