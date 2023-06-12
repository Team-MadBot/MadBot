import discord
import traceback

from discord.ext import commands
from discord import app_commands, ui
from config import settings
from classes import views
from tools import db, models

class ErrorCog(commands.Cog):
    def __init__(self, bot: models.MadBot):
        self.bot = bot
        bot.tree.error(self.on_error)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.NotOwner):
            return await ctx.reply("https://cdn.discordapp.com/attachments/996413253456511096/1083467516568948829/IMG_20230309_160732_416.jpg")

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Притормози-ка!",
                color=discord.Color.red(),
                description=(
                    f"Команда `/{interaction.command.qualified_name}` имеет задержку в `{round(error.cooldown.rate)}` " # type: ignore
                    f"использование в течении `{round(error.cooldown.per)}` секунд. Пожалуйста, попробуйте снова через "
                    f"`{round(error.retry_after, 2)}` секунд."
                )
            )
            embed.set_image(url="https://http.cat/429")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(error, app_commands.CheckFailure):
            if interaction.guild.id != 1080911312600694785: # type: ignore
                embed = discord.Embed(
                    color=discord.Color.from_str("#2b2d31")
                ).set_image(url="https://http.cat/400")
                return await interaction.response.send_message(embed=embed, ephemeral=True, view=views.BotUseTry())
            if db.check_blacklist(interaction.user.id):
                blacklist = db.get_blacklist(interaction.user.id)
                embed = discord.Embed(
                    title="Вы в чёрном списке бота!",
                    color=discord.Color.red(),
                    description=(
                        "Владелец бота занёс Вас в чёрный список бота. Причина занесения находится снизу, если она есть. "
                        "Также Вы можете посмотреть, когда Вы были внесены и когда будете вынесены, если будете. "
                        "Конечно, Вы можете обжаловать решение на сервере поддержки (кнопка ниже), но, скорее всего, "
                        "решение окончательное."
                    )
                )
                embed.add_field(name="Дата занесения:", value=f"<t:{blacklist.blocked_at}> (<t:{blacklist.blocked_at}:R>)") # type: ignore
                embed.add_field(name="Причина:", value=blacklist.reason if blacklist.reason is not None else "Не указана") # type: ignore
                embed.add_field(
                    name="Дата окончания:", 
                    value=(
                        f"<t:{blacklist.blocked_until}> (<t:{blacklist.blocked_until}:R>)" if blacklist.blocked_until is not None # type: ignore
                        else "Никогда"
                    )
                )
                view = ui.View().add_item(
                    ui.Button(
                        style=discord.ButtonStyle.url, 
                        url=settings["support_invite"],
                        label="Сервер поддержки"
                    )
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка - Недостаточно прав!",
                color=discord.Color.red(),
                description=(
                    f"Вам необходимо иметь права на `{' '.join(str(x) for x in error.missing_permissions)}` "
                    "для использования команды."
                )
            ).set_image(url="https://http.cat/403")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(
            title="Жопа взломана!",
            color=discord.Color.red(),
            description=(
                "Произошла неизвестная ошибка. Пожалуйста, напишите в поддержку со следующей информацией:\n\n"
                "> `1.` Команда, которую Вы использовали.\n"
                "> `2.` Аргументы, указанные в команде (если они конфиденциальные - не указывайте)\n"
                "> `3.` Ссылка из команды `/debug`."
            )    
        )
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True, view=None) # type: ignore
        except:
            try:
                await interaction.followup.send(embed=embed, ephemeral=True, view=None) # type: ignore
            except:
                pass
        self.bot.logger.error(
            f"Command /{interaction.command.qualified_name} raised an exception:\n" # type: ignore
            f"{traceback.format_exc()}\n"
            f"==========================================="
        )
        
async def setup(bot: models.MadBot):
    await bot.add_cog(ErrorCog(bot))
