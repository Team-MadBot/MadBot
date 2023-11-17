import discord
import aiohttp

from discord.ext import commands
from discord import app_commands
from discord import ui

from classes import checks
from classes.db import is_voted, add_voter

class ConfirmVote(ui.View):
    def __init__(self, webhook: discord.Webhook):
        super().__init__(timeout=180)
        self.webhook = webhook
    
    @ui.button(label="Да", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, _):
        if is_voted(interaction.user.id):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы уже проголосовали."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        add_voter(interaction.user.id)

        embed = discord.Embed(
            title="Голосование",
            color=discord.Color.orange(),
            description=f"Появился новый голос от пользователя `{interaction.user}` (`{interaction.user.id}`)."
        ).add_field(
            name="Дата регистрации",
            value=f"<t:{round(interaction.user.created_at.timestamp())}> (<t:{round(interaction.user.created_at.timestamp())}:R>)"
        ).set_footer(
            text=f"ID пользователя: {interaction.user.id}."
        ).set_author(
            name=interaction.user,
            icon_url=interaction.user.display_avatar.url
        )
        await self.webhook.send(embed=embed)

        embed = discord.Embed(
            title="Голосование - Подтверждено",
            color=discord.Color.green(),
            description="Спасибо, что подтвердили свой голос."
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, _):
        self.stop()
        await interaction.message.delete()

class VoteCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.webhook = discord.Webhook.from_url(
            "https://discord.com/api/webhooks/1127555690211323934/AXrl_YvRixJFmP_EkAtnU_NdhMuxfmOlQO2jThCXbC1TUEZNC_yQoYgHAZJ_WpRXtsBO",
            session=aiohttp.ClientSession()
        )
    
    @app_commands.command(name="vote", description="Подтвердить голосование на выборах.")
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    async def vote(self, interaction: discord.Interaction):
        if (datetime.datetime.now() - interaction.user.created_at).days < 60:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Ваш аккаунт слишком молод для голосования."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if is_voted(interaction.user.id):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы уже голосовали!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="Подтвердите голос",
            color=discord.Color.orange(),
            description="Нажимая на \"Да\", вы соглашаетесь, что Вы проголосовали в [опросе](https://forms.gle/uhwY7fYetrxqjarf9) "
            "и Вы согласны с тем, что если Вы голосуете с мультиаккаунта, чёрный список бота будет выдан на ВСЕ аккаунты. "
            "**НЕ НАЖИМАЙТЕ НА КНОПКУ, ЕСЛИ ВЫ НЕ ГОЛОСОВАЛИ, ИНАЧЕ ВЫ МОЖЕТЕ ПОЛУЧИТЬ ЧЁРНЫЙ СПИСОК БОТА!!!**"
        )
        await interaction.response.send_message(embed=embed, view=ConfirmVote(webhook=self.webhook), ephemeral=True)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(VoteCog(bot))
