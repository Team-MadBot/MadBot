import discord
import datetime

from discord.ext import commands
from discord import app_commands
from discord import Forbidden

from . import default_cooldown
from classes import checks


class NickCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="nick", description="[Полезности] Изменяет ваш ник.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(
        argument="Ник, на который вы хотите поменять. Оставьте пустым для сброса ника"
    )
    async def nick(self, interaction: discord.Interaction, argument: str | None = None):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!",
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not self.bot.intents.members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="На данный момент, команда недоступна.",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert self.bot.user is not None
        bot_member = await interaction.guild.fetch_member(self.bot.user.id)
        assert isinstance(interaction.user, discord.Member)
        if (
            not bot_member.guild_permissions.manage_nicknames
            or bot_member.top_role < interaction.user.top_role
        ):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не может изменить Вам никнейм!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if argument is not None and len(argument) > 32:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Длина ника не должна превышать `32 символа`!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.guild_permissions.change_nickname:
            if interaction.user.id == interaction.guild.owner_id:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Бот не может изменять никнейм владельцу сервера!",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            try:
                await interaction.user.edit(
                    nick=argument, reason="Самостоятельная смена ника"
                )
            except Forbidden:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description=f"Бот не смог изменить вам никнейм!\nТип ошибки: `Forbidden`",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            else:
                if argument is not None:
                    embed = discord.Embed(
                        title="Успешно!",
                        color=discord.Color.green(),
                        description=f"Ваш ник успешно изменён на `{argument}`!",
                        timestamp=datetime.datetime.now(),
                    )
                else:
                    embed = discord.Embed(
                        title="Успешно!",
                        color=discord.Color.green(),
                        description="Ваш ник успешно сброшен!",
                        timestamp=datetime.datetime.now(),
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            string = (
                "Вы желаете сбросить никнейм."
                if argument is None
                else f"Ваш желаемый ник: `{argument}`."
            )
            embed = discord.Embed(
                title="Запрос разрешения",
                color=discord.Color.orange(),
                description=f"Вы не имеете права на `изменение никнейма`. Попросите участника с правом на `управление никнеймами` разрешить смену ника.\n{string}",
            )
            embed.set_footer(text="Время ожидания: 5 минут.")

            class NickButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                    self.value = None

                @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
                async def confirm(self, viewinteract: discord.Interaction, button: discord.ui.Button):  # type: ignore
                    assert isinstance(viewinteract.user, discord.Member)
                    assert isinstance(interaction.user, discord.Member)

                    if not viewinteract.user.guild_permissions.manage_nicknames:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Вы не имеете права `управлять никнеймами` для использования кнопки!",
                        )
                        return await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )

                    self.value = True
                    try:
                        await interaction.user.edit(
                            nick=argument, reason=f"Одобрено // {viewinteract.user}"
                        )
                    except Forbidden:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description=f"Бот не имеет права `управление никнеймами`.\nКод ошибки: `Forbidden`.",
                        )
                        return await interaction.edit_original_response(
                            embed=embed, view=None
                        )
                    else:
                        embed = None
                        if argument is not None:
                            embed = discord.Embed(
                                title="Успешно!",
                                color=discord.Color.green(),
                                description=f"Ваш ник успешно изменён на `{argument}`!",
                                timestamp=datetime.datetime.now(),
                            )
                            embed.set_author(
                                name=viewinteract.user,
                                icon_url=viewinteract.user.display_avatar.url,
                            )
                        else:
                            embed = discord.Embed(
                                title="Успешно!",
                                color=discord.Color.green(),
                                description="Ваш ник успешно сброшен!",
                                timestamp=datetime.datetime.now(),
                            )
                            embed.set_author(
                                name=viewinteract.user,
                                icon_url=viewinteract.user.display_avatar.url,
                            )
                        await interaction.edit_original_response(embed=embed, view=None)

                @discord.ui.button(
                    emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red
                )
                async def denied(self, viewinteract: discord.Interaction, button: discord.ui.Button):  # type: ignore
                    assert isinstance(viewinteract.user, discord.Member)
                    if viewinteract.user.guild_permissions.manage_nicknames:
                        self.value = False
                        embed = discord.Embed(
                            title="Отказ",
                            color=discord.Color.red(),
                            description="Вам отказано в смене ника!",
                        )
                        embed.set_author(
                            name=viewinteract.user,
                            icon_url=viewinteract.user.display_avatar.url,
                        )
                        return await interaction.edit_original_response(
                            embed=embed, view=None
                        )
                    else:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Вы не имеете права `управлять никнеймами` для использования кнопки!",
                        )
                        return await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )

            await interaction.response.send_message(embed=embed, view=NickButtons())
            await NickButtons().wait()
            if NickButtons().value is None:
                embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
                await interaction.edit_original_response(embed=embed, view=None)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(NickCog(bot))
