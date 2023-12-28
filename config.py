import time
import os

from dotenv import load_dotenv

from typing import TypedDict

load_dotenv()

class __Settings(TypedDict):
    min_members: int
    debug_mode: bool
    token: str
    app_id: int
    weather_key: str
    sdc_key: str
    support_invite: str
    owner_id: int
    supp_guild: int
    comm_guild: int
    log_channel: int
    report_channel: int
    debug_channel: int
    perm_scope: int
    outages: int
    prem_user: int
    prem_server: int
    bc_api_ver: int
    bc_hook_url: str
    shard_log_hook_url: str
    vote_hook_url: str
    bcv2_token: str
    unbelieva_token: str
    risticks_token: str
    curr_version: str
    mongo_url: str
    catapi_key: str | None
    dogapi_key: str | None

settings: __Settings = {
    'min_members': 10,
    'debug_mode': False,
    'token': os.environ.get("TOKEN"),
    'app_id': int(os.environ.get("APP_ID")), # type: ignore
    'weather_key': os.environ.get("WEATHER_TOKEN"),
    'sdc_key': os.environ.get("SDC_TOKEN"),
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
    'curr_version': os.environ.get("CURRENT_VERSION"),
    'mongo_url': os.environ.get("MONGO_URL"),
    'catapi_key': os.environ.get("CATAPI_KEY"),
    'dogapi_key': os.environ.get("DOGAPI_KEY")
}

started_at = int( # Время запуска бота. Не изменять.
    time.time()
)

cogs_ignore = [ # список игнорируемых (?) cog'ов.
   
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
