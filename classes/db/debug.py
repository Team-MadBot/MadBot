from . import client


async def ping_db():
    await client.admin.command("ping")