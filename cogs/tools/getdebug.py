import discord
import config

from discord.ext import commands
from discord import app_commands

from classes import checks

class GetDebugCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="debug", description="[Полезности] Запрос основной информации о боте.")
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.checks.dynamic_cooldown(lambda i: app_commands.Cooldown(1, 300.0))
    async def debug(self, interaction: discord.Interaction):
        def get_permissions(perms: discord.Permissions) -> str:
            perms_: tuple[tuple[bool, str], ...] = (
                (perms.send_messages, "Отправка сообщений"),
                (perms.embed_links, "Добавление ссылок"),
                (perms.use_external_emojis, "Использование внешних эмодзи"),
                (perms.manage_channels, "Управление каналами"),
                (perms.kick_members, "Исключение участников"),
                (perms.ban_members, "Блокировка участников"),
                (perms.read_message_history, "Чтение истории сообщений"),
                (perms.read_messages, "Чтение сообщений"),
                (perms.moderate_members, "Управление участниками"),
                (perms.manage_nicknames, "Управление никнеймами"),
                (perms.manage_messages, "Управление сообщениями"),
                (perms.create_instant_invite, "Создание приглашений"),
                (perms.manage_guild, "Управление сервером"),
                (perms.manage_webhooks, "Управление вебхуками"),
                (perms.view_audit_log, "Журнал аудита")
            )

            #? It can be done in a oneline, but I think it's too messy and unreadable
            output: list[str] = []
            for i in perms_:
                output.append(("✅ " if i[0] else "❌ ") + i[1])
            return "\n".join(output)

        def get_vals() -> str:  # TODO rename
            assert interaction.guild is not None
            perms_ = (
                (interaction.guild.owner_id == interaction.user.id, "Создатель"),
                (user.guild_permissions.administrator, "Администратор")
            )

            #? It can be done in a oneline, but I think it's too messy and unreadable
            output: list[str] = []
            for i in perms_:
                output.append(("✅ " if i[0] else "❌ ") + i[1])
            return "\n".join(output)

        assert interaction.guild is not None
        assert isinstance(interaction.channel, discord.TextChannel)
        assert self.bot.user is not None
        bot_member = await interaction.guild.fetch_member(self.bot.user.id)
        user = await interaction.guild.fetch_member(interaction.user.id)
        embed = discord.Embed(title="Отладка", color=discord.Color.orange()).add_field(
            name="Права бота",
            value=get_permissions(bot_member.guild_permissions)
        ).add_field(
            name="Права в этом канале",
            value=get_permissions(interaction.channel.permissions_for(bot_member))
        ).add_field(
            name="Информация о сервере",
            value=(f"Имя канала:\n`{interaction.channel.name}`\nID канала:\n`{interaction.channel.id}`\n" +
                f"Кол-во каналов:\n`{len(interaction.guild.channels)}/500`\n" + 
                f"Название сервера:\n`{interaction.guild.name}`\nID сервера:\n`{interaction.guild.id}`\n" +
                f"Шард сервера:\n`{interaction.guild.shard_id}`"
            )
        ).add_field(
            name="Информация о пользователе",
            value=f"Пользователь:\n`{interaction.user}`\nID пользователя:\n`{interaction.user.id}`\nПрава:\n`{get_vals()}`"
        )
        channel = self.bot.get_channel(config.settings['debug_channel'])
        assert isinstance(channel, discord.TextChannel)
        message = await channel.send(embed=embed)
        await interaction.response.send_message(content=f"Если поддержка запросила ссылку с команды, отправьте ей это: {message.jump_url}",embed=embed)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(GetDebugCog(bot))
