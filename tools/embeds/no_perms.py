import discord

class NoPerms(discord.Embed):
    def __init__(self, perm: str):
        super().__init__(
            color=discord.Color.red(),
            title="Ошибка!",
            description=f"Вам необходимо право на `{perm}` для использования команды."
        )