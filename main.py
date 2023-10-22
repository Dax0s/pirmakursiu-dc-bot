import discord
from dotenv import load_dotenv
import os
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv('TOKEN')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send(f'Sw {message.author} pahsol naxui dalbajobe')



bot.run(TOKEN)
