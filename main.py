# -*- coding: utf-8 -*-
"""
Исходный код MadBot'a. Для корректной работы установите все библиотеки из
requirements.txt (pip install -r requirements.txt). Код закомментирован для 
простоты редактирования. Для работы отредактируйте файл config_example.py и
запустите main.py
"""
import os, sys, datetime, time, discord, requests, random
from hmtai import useHM
from base64 import b64encode, b64decode
from pypresence import Presence
from discord.app_commands import Choice
from discord import Forbidden, NotFound, app_commands
from discord.ext import commands
from asyncio import sleep, TimeoutError
from config_example import *


used_commands = 0 # Счетчик использований команд
key = settings['key']
bot = commands.Bot(command_prefix='mad.', intents=discord.Intents.all())
started_at = int(time.mktime(discord.utils.utcnow().timetuple()) + 10800)
actual_outage = None
owner_id = settings['owner_id']
lastcommand = 'Ещё ни разу команды не использовались'
curr_version = settings['curr_version']

btns=[
    {
        "label": "Добавить бота",
        "url": f"https://discord.com/oauth2/authorize?client_id={settings['client_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands"
    },
    {
        "label": "Поддержка бота",
        "url": settings['support_invite']
    }
]
try:
    RPC = Presence(f"{settings['client_id']}") # Discord Rich Presence. Будет видно при запуске бота.
except:
    pass
else:
    try:
        RPC.connect()
    except:
        pass
    else:
        RPC.update(
            state=f"Бот запущен.",
            details="Работа над ботом.",
            start=time.time(),
            large_image="mad_cat_default",
            large_text="MadBot - запущен",
            buttons=btns
        )


@bot.event
async def on_connect():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Перезагрузка..."))
    print("Соединено! Авторизация...")


@bot.event
async def on_ready():
    global started_at
    server = bot.get_guild(settings['server']) # Сервер логов.
    logs = server.get_channel(settings['log_channel']) # Канал логов.
    channel = bot.get_channel(967484036127813713) # Канал "общения" мониторинга. Закомментируйте, если хотите.
    for guild in bot.guilds: # Проверка на нахождение в чёрном списке.
        if guild.id in blacklist:
            await guild.leave()
            print(f"Бот вышел из {guild.name} ({guild.id})")
    print(f"Авторизация успешна! {bot.user} готов к работе!")
    if round(bot.latency, 3)*1000 < 90:
        started_at -= 10800
    embed = discord.Embed(title="Бот перезапущен!", color=discord.Color.red(), description=f"Пинг: `{int(round(bot.latency, 3)*1000)}ms`\nВерсия: `{curr_version}`")
    await logs.send(embed=embed)
    await channel.send("OK") # Канал "общения" мониторинга. Закомментируйте, если хотите.
    while True:
        if actual_outage == None:
            await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} серверов | {int(round(bot.latency, 3)*1000)}ms"))
        await sleep(60)


@bot.tree.error
async def on_error(interaction: discord.Interaction, error):
    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Произошла неизвестная ошибка! Обратитесь в поддержку со скриншотом ошибки!\n```\n{error}```", timestamp=discord.utils.utcnow())
    channel = bot.get_channel(settings['log_channel'])
    await channel.send(f"```\nOn command '{interaction.command.name}'\n{error}```")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.edit_original_message(embeds=[embed])
    print(error)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    await ctx.message.add_reaction("❌")
    await ctx.message.reply(f"```\n{error}```", delete_after=30)
    channel = bot.get_channel(settings['log_channel'])
    await channel.send(f'```\nOn message "{ctx.message.content}"\n\n{error}```')
    print(error)
    await sleep(30)
    await ctx.message.delete()


@bot.event
async def on_guild_join(guild: discord.Guild):
    if guild.id in blacklist or guild.owner.id in blacklist: # Проверка на чёрный список.
        embed=discord.Embed(title="Ваш сервер либо вы сами занесён(-ы) в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс ваш сервер либо вас в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=guild.icon_url)
        try:
            await guild.owner.send(embed=embed)
        except:
            pass
        await guild.leave()
        print(f"Бот вышел из {guild.name} ({guild.id})")
    else: 
        await sleep(1)
        embed = discord.Embed(title=f"Спасибо за добавление {bot.user.name} на сервер {guild.name}", color=discord.Color.orange(), description=f"Перед использованием убедитесь, что слеш-команды включены у вас на сервере. Ваш сервер: `{len(bot.guilds)}-ый`.")
        embed.add_field(name="Поддержка:", value=settings['support_invite'])
        embed.set_thumbnail(url=bot.user.avatar.url)
        adder = None
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
                if entry.target.id == bot.user.id:
                    adder = entry.user
        except Forbidden:
            adder = guild.owner
            embed.set_footer(text="Бот написал вам, так как не смог уточнить, кто его добавил.")
        try:
            await adder.send(embed=embed)
        except:
            pass
        embed = discord.Embed(title="Новый сервер!", color=discord.Color.green())
        embed.add_field(name="Название:", value=f"`{guild.name}`")
        embed.add_field(name="Владелец:", value=f"{guild.owner.mention}")
        embed.add_field(name="ID сервера:", value=f"`{guild.id}`")
        embed.add_field(name="Кол-во участников:", value=f"`{guild.member_count}`")
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass
        log_channel = bot.get_channel(settings['log_channel'])
        await log_channel.send(embed=embed)
        await bot.tree.sync()


@bot.event # Эксклюзив для MadBot Support.
async def on_member_join(member: discord.Member):
    if member.guild.id == 914181806285279232 and not(member.bot):
        channel = member.guild.get_channel(914191453738119240)
        embed = discord.Embed(title='Новый участник!', color=discord.Color.green(), description=f"Пользователь {member.mention} присоединился к серверу.", timestamp=member.joined_at)
        embed.add_field(name="Дата регистрации:", value=f"{discord.utils.format_dt(member.created_at, 'D')} ({discord.utils.format_dt(member.created_at, 'R')})", inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"ID участника: {member.id}")
        try:
            embed.set_image(url=f"https://some-random-api.ml/welcome/img/5/gaming4?key={key}&type=join&username={member.name}&discriminator={member.discriminator}&memberCount={member.guild.member_count}&guildName=MadBot%20Support&avatar={member.display_avatar.url}&textcolor=orange")
        except:
            pass
        await channel.send(embed=embed)


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.author.id in blacklist:
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
            await message.channel.send(int(round(bot.latency, 3)*1000))
        if message.content == "mad.debug status":
            await message.channel.send("OK")

    if message.content.startswith(f"<@!{bot.user.id}>") or message.content.startswith(f"<@{bot.user.id}>"):
        embed=discord.Embed(title="Привет! Рад, что я тебе чем-то нужен!", color=discord.Color.orange(), description="Бот работает на слеш-командах, поэтому для взаимодействия с ботом следует использовать их. Для большей информации пропишите `/help`.")
        await message.reply(embed=embed, mention_author=False)

    await bot.process_commands(message)


bot.remove_command('help')


@bot.tree.command(description="[Полезности] Показывает изменения в текущей версии.")
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
async def version(interaction: discord.Interaction, ver: Choice[str] = None):
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
        embed=discord.Embed(title=f'Версия `{curr_version}`', color=discord.Color.orange(), timestamp=updated_at, description=f'> 1) Исправлена команда `/base64`.\n> 2) Обновлен дизайн `/botinfo` и `/avatar`.\n> 3) Запрос на смену ника при отсутствии права на изменение никнейма в `/nick`.\n> 4) Небольшое дополнение команды `/nsfw`.\n> 5) Авто-постинг новостей из <#953175109135376394>.\n> 6) Показ типа операционной системы, на которой запущен бот, в `/botinfo`.\n> 7) Показ списка ролей сервера в `/serverinfo`.\n> 8) Теперь приветственное сообщение будет присылаться в ЛС добавившему бота, если это возможно.\n> 9) Команда `/outages` снова работает.\n> 10) При правильном ответе, бот пишет время ответа в `/math`.\n> 11) Добавлена команда `/clearoff`.')
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


@bot.tree.command(name="errors", description="[Полезности] Список ошибок и решения их")
async def errors(interaction: discord.Interaction):
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


@bot.tree.command(name="help", description="[Полезности] Показывает основную информацию о боте.")
async def help(interaction: discord.Interaction):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = "`/help`"
    embed=discord.Embed(title=f"Спасибо за использование `{bot.user.name}`!", color=discord.Color.orange(), description="Бот использует слеш-команды, поэтому, для запрета использования команд в определённом чате достаточно лишь отнять право у @everyone на использование слеш-команд в необходимом канале. В ближайших планах в бота будет добавлена **экономика и создатель эмбедов (с поддержкой вебхуков).** Если вам нужна поддержка - пропишите `/botinfo` и нажмите на 'Поддержка'. Обратите внимание: ЛС <@560529834325966858> предназначено только при обнаружении критического бага, если у вас просто вопрос либо незначительный баг - пишите в <#914189576090845226>!")
    embed.set_footer(text="Приятного использования!")
    embed.set_thumbnail(url=bot.user.avatar.url)
    await interaction.response.send_message(embed=embed)


@bot.command()
async def help(ctx):
    global lastcommand, used_commands
    used_commands += 1
    if ctx.author.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=ctx.author.avatar.url)
        return await ctx.send(embed=embed)
    lastcommand = "`mad.help`"
    embed=discord.Embed(title=f"Спасибо за использование `{bot.user.name}`!", color=discord.Color.orange(), description="Заранее сообщу о том, что мы используем слеш-команды! Скоро и эта команда будет недоступной! Используйте `/help`!")
    embed.set_footer(text="Приятного использования!")
    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=embed)


@bot.tree.command(name="ping", description="[Полезности] Проверка бота на работоспособность")
async def ping(interaction: discord.Interaction):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = "`/ping`"
    embed = discord.Embed(color=discord.Color.dark_red(), title=bot.user.name, description=f'⚠ **ПОНГ!!!**\n⏳ Задержка: `{int(round(bot.latency, 3)*1000)}ms`.')
    await interaction.response.send_message(embed=embed)
    

@bot.tree.command(name="userinfo", description="[Полезности] Показывает информацию о пользователе")
@app_commands.describe(member='Участник')
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
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
    guild = bot.get_guild(interaction.guild.id)
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
    if member.id == owner_id:
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
    member = await bot.fetch_user(member.id)
    if member.banner != None:
        emb.set_image(url=member.banner.url)
    emb.set_footer(text=f'ID: {member.id}')
    await interaction.response.send_message(embed=emb)


@bot.tree.command(name="kick", description="[Модерация] Выгнать участника с сервера")
@app_commands.describe(member='Участник, который будет исключен', reason="Причина кика")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
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
    lastcommand = "`/kick`"
    if interaction.user.guild_permissions.kick_members:
        member_bot = None
        for temp_member in interaction.guild.members:
            if temp_member.id == bot.user.id:
                member_bot = temp_member
        if (member.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == member.id) and interaction.guild.owner.id != interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == member.id or member_bot.guild_permissions.kick_members == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на исключение данного участника!\nТип ошибки: `Forbidden`.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title=f'Участник выгнан с сервера {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Участник:", value=f"{member.mention}", inline=True)
        embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="Причина:", value=f"{reason}", inline=True)
        try:
            await member.send(embed=embed)
        except:
            embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
        await member.kick(reason=f"{reason} // {interaction.user.name}")
        return await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description='У вас недостаточно прав для использования команды')
        return await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ban", description="[Модерация] Забанить участника на сервере")
@app_commands.describe(member='Участник, который будет забанен', reason="Причина бана", delete_message_days="За какой период дней удалить сообщения.")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str, delete_message_days: app_commands.Range[int, 0, 7] = 0):
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
    lastcommand = "`/ban`"
    if interaction.user.guild_permissions.ban_members:
        member_bot = None
        for temp_member in interaction.guild.members:
            if temp_member.id == bot.user.id:
                member_bot = temp_member
        if (member.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == member.id) and interaction.guild.owner.id != interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == member.id or member_bot.guild_permissions.ban_members == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на бан данного участника!\nТип ошибки: `Forbidden`.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = discord.Embed(title=f'Участник забанен на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Участник:", value=f"{member.mention}", inline=True)
        embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="Причина:", value=f"{reason}", inline=True)
        try:
            await member.send(embed=embed)
        except:
            embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
        await member.ban(reason=f"{reason} // {interaction.user.name}", delete_message_days=delete_message_days)
        return await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description='У вас недостаточно прав для использования команды')
        return await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="Кикнуть участника")
async def context_kick(interaction: discord.Interaction, message: discord.Message):
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
    lastcommand = "`/kick`"
    if interaction.user.guild_permissions.kick_members:
        member_bot: discord.Member
        for temp_member in interaction.guild.members:
            if temp_member.id == bot.user.id:
                member_bot = temp_member
        if interaction.channel.permissions_for(member_bot).manage_messages == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Невозможно использовать контекстное меню т.к. бот не сможет удалять сообщения с содержанием причины! Попросите администраторов выдать это право боту!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if (message.author.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == message.author.id) and interaction.guild.owner.id != interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if message.author.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == message.author.id or member_bot.guild_permissions.kick_members == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на исключение данного участника!\nТип ошибки: `Forbidden`.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(content="Укажите причину выдачи наказания", ephemeral=True)
        def check(m):
            if m.author == interaction.user:
                return True
            return False
        reason = None
        try: 
            reason: discord.Message = await bot.wait_for("message", check=check, timeout=30)
        except TimeoutError:
            return await interaction.edit_original_message(content="Время истекло!")
        else:
            await reason.delete()
            reason = reason.content
        embed = discord.Embed(title=f'Участник выгнан с сервера {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Участник:", value=f"{message.author.mention}", inline=True)
        embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="Причина:", value=f"{reason}", inline=True)
        embed.add_field(name="Доказательства:", value=f"||{message.content}||")
        try:
            await message.author.send(embed=embed)
        except:
            embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
        await message.author.kick(reason=f"{reason} // {interaction.user.name}")
        await interaction.channel.send(embed=embed)
        return await interaction.edit_original_message(content="Наказание успешно выдано!")
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `исключение участников` для использования команды!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="Забанить участника")
async def context_ban(interaction: discord.Interaction, message: discord.Message):
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
    lastcommand = "`/ban`"
    if interaction.user.guild_permissions.ban_members:
        member_bot: discord.Member
        for temp_member in interaction.guild.members:
            if temp_member.id == bot.user.id:
                member_bot = temp_member
        if interaction.channel.permissions_for(member_bot).manage_messages == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Невозможно использовать контекстное меню т.к. бот не сможет удалять сообщения с содержанием причины! Попросите администраторов выдать это право боту!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if (message.author.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == message.author.id) and interaction.guild.owner.id != interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if message.author.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == message.author.id or member_bot.guild_permissions.ban_members == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на бан данного участника!\nТип ошибки: `Forbidden`.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(content="Укажите причину выдачи наказания", ephemeral=True)
        def check(m):
            if m.author == interaction.user:
                return True
            return False
        reason = None
        try: 
            reason: discord.Message = await bot.wait_for("message", check=check, timeout=30)
        except TimeoutError:
            return await interaction.edit_original_message(content="Время истекло!")
        else:
            await reason.delete()
            reason = reason.content
        delete_message_days = None
        await interaction.edit_original_message(content="При желании, укажите, за какой период дней удалить сообщения пользователя (от `0` до `7`)? Укажите `0`, чтобы не удалять сообщения.")
        def check(m):
            if m.author == interaction.user and m.content.isdigit():
                if int(m.content) >= 0 and int(m.content) <= 7:
                    return True
            return False
        try:
            delete_message_days: discord.Message = await bot.wait_for("message", check=check, timeout=30)
        except TimeoutError:
            return await interaction.edit_original_message(content="Время истекло!")
        else:
            await delete_message_days.delete()
            delete_message_days = int(delete_message_days.content)
        embed = discord.Embed(title=f'Участник забанен на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Участник:", value=f"{message.author.mention}", inline=True)
        embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="Причина:", value=f"{reason}", inline=True)
        embed.add_field(name="Доказательства:", value=f"||{message.content}||")
        try:
            await message.author.send(embed=embed)
        except:
            embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
        await message.author.ban(delete_message_days=delete_message_days, reason=f"{reason} // {interaction.user.name}")
        await interaction.channel.send(embed=embed)
        return await interaction.edit_original_message(content="Наказание успешно выдано!")
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `банить участников` для использования команды!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="banoff", description="[Модерация] Банит участника, используя его ID")
@app_commands.describe(member="ID участника, который должен быть забанен", delete_message_days="За какой период удалять сообщения", reason="Причина бана")
async def banoff(interaction: discord.Interaction, member: str, reason: str, delete_message_days: app_commands.Range[int, 0, 7] = 0):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/banoff`'
    if interaction.user.guild_permissions.ban_members:
        if member.isdigit():
            for memb in interaction.guild.members:
                if memb.id == int(member):
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя использовать `/banoff`, если участник находится на сервере! Используйте `/ban`!")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
            member = discord.Object(id=int(member))
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Указанное значение не является чьим-то ID.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            await interaction.guild.ban(member, delete_message_days=delete_message_days, reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
        except Forbidden:
            embed = discord.Embed(title='Ошибка!', color=discord.Color.red(), description=f"Не удалось забанить участника. Проверьте наличия права `банить участников` у бота.\nТип ошибки: `Forbidden`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except NotFound:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Участник не был обнаружен! Удостоверьтесь в правильности ID!\nТип ошибки: `NotFound`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title='Участник забанен на сервере!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
            embed.add_field(name="Участник:", value=f"<@!{member.id}>", inline=True)
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)
            return await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description='У вас недостаточно прав для использования команды')
        return await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="unban", description="[Модерация] Разбанить участника на сервере")
@app_commands.describe(member="ID участника, который должен быть разбанен", reason="Причина разбана")
async def unban(interaction: discord.Interaction, member: str, reason: str):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/unban`'
    if interaction.user.guild_permissions.ban_members:
        if member.isdigit():
            member = discord.Object(id=int(member))
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Указанное значение не является чьим-то ID.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            await interaction.guild.unban(member, reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
        except Forbidden:
            embed = discord.Embed(title='Ошибка!', color=discord.Color.red(), description=f"Не удалось разбанить участника. Проверьте наличия права `банить участников` у бота.\nТип ошибки: `Forbidden`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except NotFound:
            embed = discord.Embed(title="Ошиюка!", color=discord.Color.red(), description=f"Данный участник не обнаружен в списке забаненных!\nТип ошибки: `NotFound`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Участник разбанен!", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            embed.add_field(name="Участник:", value=f"<@!{member.id}>")
            embed.add_field(name="Модератор:", value=interaction.user.mention)
            embed.add_field(name="Причина:", value=reason)
            return await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас недостаточно прав для использования команды")
        return await interaction.response.send_message(embed=embed)


@bot.tree.command(name="clear", description="[Модерация] Очистка сообщений")
@app_commands.describe(radius='Радиус, в котором будут очищаться сообщения.', member="Участник, чьи сообщения будут очищены.")
async def clear(interaction: discord.Interaction, radius: app_commands.Range[int, 1, 1000], member: discord.Member = None):
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
    lastcommand = "`/clear`"
    if interaction.channel.permissions_for(interaction.user).manage_messages:
        deleted = None
        def check(m):
            return True
        if member != None:
            def check(m):
                return m.author.id == member.id
        trying = discord.Embed(title="В процессе...", color=discord.Color.gold(), description="Сообщения очищаются, ожидайте...", timestamp=discord.utils.utcnow())
        trying.set_footer(text=f"{interaction.user.name}#{interaction.user.discriminator}")
        await interaction.response.send_message(embed=trying, ephemeral=True) 
        try:
            deleted = await interaction.channel.purge(limit=radius, check=check)
        except Forbidden:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f'Не удалось очистить `{radius} сообщений`. Возможно, я не имею право на управление сообщениями.\nТип ошибки: `Forbidden`', timestamp=discord.utils.utcnow())
            return await interaction.edit_original_message(embeds=[embed])
        else:
            from_member = '.'
            if member != None:
                from_member = f" от участника {member.mention}."
            embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Мною очищено `{len(deleted)}` сообщений в этом канале{from_member}", timestamp=discord.utils.utcnow())
            return await interaction.edit_original_message(embeds=[embed])
    else:
        embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управление сообщениями` на использование команды!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="clearoff", description="[Модерация] Очистка сообщений от вышедших участников")
@app_commands.describe(radius='Радиус, в котором будут очищаться сообщения.', member="Ник или ID участника, чьи сообщения необходимо удалить.")
async def clearoff(interaction: discord.Interaction, member: str, radius: app_commands.Range[int, 1, 1000]):
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
    lastcommand = "`/clearoff`"
    if interaction.channel.permissions_for(interaction.user).manage_messages:
        deleted = None
        def check(m: discord.Message):
            return str(m.author) == member or m.author.name == member or m.author.id == member
        trying = discord.Embed(title="В процессе...", color=discord.Color.gold(), description="Сообщения очищаются, ожидайте...", timestamp=discord.utils.utcnow())
        trying.set_footer(text=f"{interaction.user.name}#{interaction.user.discriminator}")
        await interaction.response.send_message(embed=trying, ephemeral=True) 
        try:
            deleted = await interaction.channel.purge(limit=radius, check=check)
        except Forbidden:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f'Не удалось очистить `{radius} сообщений`. Возможно, я не имею право на управление сообщениями.\nТип ошибки: `Forbidden`', timestamp=discord.utils.utcnow())
            return await interaction.edit_original_message(embeds=[embed])
        else:
            embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Мною очищено `{len(deleted)}` сообщений в этом канале.", timestamp=discord.utils.utcnow())
            return await interaction.edit_original_message(embeds=[embed])
    else:
        embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управление сообщениями` на использование команды!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="avatar", description="[Полезности] Присылает аватар пользователя")
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
async def avatar(interaction: discord.Interaction, member: discord.Member = None, format: Choice[str] = "png", size: Choice[int] = 2048, type: Choice[str] = 'server'):
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


@bot.tree.command(name="serverinfo", description="[Полезности] Информация о сервере")
async def serverinfo(interaction: discord.Interaction):
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


@bot.tree.command(name="botinfo", description="[Полезности] Информация о боте")
async def botinfo(interaction: discord.Interaction):
    global lastcommand, used_commands
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    members = 0
    for guild in bot.guilds:
        for member in guild.members:
            if not(member.bot):
                members += 1
    embed = discord.Embed(title=bot.user.name, color=discord.Color.orange())
    embed.add_field(name="Версия:", value=curr_version)
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
    embed.add_field(name="Пинг:", value=f"{int(round(bot.latency, 3)*1000)}ms")
    embed.add_field(name="Запущен:", value=f"<t:{started_at}:R>")
    embed.add_field(name="Кол-во серверов:", value=len(bot.guilds))
    embed.add_field(name="Кол-во участников:", value=members)
    owner = await bot.fetch_user(owner_id)
    embed.add_field(name="Разработчик:", value=f"{owner.mention} (ID: 560529834325966858)")
    embed.add_field(name="Ссылки", value=f"[Поддержка]({settings['support_invite']})\n[Добавить на сервер](https://discord.com/oauth2/authorize?client_id={settings['client_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands)")
    embed.add_field(name="Последняя использованная команда:", value=lastcommand)
    embed.add_field(name="Кол-во команд/контекстных меню:", value=f"{len(bot.tree.get_commands(type=discord.AppCommandType.chat_input))}/{len(bot.tree.get_commands(type=discord.AppCommandType.user)) + len(bot.tree.get_commands(type=discord.AppCommandType.message))}")
    embed.add_field(name="Обработано команд:", value=used_commands)
    embed.set_thumbnail(url=bot.user.display_avatar)
    embed.set_footer(text=f"ID бота: {bot.user.id}")
    await interaction.response.send_message(embed=embed)
    lastcommand = "`/botinfo`"
    used_commands += 1


@bot.tree.command(name="slowmode", description="[Модерация] Установить медленный режим в данном канале. Введите 0 для отключения.")
@app_commands.describe(seconds="Кол-во секунд. Укажите 0 для снятия.", reason='Причина установки медленного режима')
async def slowmode(interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600], reason: str = "Отсутствует"):
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
    lastcommand = "`/slowmode`"
    delay = seconds
    if seconds == 0:
        delay = None
    if interaction.channel.permissions_for(interaction.user).manage_channels:
        try:
            await interaction.channel.edit(reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}", slowmode_delay=delay)
        except:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"У бота отсутствует право на управление данным каналом!\nТип ошибки: `Forbidden`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = None
            if seconds>0:
                embed=discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Медленный режим успешно установлен на `{seconds}` секунд.", timestamp=discord.utils.utcnow())
            else:
                embed=discord.Embed(title="Успешно!", color=discord.Color.green(), description="Медленный режим успешно снят.", timestamp=discord.utils.utcnow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управление каналом` для использования этой команды!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="timeout", description="[Модерация] Отправляет участника подумать о своем поведении")
@app_commands.describe(member="Участник, которому нужно выдать тайм-аут", minutes="Кол-во минут, на которые будет выдан тайм-аут.", reason="Причина выдачи наказания.")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: app_commands.Range[int, 0, 40320], reason: str):
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
    lastcommand = "`/timeout`"
    if interaction.user.guild_permissions.moderate_members:
        if (member.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == member.id) and interaction.guild.owner.id != interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        if minutes == 0:
            until = None
        try:
            await member.edit(timed_out_until=until, reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
        except:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось выдать участнику тайм-аут. Убедитесь в наличии прав на управление участниками у бота и попробуйте снова!\nТип ошибки: `Forbidden`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if minutes > 0:    
                embed = discord.Embed(title=f'Участник отправлен в тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Участник:", value=f"{member.mention}",)
                embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                embed.add_field(name="Срок:", value=f"{minutes} минут")
                embed.add_field(name="Причина:", value=reason)
                try:
                    await member.send(embed=embed)
                except:
                    embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                return await interaction.response.send_message(embed=embed)
            if minutes == 0:
                embed = discord.Embed(title=f'С участника снят тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Участник:", value=f"{member.mention}")
                embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                embed.add_field(name="Причина:", value=reason)
                try:
                    await member.send(embed=embed)
                except:
                    embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                return await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управление участниками` для использования команды!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="Выдать тайм-аут")
async def context_timeout(interaction: discord.Interaction, message: discord.Message):
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
    lastcommand = "`/timeout`"
    if interaction.user.guild_permissions.moderate_members:
        member_bot: discord.Member
        for temp_member in interaction.guild.members:
            if temp_member.id == bot.user.id:
                member_bot = temp_member
        if interaction.channel.permissions_for(member_bot).manage_messages == False:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Невозможно использовать контекстное меню т.к. бот не сможет удалять сообщения с содержанием причины и срока наказания! Попросите администраторов выдать это право боту!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if (message.author.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == message.author.id) and interaction.guild.owner.id != interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message("Укажите срок выдачи наказания в минутах в радиусе от нуля до `40320` (только цифры!).", ephemeral=True)
        def check(m: discord.Message):
            if m.author == interaction.user and m.content.isdigit():
                if int(m.content) >= 0 and int(m.content) <= 40320:
                    return True
            return False
        minutes = None
        try: 
            minutes: discord.Message = await bot.wait_for("message", check=check, timeout=30)
        except TimeoutError:
            return await interaction.edit_original_message(content="Время истекло!")
        else:
            await minutes.delete()
            minutes = int(minutes.content)
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await interaction.edit_original_message(content="Теперь укажите причину")
        def check(m):
            if m.author == interaction.user:
                return True
            return False
        reason = None
        try: 
            reason: discord.Message = await bot.wait_for("message", check=check, timeout=30)
        except TimeoutError:
            return await interaction.edit_original_message(content="Время истекло!")
        else:
            await reason.delete()
            reason = reason.content
        if minutes == 0:
            until = None
        try:
            await message.author.edit(timed_out_until=until, reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
        except:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось выдать участнику тайм-аут. Убедитесь в наличии прав на управление участниками у бота и попробуйте снова!\nТип ошибки: `Forbidden`")
            return await interaction.edit_original_message(embed=embed)
        else:
            if minutes > 0:
                proofs = message.content
                if message.attachments != None:
                    for attach in message.attachments:
                        proofs += f'\n{attach.url}'
                embed = discord.Embed(title=f'Участник отправлен в тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Участник:", value=f"{message.author.mention}")
                embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                embed.add_field(name="Срок:", value=f"{minutes} минут")
                embed.add_field(name="Причина:", value=reason)
                embed.add_field(name="Доказательства:", value=f"||{proofs}||")
                try:
                    await message.author.send(embed=embed)
                except:
                    embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                await interaction.channel.send(embed=embed)
                return await interaction.edit_original_message(content="Наказание выдано успешно!")
            if minutes == 0:
                embed = discord.Embed(title=f'С участника снят тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Участник:", value=f"{message.author.mention}")
                embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                embed.add_field(name="Причина:", value=reason)
                try:
                    await message.author.send(embed=embed)
                except:
                    embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                await interaction.channel.send(embed=embed)
                return await interaction.edit_original_message(content="Наказание снято успешно!")
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управление участниками` для использования команды!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command()
async def debug(ctx: commands.Context, argument, *, arg1 = None):
    if ctx.author.id == owner_id:
        if argument == "help":
            message = await ctx.send(f"```\nservers - список серверов бота\nserverid [ID] - узнать о сервере при помощи его ID\nservername [NAME] - узнать о сервере по названию\ncreateinvite [ID] - создать инвайт на сервер\naddblacklist [ID] - добавить в ЧС\nremoveblacklist [ID] - убрать из ЧС\nverify [ID] - выдать галочку\nsupport [ID] - дать значок саппорта\nblacklist - список ЧСников\nleaveserver [ID] - покинуть сервер\nsync - синхронизация команд приложения\nchangename [NAME] - поменять ник бота\nstarttyping [SEC] - начать печатать\nsetavatar [AVA] - поменять аватар\nrestart - перезагрузка\ncreatetemplate - Ctrl+C Ctrl+V сервер```")
            await message.delete(delay=60)
        if argument == "servers":
            servernames = []
            gnames = " "
            for guild in bot.guilds:
                servernames.append(guild.name)
            for name in servernames:
                gnames += f"`{name}`, "
            await ctx.send(f"Servers: {gnames}", delete_after=120)
        if argument == "serverid":
            for guild in bot.guilds:
                if int(arg1) == guild.id:
                    await ctx.send(f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}", delete_after=120)
        if argument == "servername":
            for guild in bot.guilds:
                if str(arg1) == guild.name:
                    await ctx.send(f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}", delete_after=120)
        if argument == "createinvite":
            for guild in bot.guilds:
                if guild.id == int(arg1):
                    for channel in guild.text_channels:
                        invite = await channel.create_invite(max_age=30, reason="Запрос")
                        await ctx.send(invite.url, delete_after=30)
                        return await ctx.message.delete()
        if argument == "addblacklist":
            blacklist.append(int(arg1))
            guild = bot.get_guild(int(arg1))
            if guild != None:
                embed=discord.Embed(title="Ваш сервер занесён в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс ваш сервер в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка: обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
                embed.set_thumbnail(url=guild.icon_url)
                blacklist.append(guild.owner.id)
                try:
                    await guild.owner.send(embed=embed)
                except:
                    pass
                await guild.leave()
            await ctx.message.add_reaction("✅")
            await sleep(30)
            if int(arg1) == owner_id:
                blacklist.remove(int(arg1))
        if argument == "verify":
            verified.append(int(arg1))
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "support":
            supports.append(int(arg1))
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "blacklist":
            await ctx.send(f"Banned: {blacklist}", delete_after=60)
        if argument == "removeblacklist":
            try:
                blacklist.remove(int(arg1))
            except ValueError:
                await ctx.message.add_reaction("❌")
            else:
                await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "leaveserver":
            guild = bot.get_guild(int(arg1))
            await guild.leave()
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "sync":
            async with ctx.channel.typing():    
                await bot.tree.sync()
                await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "changename":
            await bot.user.edit(username=arg1)
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "starttyping":
            await ctx.message.delete()
            async with ctx.channel.typing():
                await sleep(int(arg1))
        if argument == "createtemplate":
            try:
                template = await ctx.guild.create_template(name="Повiстка")
            except:
                template = ctx.guild.templates
                for templ in template:
                    template = templ
                    break
            owner = ctx.guild.get_member(owner_id)
            await owner.send(template.url)
        if argument == "restart":
            await ctx.message.add_reaction("🔁")
            await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Перезагрузка..."))
            await sleep(2)
            os.execv(sys.executable, ['python'] + sys.argv)
        if argument == "setavatar":
            bot_avatar = None
            for attachment in ctx.message.attachments:
                bot_avatar = await attachment.read()
            await bot.user.edit(avatar=bot_avatar)
            await ctx.message.add_reaction("✅")
            await sleep(30)
        if argument == "stop":
            await ctx.message.add_reaction("🔁")
            await bot.close()
    await ctx.message.delete()


@bot.tree.command(name="badgeinfo", description="[Полезности] Информация о значках пользователей и серверов в боте.")
async def badgeinfo(interaction: discord.Interaction):
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


@bot.tree.command(name='outages', description="[Полезности] Показывает актуальные сбои в работе бота.")
async def outages(interaction: discord.Interaction):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/outages`'
    channel = await bot.fetch_channel(settings['outages'])
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


@bot.tree.command(name='clone', description="[Модерация] Клонирует чат.")
@app_commands.describe(delete_original="Удалять ли клонируемый канал?", reason="Причина клонирования")
async def clone(interaction: discord.Interaction, reason: str, delete_original: bool = False):
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
    lastcommand = "`/clone`"
    if interaction.user.guild_permissions.manage_channels:
        cloned = None
        try:
            cloned = await interaction.channel.clone(reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
        except Forbidden:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет право `управление каналами` для совершения действия!\nТип ошибки: `Forbidden`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await cloned.move(after=discord.Object(id=interaction.channel.id), reason=f"Клонирование // {interaction.user.name}#{interaction.user.discriminator}")
            embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Канал успешно клонирован!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            if delete_original == True:
                await sleep(10)
                await interaction.channel.delete(reason=f"Использование команды // {interaction.user.name}#{interaction.user.discriminator}")
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управление каналами` для использования команды.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="resetnick", description="[Модерация] Просит участника поменять ник")
@app_commands.describe(member="Участник, которого надо попросить сменить ник", reason="Причина сброса ника")
async def resetnick(interaction: discord.Interaction, member: discord.Member, reason: str):
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
    lastcommand = "`/resetnick`"
    if interaction.user.guild_permissions.manage_nicknames:
        if member.top_role.position >= interaction.user.top_role.position and interaction.guild.owner.id != interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете управлять никнеймами участников, чья роль выше либо равна вашей!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(title="Не понял", color=discord.Color.red(), description="Нельзя сбросить ник боту.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            await member.edit(nick="Смените ник", reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
        except Forbidden:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"У бота отсутствует право `управлять никнеймами` для совершения действия!\nТип ошибки: `Forbidden`")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=f"Никнейм сброшен на сервере {interaction.guild.name}!", color=discord.Color.red())
            embed.add_field(name="Участник:", value=member.mention)
            embed.add_field(name="Модератор:", value=interaction.user.mention)
            embed.add_field(name="Причина:", value=reason)
            try:
                await member.send(embed=embed)
            except:
                embed.set_footer(text="Участник закрыл доступ к личным сообщениям, поэтому не был оповещён.")
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управлять никнеймами` для использования команды.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="nick", description="[Полезности] Изменяет ваш ник.")
@app_commands.describe(argument="Ник, на который вы хотите поменять. Оставьте пустым для сброса ника")
async def nick(interaction: discord.Interaction, argument: str = None):
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
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=300)
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


@bot.tree.command(name="idea", description="[Полезности] Предложить идею для бота.")
@app_commands.describe(title="Суть идеи", description="Описание идеи", attachment="Изображение для показа идеи")
async def idea(interaction: discord.Interaction, title: str, description: str, attachment: discord.Attachment = None):
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
    channel = bot.get_channel(settings['idea_channel'])
    message = await channel.send(embed=idea_embed)
    await message.add_reaction("✅")
    await message.add_reaction("💤")
    await message.add_reaction("❌")
    embed = discord.Embed(title='Успешно!', color=discord.Color.green(), description="Идея отправлена в канал")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="getemoji", description="[Полезности] Выдает эмодзи картинкой.")
@app_commands.describe(emoji_name="Название, ID либо сам эмодзи.", is_registry="Стоит ли учитывать регистр имени?")
async def getemoji(interaction: discord.Interaction, emoji_name: str, is_registry: bool = False):
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


@bot.tree.command(name="cat", description="[Полезности] Присылает рандомного котика")
async def cat(interaction: discord.Interaction):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/cat`'
    resp = requests.get(f"https://some-random-api.ml/animal/cat?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        embed = discord.Embed(title="Мяу!", color=discord.Color.orange())
        embed.set_image(url=json['image'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось совершить запрос на сервер!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="dog", description="[Полезности] Присылает рандомного пёсика")
async def dog(interaction: discord.Interaction):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/dog`'
    resp = requests.get(f"https://some-random-api.ml/animal/dog?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        embed = discord.Embed(title="Гав!", color=discord.Color.orange())
        embed.set_image(url=json['image'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось совершить запрос на сервер!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="hug", description="[Реакции] Обнять участника")
@app_commands.describe(member="Участник, которого вы хотите обнять")
async def hug(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/hug`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота обнять нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя обнять самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    resp = requests.get(f"https://some-random-api.ml/animu/hug?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        embed = discord.Embed(title="Реакция: обнятие", color=discord.Color.orange(), description=f"{interaction.user.mention} обнял(-а) {member.mention}.")
        embed.set_image(url=json['link'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="Обнять")
async def context_hug(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/hug`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота обнять нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя обнять самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    resp = requests.get(f"https://some-random-api.ml/animu/hug?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        embed = discord.Embed(title="Реакция: обнятие", color=discord.Color.orange(), description=f"{interaction.user.mention} обнял(-а) {member.mention}.")
        embed.set_image(url=json['link'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="pat", description="[Реакции] Погладить участника")
@app_commands.describe(member="Участник, которого вы хотите погладить")
async def pat(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/pat`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота погладить нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя погладить самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    resp = requests.get(f"https://some-random-api.ml/animu/pat?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        embed = discord.Embed(title="Реакция: погладить", color=discord.Color.orange(), description=f"{interaction.user.mention} погладил(-а) {member.mention}.")
        embed.set_image(url=json['link'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="Погладить")
async def context_pat(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/pat`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота погладить нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя погладить самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    resp = requests.get(f"https://some-random-api.ml/animu/pat?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        embed = discord.Embed(title="Реакция: погладить", color=discord.Color.orange(), description=f"{interaction.user.mention} погладил(-а) {member.mention}.")
        embed.set_image(url=json['link'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="wink", description="[Реакции] Подмигнуть. Можно и участнику.")
@app_commands.describe(member="Участник, которому вы хотите подмигнуть.")
async def wink(interaction: discord.Interaction, member: discord.Member = None):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/wink`'
    if member != None:
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но боту подмигнуть нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя подмигнуть самому себе!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    resp = requests.get(f"https://some-random-api.ml/animu/wink?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        description = ''
        if member == None:
            description = f"{interaction.user.mention} подмигнул(-а)."
        else:
            description = f"{interaction.user.mention} подмигнул(-а) {member.mention}."
        embed = discord.Embed(title="Реакция: подмигивание", color=discord.Color.orange(), description=description)
        embed.set_image(url=json['link'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.context_menu(name="Подмигнуть")
async def context_wink(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/wink`'
    if member != None:
        if member.bot:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но боту подмигнуть нельзя")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя подмигнуть самому себе!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    resp = requests.get(f"https://some-random-api.ml/animu/wink?key={key}")
    json = resp.json()
    if resp.status_code == 200:
        embed = discord.Embed(title="Реакция: подмигивание", color=discord.Color.orange(), description=f"{interaction.user.mention} подмигнул(-а) {member.mention}.")
        embed.set_image(url=json['link'])
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось получить картинку!\nКод ошибки: `{resp.status_code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="slap", description="[Реакции] Лупит пользователя.")
@app_commands.describe(member="Участник, которого вы хотите отлупить.")
async def slap(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/slap`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота отлупить нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя отлупить самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    embed = discord.Embed(title="Реакция: шлёп", color=discord.Color.orange(), description=f"{interaction.user.mention} отлупил(-а) {member.mention}.")
    embed.set_image(url=random.choice(slap_gifs))
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="kiss", description="[Реакции] Поцеловать участника")
@app_commands.describe(member="Участник, которого вы хотите поцеловать.")
async def kiss(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/kiss`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота поцеловать нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя поцеловать самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    def check(reaction, user):
        return user == member and reaction.message.author == bot.user and (reaction.emoji == "❌" or reaction.emoji == "✅")
    embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
    await interaction.response.send_message(embed=embed)
    bot_message = await interaction.original_message()
    await bot_message.add_reaction("✅")
    await bot_message.add_reaction("❌")
    try:
        reactions = await bot.wait_for("reaction_add", check=check, timeout=120)
    except TimeoutError:
        embed = discord.Embed(title="Время истекло!", color=discord.Color.red(), description="Участник не ответил на предложение о поцелуе.")
        return await interaction.edit_original_message(embed=embed)
    else:
        if str(reactions).startswith("(<Reaction emoji='❌'"):
            embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
            await bot_message.clear_reactions()
            return await interaction.edit_original_message(embed=embed)
    embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=f"{interaction.user.mention} поцеловал(-а) {member.mention}.")
    embed.set_image(url=random.choice(kiss_gifs))
    await bot_message.clear_reactions()
    await interaction.edit_original_message(embed=embed)


@bot.tree.context_menu(name="Поцеловать")
async def context_kiss(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/kiss`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота поцеловать нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя поцеловать самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    def check(reaction, user):
        return user == member and reaction.message.author == bot.user and (reaction.emoji == "❌" or reaction.emoji == "✅")
    embed = discord.Embed(title="Ожидание...", color=discord.Color.orange(), description=f"{interaction.user.mention}, необходимо получить согласие на поцелуй от {member.mention}\nВремя ограничено!")
    await interaction.response.send_message(embed=embed)
    bot_message = await interaction.original_message()
    await bot_message.add_reaction("✅")
    await bot_message.add_reaction("❌")
    try:
        reactions = await bot.wait_for("reaction_add", check=check, timeout=120)
    except TimeoutError:
        embed = discord.Embed(title="Время истекло!", color=discord.Color.red(), description="Участник не ответил на предложение о поцелуе.")
        return await interaction.edit_original_message(embed=embed)
    else:
        if str(reactions).startswith("(<Reaction emoji='❌'"):
            embed = discord.Embed(title="Отказ!", color=discord.Color.red(), description="Участник отказал вам в поцелуе.")
            await bot_message.clear_reactions()
            return await interaction.edit_original_message(embed=embed)
    embed = discord.Embed(title="Реакция: поцелуй", color=discord.Color.orange(), description=f"{interaction.user.mention} поцеловал(-а) {member.mention}.")
    embed.set_image(url=random.choice(kiss_gifs))
    await bot_message.clear_reactions()
    await interaction.edit_original_message(embed=embed)


@bot.tree.command(name="hit", description="[Реакции] Ударить участника")
@app_commands.describe(member="Участник, которого вы хотите ударить.")
async def hit(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/hit`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота ударить нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя ударить самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    embed = discord.Embed(title="Реакция: удар", color=discord.Color.orange(), description=f"{interaction.user.mention} ударил(-а) {member.mention}.")
    embed.set_image(url=random.choice(hit_gifs))
    await interaction.response.send_message(embed=embed)


@bot.tree.context_menu(name="Ударить")
async def context_hit(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/hit`'
    if member.bot:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Увы, но бота ударить нельзя")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if member.id == interaction.user.id:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя ударить самого себя!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    embed = discord.Embed(title="Реакция: удар", color=discord.Color.orange(), description=f"{interaction.user.mention} ударил(-а) {member.mention}.")
    embed.set_image(url=random.choice(hit_gifs))
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="base64", description="[Полезности] (Де-)кодирует указанный текст в Base64.")
@app_commands.describe(make="Что нужно сделать с текстом?", text="Текст для (де-)кодировки")
@app_commands.choices(make=[
    Choice(name="Кодировать", value="encode"),
    Choice(name="Декодировать", value="decode")
])
async def base64(interaction: discord.Interaction, make: Choice[str], text: str):
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


@bot.tree.command(name="nsfw", description="[NSFW] Присылает NSFW картинку на тематику (бе).")
@app_commands.describe(choice="Тематика NSFW картинки", is_ephemeral="Выберите, будет ли картинка отправлена только вам.")
@app_commands.choices(choice=[
    Choice(name="Ass", value="ass"),
    Choice(name="BDSM", value="bdsm"),
    Choice(name="Cum", value="cum"),
    Choice(name="Creampie", value="creampie"),
    Choice(name="Manga", value="manga"),
    Choice(name="Femdom", value="femdom"),
    Choice(name="Hentai", value="hentai"),
    Choice(name="Public", value="public"),
    Choice(name="Ero", value="ero"),
    Choice(name="Orgy", value="orgy"),
    Choice(name="Yuri", value="yuri"),
    Choice(name="Glasses", value="glasses"),
    Choice(name="Cuckold", value="cuckold"),
    Choice(name="Blowjob", value="blowjob"),
    Choice(name="Boobjob", value="boobjob"),
    Choice(name="Foot", value="foot"),
    Choice(name="Thighs", value="thighs"),
    Choice(name="Vagina", value="pussy"),
    Choice(name="Uniform", value="uniform"),
    Choice(name="Gangbang", value="gangbang"),
    Choice(name="Tentacles", value="tentacles"),
    Choice(name="GIF", value="hnt_gifs"),
    Choice(name="NSFW Neko", value="nsfwNeko")
])
async def nsfw(interaction: discord.Interaction, choice: Choice[str], is_ephemeral: bool = False):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/nsfw`'
    if interaction.channel.is_nsfw():
        embed = discord.Embed(title=choice.name, color=discord.Color.orange())
        embed.set_image(url=useHM(29, choice.value))
        await interaction.response.send_message(embed=embed, ephemeral=is_ephemeral)
    else:
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Данный канал не является NSFW каналом!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="send", description="[Полезности] Отправляет сообщение в канал от имени вебхука")
@app_commands.describe(message="Сообщение, которое будет отправлено")
async def send(interaction: discord.Interaction, message: str):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/send`'
    if interaction.channel.permissions_for(interaction.guild.get_member(bot.user.id)).manage_webhooks == False:
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

@bot.tree.command(name="getaudit", description="[Полезности] Получает информацию о кол-ве модерационных действий пользователя.")
@app_commands.describe(member="Участник, чьё кол-во действий вы хотите увидить")
async def getaudit(interaction: discord.Interaction, member: discord.Member):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/getaudit`'
    if interaction.user.guild_permissions.view_audit_log:
        member_bot = await interaction.guild.fetch_member(bot.user.id)
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


@bot.tree.command(name="math", description="[Развлечения] Реши несложный пример на сложение/вычитание")
async def math_cmd(interaction: discord.Interaction):
    global lastcommand, used_commands
    used_commands += 1
    if interaction.user.id in blacklist:
        embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    lastcommand = '`/math`'
    choice = ['+','-']
    tosolve = f"{random.randint(9,99)} {random.choice(choice)} {random.randint(9,99)}"
    answer = eval(tosolve)
    embed = discord.Embed(title="Реши пример!", color=discord.Color.orange(), description=f"`{tosolve}`")
    embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)
    start = time.time()
    def check(m):
        isint = False
        try:
            temp = int(m.content)
        except:
            isint = False
        else:
            isint = True
        return interaction.user.id == m.author.id and isint
    try:
        ans = await bot.wait_for("message", check=check, timeout=15)
    except TimeoutError:
        embed = discord.Embed(title="Время истекло!", color=discord.Color.red(), description=f"Правильный ответ: `{answer}`.")
        embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
        message = await interaction.original_message()
        await message.reply(embed=embed)
    else:
        if int(ans.content) == int(answer):
            wasted = time.time() - start
            embed = discord.Embed(title="Правильно!", color=discord.Color.green(), description=f"Ответ: `{answer}`. Время ответа: `{round(wasted, 3)}s`.")
            embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            await ans.reply(embed=embed)
        else:
            embed = discord.Embed(title="Неправильно!", color=discord.Color.red(), description=f"Правильный ответ: `{answer}`")
            embed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            await ans.reply(embed=embed)


print("Подключение к Discord...")
bot.run(settings['token'])
