import discord
import typing

from discord.ext import commands
from discord import app_commands
from discord import ui

from fluent.runtime import FluentLocalization, FluentResourceLoader

from . import hard_cooldown
from classes import checks
from classes import db

class AutoroleCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="autorole", description="Настроить выдачу одной роли при входе на сервер")
    @app_commands.describe(role="Роль для выдачи. Не указывайте её для удаления.")
    @app_commands.checks.dynamic_cooldown(hard_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def autorole(self, interaction: discord.Interaction, role: typing.Optional[discord.Role]):
        loader = FluentResourceLoader("locales/{locale}")
        l10n = FluentLocalization(["ru"], ["main.ftl", "texts.ftl", "commands.ftl"], loader)
        if interaction.guild is None:
            embed = discord.Embed(title=l10n.format_value("error_title"), color=discord.Color.red(), description=l10n.format_value("guild_only_error"))
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True) 
        if not self.bot.intents.members:
            embed = discord.Embed(
                title=l10n.format_value("error_title"),
                color=discord.Color.red(),
                description=l10n.format_value("intents_are_not_enabled")
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        if interaction.user.guild_permissions.manage_guild:
            role_info = await db.get_guild_autorole(interaction.guild.id)
            if role is None:
                if role_info is None:
                    embed = discord.Embed(
                        title=l10n.format_value("error_title"),
                        color=discord.Color.red(),
                        description=l10n.format_value("autorole_no_active_role")
                    )
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                class Buttons1(ui.View):  # Error: Объявление класса "Buttons" скрывается объявлением с тем же именем  # TODO rename
                    def __init__(self):
                        super().__init__(timeout=180)
                        self.value = None

                    @ui.button(label=l10n.format_value("yes"), style=discord.ButtonStyle.green)
                    async def yes(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                        if viewinteract.user.id != interaction.user.id:
                            return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                        await viewinteract.response.defer()
                        self.value = True
                        self.stop()

                    @ui.button(label=l10n.format_value("no"), style=discord.ButtonStyle.red)
                    async def no(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                        if viewinteract.user.id != interaction.user.id:
                            return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                        await viewinteract.response.defer()
                        self.value = True
                        self.stop()

                embed = discord.Embed(
                    title=l10n.format_value("autorole_confirm_title"),
                    color=discord.Color.orange(),
                    description=l10n.format_value("autorole_confirm_deletion", {"role": f"<@&{role_info}>"})
                )
                view = Buttons1()
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await view.wait()
                if view.value is None:
                    embed = discord.Embed(
                        title=l10n.format_value("time_exceeded"),
                        color=discord.Color.red()
                    )
                    return await interaction.edit_original_response(embed=embed, view=None)
                if not view.value:
                    return await interaction.delete_original_response()
                await db.delete_guild_autorole(interaction.guild.id)
                embed = discord.Embed(
                    title=l10n.format_value("success"),
                    color=discord.Color.green(),
                    description=l10n.format_value("autorole_deletion_success", {"role": f"<@&{role_info}>"})
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if role_info is None:
                await db.add_guild_autorole(interaction.guild.id, role.id)
                embed = discord.Embed(
                    title=l10n.format_value("success"),
                    color=discord.Color.green(),
                    description=l10n.format_value("autorole_add_success", {"role": f"<@&{role.id}>"})
                )
                return await interaction.response.send_message(embed=embed)
            class Buttons(ui.View):
                def __init__(self):
                    super().__init__(timeout=180)
                    self.value = None

                @ui.button(label=l10n.format_value("yes"), style=discord.ButtonStyle.green)
                async def yes(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                    if viewinteract.user.id != interaction.user.id:
                        return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                    await viewinteract.response.defer()
                    self.value = True
                    self.stop()

                @ui.button(label=l10n.format_value("no"), style=discord.ButtonStyle.red)
                async def no(self, viewinteract: discord.Interaction, button: ui.Button):  # type: ignore
                    if viewinteract.user.id != interaction.user.id:
                        return await interaction.response.send_message(l10n.format_value("button_click_forbidden"))
                    await viewinteract.response.defer()
                    self.value = True
                    self.stop()

            embed = discord.Embed(
                title=l10n.format_value("autorole_confirm_title"),
                color=discord.Color.orange(),
                description=l10n.format_value("autorole_confirm_update", {"role1": f"<@&{role_info}>", "role2": f"<@&{role.id}>"})
            )
            view = Buttons()
            await interaction.response.send_message(embed=embed, view=view)
            await view.wait()
            if view.value is None:
                embed = discord.Embed(
                    title=l10n.format_value("time_exceeded"),
                    color=discord.Color.red()
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if not view.value:
                return await interaction.delete_original_response()
            await db.update_guild_autorole(interaction.guild.id, role.id)
            embed = discord.Embed(
                title=l10n.format_value("success"),
                color=discord.Color.green(),
                description=l10n.format_value("autorole_update_success", {"role1": f"<@&{role_info}>", "role2": f"<@&{role.id}>"})
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title=l10n.format_value("error_title"),
                color=discord.Color.red(),
                description=l10n.format_value("perms_required_error", {"perm": l10n.format_value("perms_manage_server").lower()})            
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(AutoroleCog(bot))
