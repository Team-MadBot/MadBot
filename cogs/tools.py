# -*- coding: utf-8 -*-
import discord, datetime, sys, os, typing
from base64 import b64decode, b64encode
from asyncio import sleep, TimeoutError
from discord import NotFound, Forbidden, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from config_example import *

def is_shutted_down(interaction: discord.Interaction):
    return interaction.command.name not in shutted_down

class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.author.id in blacklist:
            return

        if message.channel.id == settings['github_channel']:
            await sleep(10) # Задержка, чтобы можно было успеть удалить сообщение.
            try:
                await message.publish()
            except:
                pass

        if message.content.startswith('Дарова, ботяра'):
            await message.reply(f' {message.author.mention} бот, не я')

        if message.content.startswith("/"):
            embed = discord.Embed(title="Команда введена неправильно!", color=discord.Color.red(), description="У бота `/` является не префиксом, а вызовом слеш-команд. Полностью очистите строку сообщений, поставьте `/` и выберите команду из списка.")
            await message.reply(embed=embed, delete_after=20)
        
        if message.author.id == 963819843142946846: # Триггер на сообщения мониторинга.
            await sleep(3)
            if message.content == "mad.debug ping":
                await message.channel.send(int(round(self.bot.latency, 3)*1000))
            if message.content == "mad.debug status":
                await message.channel.send("OK")

        if message.content.startswith(f"<@!{self.bot.user.id}>") or message.content.startswith(f"<@{self.bot.user.id}>"):
            embed=discord.Embed(title="Привет! Рад, что я тебе чем-то нужен!", color=discord.Color.orange(), description="Бот работает на слеш-командах, поэтому для взаимодействия с ботом следует использовать их. Для большей информации пропишите `/help`.")
            await message.reply(embed=embed, mention_author=False)

        await self.bot.process_commands(message)

    @app_commands.command(description="[Полезности] Показывает изменения в текущей версии.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(ver="Версия бота")
    @app_commands.choices(ver=[
        Choice(name="Актуальная", value="actual"),
        Choice(name="0.7", value='07'),
        Choice(name="0.6", value='06'),
        Choice(name="0.5", value="05"),
        Choice(name="0.4", value="04"),
        Choice(name="0.3.9", value="039"),
        Choice(name="0.3.8", value="038"),
        Choice(name="0.3.7", value="037"),
        Choice(name="0.3.6", value="036")
    ])
    async def version(self, interaction: discord.Interaction, ver: Choice[str] = None):
        global lastcommand
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/version`"
        embed = None
        if ver != None:
            ver = ver.name
        if ver == None or ver == '0.7' or ver == "Актуальная":
            updated_at = datetime.datetime(2022, 5, 8, 20, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `{settings["curr_version"]}`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Исправлена команда `/base64`.\n> 2) Обновлен дизайн `/botinfo` и `/avatar`.\n> 3) Запрос на смену ника при отсутствии права на изменение никнейма в `/nick`.\n> 4) Небольшое дополнение команды `/nsfw`.\n> 5) Авто-постинг новостей из <#953175109135376394>.\n> 6) Показ типа операционной системы, на которой запущен бот, в `/botinfo`.\n> 7) Показ списка ролей сервера в `/serverinfo`.\n> 8) Теперь приветственное сообщение будет присылаться в ЛС добавившему бота, если это возможно.\n> 9) Команда `/outages` снова работает.\n> 10) При правильном ответе, бот пишет время ответа в `/math`.\n> 11) Добавлена команда `/clearoff`.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.6':
            updated_at = datetime.datetime(2022, 5, 5, 20, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.6`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Исправление обхода проверки иерархии, используя `/banoff`.\n> 2) Добавлены контекстные меню модерации.\n> 3) Добавлены команды `/kiss` и `/hit`.\n> 4) Для поцелуя необходимо получить разрешение от второго участника.\n> 5) Добавлена первая развлекательная команда: `/math`.\n> 6) Улучшение системы мониторинга бота.\n> 7) Поддержка ввода эмодзи в `/getemoji`.\n> 8) Фильтрация гифок в `/slap`. Не хочу случайно получить бан.\n> 9) Коллаборация `/clear` и `/clearfrom`.\n> 10) Добавлен счетчик обработанных команд в `/botinfo`.\n> 11) В заголовке `/serverinfo` отображается количество ботов.\n> 12) Куча исправлений.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.5':
            updated_at = datetime.datetime(2022, 4, 18, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.5`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлена команда `/banoff`.\n> 2) Добавлены команды реакций.\n> 3) Добавлены контекстные меню. Со временем их будет больше.\n> 4) Бот оповещает участника о выдаче участнику наказания.\n> 5) Добавлена команда `/getemoji`.\n> 6) Добавлены команды `/dog` и `/cat`.\n> 7) В `/botinfo` появился показ версий Python и discord.py, а так же показ кол-ва обработанных команд.\n> 8) Добавлена команда `/nsfw`. Применение объяснять не надо (так ведь?).\n> 9) В тестовом режиме добавлена команда `/base64`. Шифрует она только латиницу.\n> 10) Теперь в `/clearfrom` можно очищать сообщения любых участников.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.4':
            updated_at = datetime.datetime(2022, 3, 27, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.4 [ОБТ]`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Исправлена команда `/serverinfo`.\n> 2) Добавлено поле "Запущено" в `/botinfo`.\n> 3) Добавлено поле "Статус" в `/userinfo`.\n> 4) Исправлена возможность выдать наказание участнику, чья роль выше либо равна роли модератора.\n> 5) Теперь надо выбирать размер аватара вместо ручного ввода в команде `/avatar`.\n> 6) Обновлена ссылка на поддержку бота в его "обо мне".\n> 7) Добавлены значки "Bug Hunter" и "Bug Terminator". Подробнее: `/badgeinfo`.\n> 8) Теперь нельзя сбрасывать ник ботам. Не спрашивайте, почему.\n> 9) Теперь пинг (который без лишнего нуля) виден в статусе бота.\n> 10) Уточнение в `/clearfrom`.\n> 11) Добавлена команда `/unban` (спустя полгода с добавления команды `/ban`).\n> 12) Добавлена команда `/idea` для публикации идей в канал <#957688771200053379>.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.3.9':
            updated_at = datetime.datetime(2022, 3, 17, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.3.9 [ОБТ]`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлены команды `/resetnick`, `/clone` и `/nick`.\n> 2) Команда `/cooldown` переименована в `/slowmode`.\n> 3) Для команд модерации добавлено обязательное указание причины.\n> 4) При ошибках в командах модерации показывается тип ошибки.\n> 5) Добавлена команда `/errors` для самостоятельного решения ошибок.\n> 6) Немного изменено оформление "обо мне" бота.\n> 7) Ошибки будут логироваться в канале логов бота на сервере поддержки. Это сделано для быстрого обнаружения проблемы и исправления её.\n> 8) При использовании команды `/nick` и отсутствии прав на изменение ника, бот запросит подтверждение изменения ника у администраторов.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.3.8':
            updated_at = datetime.datetime(2022, 3, 7, 19, 0, 0, 0)
            embed=discord.Embed(title=f'Версия `0.3.8 [ОБТ]`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Переезд на `discord.py v2.0`.\n> 2) Исправлена проблема с вводом причины в `/timeout`.\n> 3) Удалена команда `/beauty`.\n> 4) Исправлена возможность ввести значение ниже `1` в `/clear` и `/clearfrom`.\n> 5) Возможность посмотреть изменения в предыдущих версиях в `/version`.\n> 6) Теперь в `/userinfo` показывается по умолчанию серверная аватарка (если есть).\n> 7) При наличии **стандартного** баннера, он будет виден в `/userinfo`.\n> 8) Можно выбрать тип аватара (серверный либо стандартный) в `/avatar`.')
            embed.set_footer(text="Обновлено:")
        if ver == "0.3.7":
            updated_at = datetime.datetime(2022, 3, 4, 18, 0, 0, 0)
            embed=discord.Embed(title="Версия `0.3.7 [ОБТ]`", color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлены значки в `/userinfo` и `/serverinfo`.\n> 2) Добавлена команда `/badgeinfo` для ознакомления со значками.\n> 3) Исправлен баг с неактуальной ссылкой на поддержку в `/botinfo`.\n> 4) Добавлена возможность просмотра последней использованной команды бота в `/botinfo`.\n> 5) Пользователи теперь могут попасть в чёрный список бота.\n> 6) [BETA] Появилась возможность проверить, находится ли участник в чёрном списке бота.\n> 7) Можно узнать о боте, упомянув его.\n> 8) В случае, если вы будете использовать `/` как префикс бота, он вам сделает предупреждение.\n> 9) Добавлена команда `/help` для первичного ознакомления с ботом.')
            embed.set_footer(text="Обновлено:")
        if ver == '0.3.6':
            updated_at = datetime.datetime(2022, 2, 17, 9, 0, 0, 0)
            embed=discord.Embed(title="Версия `0.3.6 [ОБТ]`", color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Добавлены таймштампы в `/serverinfo` и `/userinfo`.\n> 2) Добавлено поле "Присоединился" в `/userinfo`.\n> 3) Теперь видно, когда бот перезапускается в его статусе.\n> 4) Изменена аватарка.\n> 5) Изменен порядок аргументов по умолчанию в `/clearfrom`.\n> 6) Добавлена "Защита от дурака" в `/avatar` при вводе параметра `size`.\n> 7) Добавлено поле "Кол-во участников" в `/botinfo`.')
            embed.set_footer(text="Обновлено:")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="errors", description="[Полезности] Список ошибок и решения их")
    @app_commands.check(is_shutted_down)
    async def errors(self, interaction: discord.Interaction):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/errors`"
        embed = discord.Embed(title="Ошибки бота:", color=discord.Color.orange())
        embed.add_field(name="Ошибка: Forbidden", value="Бот не может совершить действие. Убедитесь, что бот имеет право(-а) на совершение действия.", inline=False)
        embed.add_field(name="Ошибка: NotFound", value="Боту не удалось найти объект (пользователя, сервер и т.д.).", inline=False)
        embed.add_field(name="Ошибка: HTTPException", value="Бот отправил некорректный запрос на сервера Discord, из-за чего получил ошибку. Убедитесь, что вы ввели всё верно.", inline=False)
        embed.set_footer(text="В случае, если вашей ошибки нет в списке, обратитесь в поддержку.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="[Полезности] Показывает основную информацию о боте.")
    @app_commands.check(is_shutted_down)
    async def help(self, interaction: discord.Interaction):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/help`"
        embed=discord.Embed(title=f"Спасибо за использование `{self.bot.user.name}`!", color=discord.Color.orange(), description="Бот использует слеш-команды, поэтому, для запрета использования команд в определённом чате достаточно лишь отнять право у @everyone на использование слеш-команд в необходимом канале. В ближайших планах в бота будет добавлена **экономика и создатель эмбедов (с поддержкой вебхуков).** Если вам нужна поддержка - пропишите `/botinfo` и нажмите на 'Поддержка'. Обратите внимание: ЛС <@560529834325966858> предназначено только при обнаружении критического бага, если у вас просто вопрос либо незначительный баг - пишите в <#914189576090845226>!")
        embed.set_footer(text="Приятного использования!")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping", description="[Полезности] Проверка бота на работоспособность")
    @app_commands.check(is_shutted_down)
    async def ping(self, interaction: discord.Interaction):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/ping`"
        embed = discord.Embed(color=discord.Color.dark_red(), title=self.bot.user.name, description=f'⚠ **ПОНГ!!!**\n⏳ Задержка: `{int(round(self.bot.latency, 3)*1000)}ms`.')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="[Полезности] Показывает информацию о пользователе")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member='Участник')
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.DMChannel):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/userinfo`"
        global emb
        badges = ''
        guild = self.bot.get_guild(interaction.guild.id)
        for memb in interaction.guild.members:
            if memb == member:
                member = memb
                break
        if member == None:
            member = interaction.user
        if member.id in blacklist:
            badges += '<:ban:946031802634612826> '
        if member.is_timed_out():
            badges += '<:timeout:950702768782458893> '
        if member.id == settings['owner_id']:
            badges += '<:code:946056751646638180> '
        if member.id in supports:
            badges += '<:support:946058006641143858> '
        if member.id in bug_hunters:
            badges += '<:bug_hunter:955497457020715038> '
        if member.id in bug_terminators:
            badges += '<:bug_terminator:955891723152801833> '
        if member.id in verified:
            badges += '<:verified:946057332389978152> '
        if member.bot:
            badges += '<:bot:946064625525465118> '
        member = guild.get_member(member.id)
        if member.nick == None:
            emb = discord.Embed(title=f"`{member.name}#{member.discriminator}` {badges}", color=member.color)
        else:
            emb = discord.Embed(title=f"`{member.name}#{member.discriminator}` | `{member.nick}` {badges}", color=member.color)
        emb.add_field(name="Упоминание:", value=member.mention, inline=False)
        if member.status == discord.Status.online:
            emb.add_field(name="Статус:", value="🟢 В сети", inline=False)
        elif member.status == discord.Status.idle:
            emb.add_field(name="Статус:", value="🌙 Нет на месте", inline=False)
        elif member.status == discord.Status.dnd:
            emb.add_field(name="Статус:", value="🔴 Не беспокоить", inline=False)
        else:
            emb.add_field(name="Статус:", value="🔘 Не в сети", inline=False)
        emb.add_field(name="Ссылка на профиль:", value=f"[Тык](https://discord.com/users/{member.id})", inline=False)
        if member.bot:
            emb.add_field(name="Бот?:", value="Да", inline=False)
        else:
            emb.add_field(name="Бот?:", value="Нет", inline=False)
        if member.guild_permissions.administrator:
            emb.add_field(name="Администратор?:", value=f'Да', inline=False)
        else:
            emb.add_field(name="Администратор?:", value='Нет', inline=False)
        emb.add_field(name="Самая высокая роль на сервере:", value=f"{member.top_role.mention}", inline=False)
        emb.add_field(name="Акаунт был создан:", value=f"{discord.utils.format_dt(member.created_at, 'D')} ({discord.utils.format_dt(member.created_at, 'R')})", inline=False)
        emb.add_field(name="Присоединился:", value=f"{discord.utils.format_dt(member.joined_at, 'D')} ({discord.utils.format_dt(member.joined_at, 'R')})", inline=False)
        emb.set_thumbnail(url=member.display_avatar.replace(static_format="png", size=1024))
        member = await self.bot.fetch_user(member.id)
        if member.banner != None:
            emb.set_image(url=member.banner.url)
        emb.set_footer(text=f'ID: {member.id}')
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="avatar", description="[Полезности] Присылает аватар пользователя")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member='Участник, чью аватарку вы хотите получить', format="Формат изображения", size="Размер изображения", type="Тип аватара")
    @app_commands.choices(
        format=[
            Choice(name="PNG (прозрачный фон)", value="png"),
            Choice(name="JPEG (черный фон)", value="jpeg"),
            Choice(name="JPG (как JPEG)", value='jpg'),
            Choice(name="WEBP (веб-картинка)", value='webp')
        ],
        size=[
            Choice(name="16x16 пикселей", value=16),
            Choice(name="32x32 пикселей", value=32),
            Choice(name="64x64 пикселей", value=64),
            Choice(name="128x128 пикселей", value=128),
            Choice(name="256x256 пикселей", value=256),
            Choice(name="512x512 пикселей", value=512),
            Choice(name="1024x1024 пикселей", value=1024),
            Choice(name="2048x2048 пикселей", value=2048),
            Choice(name="4096x4096 пикселей", value=4096)
        ],
        type=[
            Choice(name="Стандартная", value='standart'),
            Choice(name="Серверная", value='server')
        ]
    )
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None, format: Choice[str] = "png", size: Choice[int] = 2048, type: Choice[str] = 'server'):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.DMChannel):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/avatar`"
        if member == None:
            member = interaction.user
        if format != 'png':
            format = format.value
        if size != 2048:
            size = size.value
        if type != 'server':
            type = type.value
        user_avatar = member.display_avatar
        if member.avatar != None:
            user_avatar = member.avatar
        embed = discord.Embed(color=member.color, description=f"[Скачать]({user_avatar.replace(static_format=format, size=size)})")
        embed.set_author(name=f"Аватар {member}")
        embed.set_image(url=user_avatar.replace(static_format=format, size=size))
        if type == "server":
            type = "Серверный"
        else:
            type = "Стандартный"
        embed.set_footer(text=f"Запросил: {interaction.user.name}#{interaction.user.discriminator} | Формат: {format} | Размер: {size} | Тип аватара: {type}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="[Полезности] Информация о сервере")
    @app_commands.check(is_shutted_down)
    async def serverinfo(self, interaction: discord.Interaction):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.DMChannel):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/serverinfo`"
        badges = ''
        if interaction.guild.id in blacklist:
            badges += '<:ban:946031802634612826> '
        if interaction.guild.id in verified:
            badges += '<:verified:946057332389978152> '
        if interaction.guild.id in beta_testers:
            badges += '<:beta:946063731819937812> '
        bots = 0
        for member in interaction.guild.members:
            if member.bot:
                bots += 1
        online = len(list(filter(lambda x: x.status == discord.Status.online, interaction.guild.members)))
        idle = len(list(filter(lambda x: x.status == discord.Status.idle, interaction.guild.members)))
        dnd = len(list(filter(lambda x: x.status == discord.Status.dnd, interaction.guild.members)))
        offline = len(list(filter(lambda x: x.status == discord.Status.offline, interaction.guild.members)))
        embed = discord.Embed(title=f"{interaction.guild.name} {badges}", color=discord.Color.orange(), description=f"🟢 `{online}` | 🌙 `{idle}` | 🔴 `{dnd}` | ⚪ `{offline}`")
        embed.add_field(name="Владелец:", value=interaction.guild.owner.mention, inline=True)
        if interaction.guild.default_notifications == "all_messages":
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Все сообщения", inline=True)
        else:
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Только @упоминания", inline=True)
        embed.add_field(name="Кол-во каналов:", value=len(interaction.guild.channels) - len(interaction.guild.categories), inline=True)
        embed.add_field(name="Кол-во категорий:", value=len(interaction.guild.categories), inline=True)
        embed.add_field(name="Текстовых каналов:", value=len(interaction.guild.text_channels), inline=True)
        embed.add_field(name="Голосовых каналов:", value=len(interaction.guild.voice_channels), inline=True)
        embed.add_field(name="Трибун:", value=len(interaction.guild.stage_channels), inline=True)
        embed.add_field(name="Участники:", value=f"**Всего:** {interaction.guild.member_count}.\n**Участники:** {interaction.guild.member_count - bots}.\n**Боты:** {bots}.", inline=True)
        embed.add_field(name="Кол-во эмодзи:", value=f"{len(interaction.guild.emojis)}/{interaction.guild.emoji_limit * 2}", inline=True)
        temp = interaction.guild.verification_level
        if temp == discord.VerificationLevel.none:
            embed.add_field(name="Уровень проверки:", value="Отсутствует", inline=True)
        elif temp == discord.VerificationLevel.low:
            embed.add_field(name="Уровень проверки:", value="Низкий", inline=True)
        elif temp == discord.VerificationLevel.medium:
            embed.add_field(name="Уровень проверки:", value="Средний", inline=True)
        elif temp == discord.VerificationLevel.high:
            embed.add_field(name="Уровень проверки:", value="Высокий", inline=True)
        elif temp == discord.VerificationLevel.very_high:
            embed.add_field(name="Уровень проверки:", value="Очень высокий", inline=True)
        embed.add_field(name="Дата создания:", value=f"{discord.utils.format_dt(interaction.guild.created_at, 'D')} ({discord.utils.format_dt(interaction.guild.created_at, 'R')})", inline=True)
        if interaction.guild.rules_channel != None:
            embed.add_field(name="Канал с правилами:", value=interaction.guild.rules_channel.mention)
        else:
            embed.add_field(name="Канал с правилами:", value="Недоступно (сервер не является сервером сообщества)")
        roles = ""
        counter = 0
        guild_roles = await interaction.guild.fetch_roles()
        for role in guild_roles:
            if counter == 0:
                counter += 1
                continue
            if counter <= 15:
                roles += f"{role.mention}, "
            else:
                roles += f"и ещё {len(guild_roles) - 15}..."
                break
            counter += 1
        embed.add_field(name=f"Роли ({len(interaction.guild.roles)}):", value=roles)
        if interaction.guild.icon != None:
            embed.set_thumbnail(url=interaction.guild.icon.replace(static_format="png", size=1024))
        if interaction.guild.banner != None:
            embed.set_image(url=interaction.guild.banner.replace(static_format="png"))
        embed.set_footer(text=f"ID: {interaction.guild.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="[Полезности] Информация о боте")
    @app_commands.check(is_shutted_down)
    async def botinfo(self, interaction: discord.Interaction):
        global lastcommand, used_commands
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        members = 0
        for guild in self.bot.guilds:
            for member in guild.members:
                if not(member.bot):
                    members += 1
        embed = discord.Embed(title=self.bot.user.name, color=discord.Color.orange())
        embed.add_field(name="Версия:", value=settings['curr_version'])
        embed.add_field(name="Версия discord.py:", value=f"{discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro} `{discord.version_info.releaselevel.upper()}`")
        embed.add_field(name="Версия Python:", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        ver_info = sys.platform
        if ver_info.startswith("win32"):
            ver_info = "Windows"
        if ver_info.startswith("linux"):
            ver_info = "Linux"
        if ver_info.startswith("aix"):
            ver_info = "AIX"
        if ver_info.startswith("darwin"):
            ver_info = "MacOS"
        embed.add_field(name="Операционная система:", value=ver_info)
        embed.add_field(name="Пинг:", value=f"{int(round(self.bot.latency, 3)*1000)}ms")
        embed.add_field(name="Запущен:", value=f"<t:{started_at}:R>")
        embed.add_field(name="Кол-во серверов:", value=len(self.bot.guilds))
        embed.add_field(name="Кол-во участников:", value=members)
        owner = await self.bot.fetch_user(settings['owner_id'])
        embed.add_field(name="Разработчик:", value=f"{owner.mention} (ID: 560529834325966858)")
        embed.add_field(name="Ссылки", value=f"[Поддержка]({settings['support_invite']})\n[Добавить на сервер](https://discord.com/oauth2/authorize?client_id={settings['client_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands)")
        embed.add_field(name="Последняя использованная команда:", value=lastcommand)
        embed.add_field(name="Кол-во команд/контекстных меню:", value=f"{len(self.bot.tree.get_commands(type=discord.AppCommandType.chat_input))}/{len(self.bot.tree.get_commands(type=discord.AppCommandType.user)) + len(self.bot.tree.get_commands(type=discord.AppCommandType.message))}")
        embed.add_field(name="Обработано команд:", value=used_commands)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(text=f"ID бота: {self.bot.user.id}")
        await interaction.response.send_message(embed=embed)
        lastcommand = "`/botinfo`"
        used_commands += 1

    @app_commands.command(name="badgeinfo", description="[Полезности] Информация о значках пользователей и серверов в боте.")
    @app_commands.check(is_shutted_down)
    async def badgeinfo(self, interaction: discord.Interaction):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/badgeinfo`"
        embed=discord.Embed(title="Виды значков:", color=discord.Color.orange())
        embed.add_field(name="Значки пользователя:", value=f"<:ban:946031802634612826> - пользователь забанен в системе бота.\n<:timeout:950702768782458893> - пользователь получил тайм-аут на сервере.\n<:code:946056751646638180> - разработчик бота.\n<:support:946058006641143858> - поддержка бота.\n<:bug_hunter:955497457020715038> - охотник на баги (обнаружил и сообщил о 3-х и более багах).\n<:bug_terminator:955891723152801833> - уничтожитель багов (обнаружил и сообщил о 10-ти и более багах).\n<:verified:946057332389978152> - верифицированный пользователь.\n<:bot:946064625525465118> - участник является ботом.", inline=False)
        embed.add_field(name="Значки сервера:", value=f"<:verified:946057332389978152> - верифицированный сервер.\n<:ban:946031802634612826> - сервер забанен в системе бота.\n<:beta:946063731819937812> - сервер, имеющий доступ к бета-командам.", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='outages', description="[Полезности] Показывает актуальные сбои в работе бота.")
    @app_commands.check(is_shutted_down)
    async def outages(self, interaction: discord.Interaction):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/outages`'
        channel = await self.bot.fetch_channel(settings['outages'])
        outage = None
        async for message in channel.history(limit=1):
            outage = message
        if message.content.find("<:outage_fixed:958778052136042616>") == -1:
            embed = discord.Embed(title="Обнаружено сообщение о сбое!", color=discord.Color.red(), description=outage.content, timestamp=outage.created_at)
            embed.set_author(name=outage.author, icon_url=outage.author.display_avatar.url)
            embed.set_footer(text="Актуально на")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Актуальные сбои отсутствуют", color=discord.Color.green(), description="Спасибо, что пользуетесь MadBot!", timestamp=discord.utils.utcnow())
            embed.set_footer(text="Актуально на")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nick", description="[Полезности] Изменяет ваш ник.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(argument="Ник, на который вы хотите поменять. Оставьте пустым для сброса ника")
    async def nick(self, interaction: discord.Interaction, argument: str = None):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.DMChannel):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = "`/nick`"
        if argument != None:
            if len(argument) > 32:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Длина ника не должна превышать `32 символа`!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.guild_permissions.change_nickname:
            if interaction.user.id == interaction.guild.owner.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не может изменять никнейм владельцу сервера!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            try:
                await interaction.user.edit(nick=argument, reason="Самостоятельная смена ника")
            except Forbidden:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не смог изменить вам никнейм!\nТип ошибки: `Forbidden`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = None
                if argument != None:
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Ваш ник успешно изменён на `{argument}`!", timestamp=discord.utils.utcnow())
                else:
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ваш ник успешно сброшен!", timestamp=discord.utils.utcnow())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            string = None
            if argument == None:
                string = "Вы желаете сбросить никнейм."
            else:
                string = f"Ваш желаемый ник: `{argument}`."
            embed = discord.Embed(title="Запрос разрешения", color=discord.Color.orange(), description=f"Вы не имеете права на `изменение никнейма`. Попросите участника с правом на `управление никнеймами` разрешить смену ника.\n{string}")
            embed.set_footer(text="Время ожидания: 5 минут.")
            await interaction.response.send_message(embed=embed)
            bot_message = await interaction.original_message()
            await bot_message.add_reaction("✅")
            await bot_message.add_reaction("❌")
            def check(reaction: discord.Reaction, user: discord.Member):
                return user.guild_permissions.manage_nicknames and (reaction.emoji == "✅" or reaction.emoji == "❌")
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=300)
            except TimeoutError:
                embed = discord.Embed(title="Запрос разрешения", color=discord.Color.red(), description="Время истекло!")
                await bot_message.clear_reactions()
                return await interaction.edit_original_message(embed=embed)
            else:
                if reaction.emoji == "❌":
                    embed = discord.Embed(title="Отказ", color=discord.Color.red(), description="Вам отказано в смене ника!")
                    embed.set_author(name=user, icon_url=user.display_avatar.url)
                    await bot_message.clear_reactions()
                    return await interaction.edit_original_message(embed=embed)
                try:
                    await interaction.user.edit(nick=argument, reason=f"Одобрено // {user}")
                except Forbidden:
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права `управление никнеймами`.\nКод ошибки: `Forbidden`.")
                    return await interaction.edit_original_message(embed=embed)
                else:
                    embed = None
                    if argument != None:
                        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Ваш ник успешно изменён на `{argument}`!", timestamp=discord.utils.utcnow())
                        embed.set_author(name=user, icon_url=user.display_avatar.url)
                    else:
                        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ваш ник успешно сброшен!", timestamp=discord.utils.utcnow())
                        embed.set_author(name=user, icon_url=user.display_avatar.url)
                    await bot_message.clear_reactions()
                    await interaction.edit_original_message(embed=embed)

    @app_commands.command(name="idea", description="[Полезности] Предложить идею для бота.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(title="Суть идеи", description="Описание идеи", attachment="Изображение для показа идеи")
    async def idea(self, interaction: discord.Interaction, title: str, description: str, attachment: typing.Optional[discord.Attachment]):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/idea`'
        idea_embed = discord.Embed(title=title, color=discord.Color.orange(), description=description, timestamp=discord.utils.utcnow())
        idea_embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar)
        if attachment != None:
            idea_embed.set_image(url=attachment.url)
        channel = self.bot.get_channel(settings['idea_channel'])
        message = await channel.send(embed=idea_embed)
        await message.add_reaction("✅")
        await message.add_reaction("💤")
        await message.add_reaction("❌")
        embed = discord.Embed(title='Успешно!', color=discord.Color.green(), description="Идея отправлена в канал")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="getemoji", description="[Полезности] Выдает эмодзи картинкой.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(emoji_name="Название, ID либо сам эмодзи.", is_registry="Стоит ли учитывать регистр имени?")
    async def getemoji(self, interaction: discord.Interaction, emoji_name: str, is_registry: bool = False):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/getemoji`'
        embeds = []
        for emoji in interaction.guild.emojis:
            x = emoji.name
            y = emoji_name
            z = str(emoji)
            if not is_registry:
                x = x.lower()
                y = y.lower()
                z = z.lower()
            if x == y or str(emoji.id) == y or z == y:
                try:
                    embed = discord.Embed(title="🤪 Информация об эмодзи", color=discord.Color.orange(), description=f"[Скачать]({emoji.url})")
                    embed.add_field(name="Название:", value=f"```\n{emoji.name}```")
                    embed.add_field(name="Вид без форматирования:", value=f"```\n{str(emoji)}```")
                    embed.set_footer(text=f"ID: {emoji.id}")
                    embed.set_thumbnail(url=emoji.url)
                    if len(embeds) == 9:
                        embed.set_footer(text="Это максимальное кол-во эмодзи, которое может быть выведено за раз.")
                    if len(embeds) != 10:
                        embeds.append(embed)
                except Forbidden:
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет доступа к файлу эмодзи.\nТип ошибки: `Forbidden`.")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Эмодзи с данным именем не был обнаружен!\nТип ошибки: `NotFound`.")
        if len(embeds) == 0:
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(embeds=embeds)

    @app_commands.command(name="base64", description="[Полезности] (Де-)кодирует указанный текст в Base64.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(make="Что нужно сделать с текстом?", text="Текст для (де-)кодировки")
    @app_commands.choices(make=[
        Choice(name="Кодировать", value="encode"),
        Choice(name="Декодировать", value="decode")
    ])
    async def base64(self, interaction: discord.Interaction, make: Choice[str], text: str):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/base64`'
        if make.value == "encode":
            ans = text.encode("utf8")
            ans = b64encode(ans)
            ans = str(ans).removeprefix("b'")
            ans = str(ans).removesuffix("'")
            embed = discord.Embed(title="Зашифровка:", color=discord.Color.orange())
            embed.add_field(name="Исходный текст:", value=text, inline=False)
            embed.add_field(name="Полученный текст:", value=ans)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        if make.value == "decode":
            ans = b64decode(text)
            ans = ans.decode("utf8")
            embed = discord.Embed(title="Расшифровка:", color=discord.Color.orange())
            embed.add_field(name="Исходный текст:", value=text, inline=False)
            embed.add_field(name="Полученный текст:", value=ans)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="send", description="[Полезности] Отправляет сообщение в канал от имени вебхука")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(message="Сообщение, которое будет отправлено")
    async def send(self, interaction: discord.Interaction, message: str):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/send`'
        if interaction.channel.permissions_for(interaction.guild.get_member(self.bot.user.id)).manage_webhooks == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на управление вебхуками!\nТип ошибки: `Forbidden`.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        webhook = None
        webhooks = await interaction.channel.webhooks()
        for hook in webhooks:
            if hook.name == "MadWebHook":
                webhook = hook
                break
        if webhook == None:
            webhook = await interaction.channel.create_webhook(name="MadWebHook")
        await webhook.send(message, username=interaction.user.name, avatar_url=interaction.user.display_avatar.url)
        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Сообщение успешно отправлено!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="getaudit", description="[Полезности] Получает информацию о кол-ве модерационных действий пользователя.")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(member="Участник, чьё кол-во действий вы хотите увидить")
    async def getaudit(self, interaction: discord.Interaction, member: discord.Member):
        global lastcommand, used_commands
        used_commands += 1
        if interaction.user.id in blacklist:
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        lastcommand = '`/getaudit`'
        if interaction.user.guild_permissions.view_audit_log:
            member_bot = await interaction.guild.fetch_member(self.bot.user.id)
            if member_bot.guild_permissions.view_audit_log == False:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет доступа к журналу аудита!\nТип ошибки: `Forbidden`.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            embed = discord.Embed(title="В процессе...", color=discord.Color.yellow(), description=f"Собираем действия участника {member.mention}...")
            await interaction.response.send_message(embed=embed)
            entries = [entry async for entry in interaction.guild.audit_logs(limit=None, user=member)]
            embed = discord.Embed(title="Готово!", color=discord.Color.green(), description=f"Бот смог насчитать `{len(entries)}` действий от участника {member.mention}.")
            await interaction.edit_original_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `просмотр журнала аудита` для выполнения этой команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tools(bot))
    print('Cog "Tools" запущен.')