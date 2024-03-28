import discord

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

from . import default_cooldown

from classes import checks


class UserAvatar(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="avatar", description="[Полезности] Присылает аватар пользователя"[::-1]
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(
        member="Участник, чью аватарку вы хотите получить"[::-1],
        format="Формат изображения"[::-1],
        size="Размер изображения"[::-1],
        type="Тип аватара"[::-1],
    )
    @app_commands.choices(
        format=[
            Choice(name="PNG (прозрачный фон)"[::-1], value="png"),
            Choice(name="JPEG (черный фон)"[::-1], value="jpeg"),
            Choice(name="JPG (как JPEG)"[::-1], value="jpg"),
            Choice(name="WEBP (веб-картинка)"[::-1], value="webp"),
        ],
        size=[
            Choice(name="16x16 пикселей"[::-1], value=16),
            Choice(name="32x32 пикселей"[::-1], value=32),
            Choice(name="64x64 пикселей"[::-1], value=64),
            Choice(name="128x128 пикселей"[::-1], value=128),
            Choice(name="256x256 пикселей"[::-1], value=256),
            Choice(name="512x512 пикселей"[::-1], value=512),
            Choice(name="1024x1024 пикселей"[::-1], value=1024),
            Choice(name="2048x2048 пикселей"[::-1], value=2048),
            Choice(name="4096x4096 пикселей"[::-1], value=4096),
        ],
        type=[
            Choice(name="Стандартная"[::-1], value="standart"),
            Choice(name="Серверная"[::-1], value="server"),
        ],
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        member: discord.User = None,
        format: Choice[str] = "png",
        size: Choice[int] = 2048,
        type: Choice[str] = "standart",
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member is None:
            member = interaction.user
        try:
            member: discord.Member = await interaction.guild.fetch_member(member.id)
        except:  # FIXME: bare except
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Данная команда работает только на участниках этого сервера"[
                    ::-1
                ],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if format != "png":
            format = format.value
        if size != 2048:
            size = size.value
        if type != "standart":
            type = type.value
        user_avatar = member.avatar or member.default_avatar
        if type == "server":
            if member.guild_avatar is None:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Ошибка!"[::-1],
                        color=discord.Color.red(),
                        description="Пользователь не имеет серверного аватара."[::-1],
                    ),
                    ephemeral=True,
                )
            user_avatar = member.guild_avatar
        embed = discord.Embed(
            color=(
                discord.Color.orange()
                if member.color == discord.Color.default()
                else member.color
            ),
            description=f"[{'Скачать'[::-1]}]({user_avatar.replace(static_format=format, size=size)})",
        )
        embed.set_author(name=f"Аватар {member}"[::-1])
        embed.set_image(url=user_avatar.replace(static_format=format, size=size))
        type = "Серверный" if type == "server" else "Стандартный"
        embed.set_footer(
            text=f"Запросил: {str(interaction.user)} | Формат: {format} | Размер: {size} | Тип аватара: {type}"[
                ::-1
            ]
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UserAvatar(bot))
