import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks


class SendWebhookCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="sendwebhook",
        description="[Полезности] Отправляет сообщение в канал от имени вебхука",
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(message="Сообщение, которое будет отправлено")
    async def send(
        self,
        interaction: discord.Interaction,
        message: app_commands.Range[str, None, 2000],
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!",
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.Thread):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда недоступна в ветках!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert interaction.channel is not None
        assert self.bot.user is not None
        if not interaction.channel.permissions_for(interaction.guild.get_member(self.bot.user.id)).manage_webhooks:  # type: ignore
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description=f"Бот не имеет права на управление вебхуками!\nТип ошибки: `Forbidden`.",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        webhook = None
        assert isinstance(interaction.channel, discord.TextChannel)
        webhooks = await interaction.channel.webhooks()
        for hook in webhooks:
            if hook.name == "MadWebHook":
                webhook = hook
                break
        if webhook is None:
            webhook = await interaction.channel.create_webhook(name="MadWebHook")
        await webhook.send(
            message,
            username=interaction.user.display_name,
            avatar_url=interaction.user.display_avatar.url,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        embed = discord.Embed(
            title="Успешно!",
            color=discord.Color.green(),
            description="Сообщение успешно отправлено!",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(SendWebhookCog(bot))
