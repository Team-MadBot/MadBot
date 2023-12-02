import logging

logger = logging.getLogger('discord')

logger.info

def cog_load(self):
        logging.getLogger("discord").addHandler(RotatingFileHandler(
            filename="discord.log",
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,
            backupCount=10,
        ))
        self.logger = logging.getLogger("discord")
    
def cog_unload(self):
    self.logger.removeHandler(self.logger.handlers[-1])
