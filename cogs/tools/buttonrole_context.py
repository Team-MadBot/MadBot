import discord

from discord.ext import commands
from discord import app_commands
from discord import ui

class ButtonRoleEditRoles(ui.RoleSelect):
    def __init__(
        self, 
        default_roles: list[discord.abc.Snowflake] | None = None # TODO: use when d.py 2.4 final out
    ):
        super().__init__(
            placeholder="Выберите роли", 
            max_values=25
        )
        self.interaction: discord.Interaction | None = None
        self.selected_roles: list[discord.Role] | None = None

    async def callback(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.selected_roles = self.values

class ButtonRoleContextCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(
                name="Изменить выдачу",
                callback=self.buttonrolecontext
            )
        )

    @app_commands.guild_only()
    async def buttonrolecontext(self, interaction: discord.Interaction, message: discord.Message):
        if message.author.id != self.bot.user.id or message.components == []:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данное сообщение нельзя отредактировать!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        component = message.components[0].children[0]
        if int(component.custom_id) not in [interaction.guild.id, [r.id for r in interaction.guild.roles]]:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данное сообщение нельзя отредактировать!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        roles = [discord.Object(i.value) for i in component.options] if int(component.custom_id) == interaction.guild.id else [discord.Object(component.custom_id)]


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ButtonRoleContextCog(bot))
