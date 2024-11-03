import asyncio
import os
import disnake

from disnake.ext import commands

from src.db.engine import db_init
from src.store.config import DiscordConfig


intents = disnake.Intents.all()

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("."),
    intents=intents, owner_id=DiscordConfig.OWNER,

)


path_cogs = "src/bot/cogs"
for file in os.listdir(path_cogs):
    if file[-3:] == ".py":
        module_path = path_cogs.replace("/", ".") + "." + file[0:-3]
        bot.load_extension(module_path)


asyncio.run(db_init())

bot.run(DiscordConfig.TOKEN)
