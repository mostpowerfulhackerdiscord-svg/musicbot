import discord
from discord.ext import commands
from Handlers.Handler import BotHandler
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = None
USER_IDS = {}
env_path = "Modules/passes/secretpass.env"

with open(env_path, "r", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if line.startswith("DISCORD_TOKEN="):
            DISCORD_TOKEN = line.split("=", 1)[1].strip()
        elif line.startswith("USER_ID"):
            key, value = line.split("=", 1)
            USER_IDS[key] = value.strip()

@bot.event
async def on_ready():
    BotHandler.register(bot)
    await bot.tree.sync()
    print(f"Bot logged in as {bot.user}")

bot.run(DISCORD_TOKEN)
