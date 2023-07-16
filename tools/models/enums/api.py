from typing import (
    Literal, 
    Final
)

NC_CATEGORIES: Final = Literal[
    'baka', 
    'cry', 
    'cuddle', 
    'happy', 
    'hug', 
    'kiss', 
    'sad', 
    'wag', 
    'poke', 
    'pat', 
    'dance', 
    'smug', 
    'wave', 
    'menhera-chan'
]
SDC_URL: Final[str] = "https://api.server-discord.com/v2/bots/{bot_id}/stats"
