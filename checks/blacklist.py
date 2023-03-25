import discord

from tools import db

def in_blacklist(interaction: discord.Interaction):
    return not db.check_blacklist(interaction.user.id)
