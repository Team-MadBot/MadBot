import discord
import datetime

class NoPerms(discord.Embed):
    def __init__(self, perm: str):
        super().__init__(
            color=discord.Color.red(),
            title="Ошибка!",
            description=f"Вам необходимо право на `{perm}` для использования команды."
        ).set_image(
            url="https://http.cat/403"
        )

class UnknownError(discord.Embed):
    def __init__(self):
        super().__init__(
            color=discord.Color.red(),
            title="Неизвестная ошибка!",
            description=(
                "Произошла неизвестная ошибка. Пожалуйста, напишите в поддержку со следующей информацией:\n\n"
                "> `1.` Команда, которую Вы использовали.\n"
                "> `2.` Аргументы, указанные в команде (если они конфиденциальные - не указывайте)\n"
                "> `3.` Ссылка из команды `/debug`.\n"
                "> `4.` Данный скриншот."
            ),
            timestamp=datetime.datetime.now()
        ).add_field(
            name="Информация об ошибке (для понимания проблемы)",
            value=f"Время ошибки (МСК): **{datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}**"
        ).set_image(
            url="https://http.cat/400"
        )
