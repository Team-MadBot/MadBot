import discord

from discord.ext import commands
from discord import app_commands
from discord import Forbidden

from . import default_cooldown
from classes import checks


class GetEmojiCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="getemoji", description="[Полезности] Выдает эмодзи картинкой."
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(
        emoji_name="Название, ID либо сам эмодзи.",
        is_registry="Стоит ли учитывать регистр имени?",
    )
    async def getemoji(
        self,
        interaction: discord.Interaction,
        emoji_name: str,
        is_registry: bool = False,
    ):
        if emoji_name.startswith("<") and emoji_name.endswith(">"):
            emoji_id = int(emoji_name.removesuffix(">").split(":")[2])
            emoji = self.bot.get_emoji(emoji_id)
            if emoji is None:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Данный эмодзи не обнаружен! Убедитесь, что бот есть на сервере, на котором есть эмодзи!",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            embed = discord.Embed(
                title="🤪 Информация об эмодзи",
                color=discord.Color.orange(),
                description=f"[Скачать]({emoji.url})",
            )
            embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
            embed.add_field(
                name="Вид без форматирования:", value=f"```\n{str(emoji)}```"
            )
            embed.set_footer(text=f"ID: {emoji.id}")
            embed.set_thumbnail(url=emoji.url)
            return await interaction.response.send_message(embed=embed)
        if emoji_name.isdigit():
            emoji_id = int(emoji_name)
            emoji = self.bot.get_emoji(emoji_id)
            if emoji is None:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Данный эмодзи не обнаружен! Убедитесь, что бот есть на сервере, на котором есть эмодзи!",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            embed = discord.Embed(
                title="🤪 Информация об эмодзи",
                color=discord.Color.orange(),
                description=f"[Скачать]({emoji.url})",
            )
            embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
            embed.add_field(
                name="Вид без форматирования:", value=f"```\n{str(emoji)}```"
            )
            embed.set_footer(text=f"ID: {emoji.id}")
            embed.set_thumbnail(url=emoji.url)
            return await interaction.response.send_message(embed=embed)
        embeds: list[discord.Embed] = []
        assert interaction.guild is not None
        for emoji in interaction.guild.emojis:
            x = emoji.name
            y = emoji_name
            z = str(emoji)
            if not is_registry:
                x = x.lower()
                y = y.lower()
                z = z.lower()
            if x == y or str(emoji.id) == y or z == y:
                try:
                    embed = discord.Embed(
                        title="🤪 Информация об эмодзи",
                        color=discord.Color.orange(),
                        description=f"[Скачать]({emoji.url})",
                    )
                    embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
                    embed.add_field(
                        name="Вид без форматирования:", value=f"```\n{str(emoji)}```"
                    )
                    embed.set_footer(text=f"ID: {emoji.id}")
                    embed.set_thumbnail(url=emoji.url)
                    if len(embeds) == 9:
                        embed.set_footer(
                            text="Это максимальное кол-во эмодзи, которое может быть выведено за раз."
                        )
                    if len(embeds) != 10:
                        embeds.append(embed)
                except Forbidden:
                    embed = discord.Embed(
                        title="Ошибка!",
                        color=discord.Color.red(),
                        description=f"Бот не имеет доступа к файлу эмодзи.\nТип ошибки: `Forbidden`.",
                    )
                    return await interaction.response.send_message(
                        embed=embed, ephemeral=True
                    )
        embed = discord.Embed(
            title="Ошибка!",
            color=discord.Color.red(),
            description=f"Эмодзи с данным именем не был обнаружен!\nТип ошибки: `NotFound`.",
        )
        if not len(embeds):
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(embeds=embeds)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(GetEmojiCog(bot))
