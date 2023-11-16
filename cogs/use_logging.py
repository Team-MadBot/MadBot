import logging
import discord

from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def cog_load(self):
        logging.basicConfig(
            filename="commands.log", 
            encoding='utf-8', 
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logging.disable(0)
    
    def cog_unload(self):
        logging.disable()
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.application_command: return
        logging.info(
            f"[SLASH USAGE] - '{interaction.user}' ({interaction.user.id}): '/{interaction.command.qualified_name}'"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
    print("Cog \"Logging\" запущен!")