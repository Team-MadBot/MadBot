import discord
import time
import os

from dotenv import load_dotenv

load_dotenv()

settings = {
    'min_members': 10,
    'token': os.environ.get("TOKEN"),
    'app_id': int(os.environ.get("APP_ID")), # type: ignore
    'key': os.environ.get("SRA_TOKEN"),
    'weather_key': os.environ.get("WEATHER_TOKEN"),
    'sdc_key': os.environ.get("SDC_TOKEN"),
    'nc_token': os.environ.get("NC_TOKEN"),
    'support_invite': os.environ.get("SUPPORT_INVITE_URL"),
    'owner_id': int(os.environ.get("OWNER_ID")), # type: ignore
    'supp_guild': int(os.environ.get("SUPPORT_GUILD_ID")), # type: ignore
    'comm_guild': int(os.environ.get("COMMUNITY_GUILD_ID")), # type: ignore
    'log_channel': int(os.environ.get("LOG_CHANNEL_ID")), # type: ignore
    'report_channel': int(os.environ.get("REPORT_CHANNEL_ID")), # type: ignore
    'debug_channel': int(os.environ.get("DEBUG_CHANNEL_ID")), # type: ignore
    'perm_scope': int(os.environ.get("PERM_SCOPE")), # type: ignore
    'outages': int(os.environ.get("OUTAGES_CHANNEL_ID")), # type: ignore
    'prem_user': int(os.environ.get("PREMIUM_USER_ROLE_ID")), # type: ignore
    'prem_server': int(os.environ.get("PREMIUM_SERVER_ROLE_ID")), # type: ignore
    'bc_api_ver': int(os.environ.get("BC_API_VER")), # type: ignore
    'bc_hook_url': os.environ.get("BC_WEBHOOK_URL"),
    'shard_log_hook_url': os.environ.get("SHARD_LOG_WEBHOOK_URL"),
    'vote_hook_url': os.environ.get("VOTE_WEBHOOK_URL"),
    'bcv2_token': os.environ.get("BC_TOKEN"),
    'unbelieva_token': os.environ.get("UNBELIEVA_TOKEN"),
    'risticks_token': os.environ.get("RISTICKS_TOKEN"),
    'curr_version': os.environ.get("CURRENT_VERSION")
}

started_at = int( # Время запуска бота. Не изменять.
    time.time()
)

cogs_ignore = [ # список игнорируемовых (?) cog'ов.
   
]

blacklist = [ # done
    670322143543951367,
    823593030253674496,
    992539399927640124,
    986989653229994004,
    895027718842884106,
    1019612041083883541,
    1036216648090275860,
    1028223525049348106,
    1082919094837334057
]
supports = [
    560529834325966858,
    754719910256574646,
    777140702747426817,
    615938723535912970
]
verified = [
    560529834325966858,
    903661712903921715,
    942667891701071892,
    754719910256574646,
    880911386916577281,
    958427702879215697,
    914181806285279232,
    981247575451639888,
    777140702747426817
]
beta_testers = [
    914181806285279232,
    796449686986424340,
    942667891701071892,
    721118036807123094
]
bug_hunters = [
    560529834325966858,
    754719910256574646
]
bug_terminators = [
    560529834325966858,
    754719910256574646
]
coders = [ # Помощники разработчика.
    560529834325966858
]

slap_gifs = [ # Гифки шлёпа.
    "https://cdn.discordapp.com/attachments/707201738255368194/847553281852702770/tenor_1.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847553382339182642/tenor_2.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847553413319098418/tenor_3.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847553484949553202/tenor_4.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847553521683529758/tenor_5.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847553545632612443/tenor_6.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847553662780047421/tenor_12.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847554139943731250/tenor_23.gif",
    "https://cdn.discordapp.com/attachments/707201738255368194/847554219648352266/tenor_24.gif"
]
kiss_gifs = [ # Гифки поцелуя.
    "https://i.imgur.com/a66k9c7.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967834319160750111/animesher.com_kiss-anime-love-tender-kiss-766612.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967834665568305162/d0cd64030f383d56e7edc54a484d4b8d.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967834666021310534/giphy.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967834666277175296/kiss-anime.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967834666709164123/tumblr_0cd93127b3eee8352ca2a5a66349bcdb_0d2f4ba2_500.gif"
]
hit_gifs = [ # Гифки удара.
    "https://cdn.discordapp.com/attachments/956616897363869796/967842754828861470/2ce5a017f6556ff103bce87b273b89b7.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967842755147624468/anime.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967842755697049600/anime-hit.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967842755978100786/animesher.com_hitting-toradora-funny-1701058.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967842756288475277/head-hit-anime.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967842756590444624/hit.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967842756875673710/hit-anime.gif",
    "https://cdn.discordapp.com/attachments/956616897363869796/967842757148278864/hit-head-anime.gif"
]
