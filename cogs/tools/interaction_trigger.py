import discord

from discord import app_commands
from discord.ext import commands

from contextlib import suppress
from asyncio import sleep

class InteractionTrigger(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data['component_type'] == 2 and interaction.data['custom_id'].isdigit():
            with suppress(Exception):
                role_id = int(interaction.data['custom_id'])
            with suppress(Exception):
                try:
                    member = await interaction.guild.fetch_member(interaction.user.id)
                except:  # FIXME: bare except 
                    return
                role = interaction.guild.get_role(role_id)
                if role is None:
                    return
                if role_id in [role.id for role in member.roles]:
                    try:
                        await member.remove_roles(role, reason="Нажатие на кнопку")
                    except:  # FIXME: bare except
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    embed = discord.Embed(
                        title="Выбор роли", 
                        color=discord.Color.green(),
                        description=f"Роль {role.mention} успешно убрана!"
                    )
                else:
                    try:
                        await member.add_roles(role, reason="Нажатие на кнопку")
                    except:  # FIXME: bare except
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    embed = discord.Embed(
                        title="Выбор роли", 
                        color=discord.Color.green(),
                        description=f"Роль {role.mention} успешно добавлена!"
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        elif interaction.type == discord.InteractionType.component and interaction.data['component_type'] == 3 and interaction.data['values'][0].isdigit():
            await interaction.response.defer(thinking=True, ephemeral=True)
            changes = ""
            for value in interaction.data['values']:
                with suppress(Exception):
                    role_id = int(value)
                with suppress(Exception):
                    try: 
                        member = await interaction.guild.fetch_member(interaction.user.id)
                    except:  # FIXME: bare except 
                        return
                    role = interaction.guild.get_role(role_id)
                    if role is None:
                        return
                    if role_id in [role.id for role in member.roles]:
                        try:
                            await member.remove_roles(role, reason="Нажатие на кнопку")
                        except:  # FIXME: bare except
                            embed = discord.Embed(
                                title="Ошибка!",
                                color=discord.Color.red(),
                                description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                            )
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        changes += f"Роль {role.mention} успешно убрана!\n"
                    else:
                        try:
                            await member.add_roles(role, reason="Нажатие на кнопку")
                        except:  # FIXME: bare except
                            embed = discord.Embed(
                                title="Ошибка!",
                                color=discord.Color.red(),
                                description="Бот не имеет права `управлять ролями`, что необходимо для работы функции!"
                            )
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        changes += f"Роль {role.mention} успешно добавлена!\n"
            embed = discord.Embed(
                title="Выбор ролей:",
                color=discord.Color.green()
            )
            embed.add_field(name="Изменения:", value=changes)
            await interaction.followup.send(embed=embed)
        elif not(interaction.response.is_done()) and interaction.type == discord.InteractionType.component:
            await sleep(4)
            if interaction.response.is_done(): return
            embed = discord.Embed(
                title="Ошибка",
                color=discord.Color.red(),
                description="Похоже, данный компонент больше не работает. Вызовите команду для получения этого компонента снова!"
            )
            with suppress(Exception):
                await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(InteractionTrigger(bot))