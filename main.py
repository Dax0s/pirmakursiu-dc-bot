import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.members = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# tree = app_commands.CommandTree(bot)

TOKEN = os.getenv('TOKEN')

SUBMISSIONS_CHANNEL_ID = 1165583893324382218
VOTING_CHANNEL_ID = 1165583928954978424

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send(f'Sw {message.author} pahsol naxui dalbajobe')

@bot.event
async def on_message(msg):

    if msg.author == bot.user:
        if msg.channel.id == VOTING_CHANNEL_ID:
            await msg.add_reaction("👍")
        else:
            await msg.add_reaction("💀")
        return
    
    voting_channel = bot.get_channel(VOTING_CHANNEL_ID)

    # if message is sent to submissions channel
    if msg.channel.id == SUBMISSIONS_CHANNEL_ID:
        attachment_count = len(msg.attachments)

        if attachment_count > 1:
            await msg.author.send("Only one attachment is allowed")
            await msg.delete()
            return
    
        if attachment_count == 0:
            await msg.author.send("Please send an image. Not a text message!")
            await msg.delete()
            return

        print(msg.attachments)

        full_filename = msg.attachments[0].filename
        file_extension = full_filename.split('.')[1]

        allowed_extensions = ["apng", "avif", "gif", "jpeg", "jpg", "png", "svg", "webp", "bmp", "ico", "tiff"]

        if file_extension.lower() in allowed_extensions:
            await voting_channel.send(msg.attachments[0])
            await msg.author.send("photo uploaded successfully")
        else:
            await msg.author.send(f"Allowed extensions: {allowed_extensions}\nNote: iphone RAW photos (chujnia) aren't allowed")
        
        await msg.delete()



user_reactions = {}

@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    user_id = payload.user_id
    channel_id = payload.channel_id

    if user_id == bot.user.id and channel_id != VOTING_CHANNEL_ID:
        return

    if payload.event_type == "REACTION_ADD" and channel_id == VOTING_CHANNEL_ID:
        if user_reactions.get(user_id, None) is None:
            user_reactions[user_id] = {}

        user_message_reactions = user_reactions[user_id]
        if user_message_reactions.get(message_id, None) is None:
            user_message_reactions[message_id] = 1
        else:
            user_message_reactions[message_id] += 1

        if user_message_reactions[message_id] == 2:
            channel_id = payload.channel_id
            channel = bot.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            await message.remove_reaction(payload.emoji, discord.Object(user_id))
            print("istrinta naxui durneli tu")

@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    user_id = payload.user_id
    channel_id = payload.channel_id

    if user_id == bot.user.id and channel_id != VOTING_CHANNEL_ID:
        return
   
    if payload.event_type == "REACTION_REMOVE" and channel_id == VOTING_CHANNEL_ID:
        if user_reactions.get(user_id, None) is not None:
            user_message_reactions = user_reactions[user_id]
            if user_message_reactions.get(message_id, None) is not None:
                user_message_reactions[message_id] -= 1

                # Check if the user removed their first reaction
                if user_message_reactions[message_id] == 0:
                    channel_id = payload.channel_id
                    channel = bot.get_channel(channel_id)
                    message = await channel.fetch_message(message_id)
                    
                    # You can add your custom logic here to respond to the removal of the first reaction
                    print(f"{bot.get_user(user_id)} removed their first reaction from the message!")

bot.run(TOKEN)
