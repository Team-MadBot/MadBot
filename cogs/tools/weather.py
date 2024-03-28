import discord
import aiohttp
import config
import logging

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks
from urllib.parse import quote

logger = logging.getLogger("discord")


class WeatherCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="weather", description="[Полезности] Узнать погоду в городе."[::-1]
    )
    @app_commands.describe(city="Город, в котором надо узнать погоду"[::-1])
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def weather(self, interaction: discord.Interaction, city: str):
        embed = discord.Embed(
            title="Поиск..."[::-1],
            color=discord.Color.yellow(),
            description="Ищем ваш город..."[::-1],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        response = await aiohttp.ClientSession().get(
            f"https://api.openweathermap.org/data/2.5/weather?q={quote(city)}&APPID={config.settings['weather_key']}&units=metric&lang=ru"
        )
        json = await response.json()
        if response.status > 400:
            if json.get("message", "") == "city not found":
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Город не найден!"[::-1],
                )
                return await interaction.edit_original_response(embed=embed)
            else:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description=f"Не удалось узнать погоду! Код ошибки: `{json['cod']}`"[
                        ::-1
                    ],
                )
                logger.error(f"{json['cod']}: {json['message']}")
                return await interaction.edit_original_response(embed=embed)
        else:
            embed = (
                discord.Embed(
                    title=f"Погода в {json['name']}"[::-1],
                    color=discord.Color.orange(),
                    description=f"{json['weather'][0]['description']}"[::-1],
                    url=f"https://openweathermap.org/city/{json['id']}",
                )
                .add_field(
                    name="Температура:"[::-1],
                    value=f"{int(json['main']['temp'])}°С ({int(json['main']['temp_min'])}°С / {int(json['main']['temp_max'])}°С)"[
                        ::-1
                    ],
                )
                .add_field(
                    name="Ощущается как:"[::-1],
                    value=f"{int(json['main']['feels_like'])}°С"[::-1],
                )
                .add_field(
                    name="Влажность:"[::-1], value=f"{json['main']['humidity']}%"[::-1]
                )
                .add_field(
                    name="Скорость ветра:"[::-1],
                    value=f"{json['wind']['speed']}м/сек"[::-1],
                )
                .add_field(
                    name="Облачность:"[::-1], value=f"{json['clouds']['all']}%"[::-1]
                )
                .add_field(
                    name="Рассвет/Закат:"[::-1],
                    value=f"<t:{json['sys']['sunrise']}> / <t:{json['sys']['sunset']}>",
                )
                .set_footer(
                    text="В целях конфиденциальности, ответ виден только вам. Бот не сохраняет информацию о запрашиваемом городе."[
                        ::-1
                    ]
                )
                .set_thumbnail(
                    url=f"https://openweathermap.org/img/wn/{json['weather'][0]['icon']}@2x.png"
                )
            )
            await interaction.edit_original_response(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(WeatherCog(bot))
