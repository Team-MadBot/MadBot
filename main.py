from config import settings
from tools import models

bot = models.MadBot()

bot.run(settings['token'], root_logger=True) # type: ignore
