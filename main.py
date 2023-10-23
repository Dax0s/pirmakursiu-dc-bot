import discord
from discord import app_commands
from dotenv import load_dotenv
from discord.utils import get
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

TOKEN = os.getenv('TOKEN')

SUBMISSIONS_CHANNEL_ID = 1165583893324382218
VOTING_CHANNEL_ID = 1165583928954978424

SUBMISSIONS_CHANNEL_ID_ISTORIJOS = 1166033643752407111
VOTING_CHANNEL_ID_ISTORIJOS = 1166033690158182470


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()


# fotkes
@bot.event
async def on_message(msg):

    if msg.content.startswith('$hello'):
        await msg.channel.send(f'Sw {msg.author} pashol naxui dalbajobe')

    if msg.author == bot.user:
        if msg.channel.id == VOTING_CHANNEL_ID or msg.channel.id == VOTING_CHANNEL_ID_ISTORIJOS:
            await msg.add_reaction("👍")
            await msg.add_reaction("💀")
        else:
            return
    
    voting_channel = bot.get_channel(VOTING_CHANNEL_ID)
    voting_channel_istorijos = bot.get_channel(VOTING_CHANNEL_ID_ISTORIJOS)
    

    # fotkes
    if msg.channel.id == SUBMISSIONS_CHANNEL_ID:
        attachment_count = len(msg.attachments)

        # if more than one attachment
        if attachment_count > 1:
            await msg.author.send("Only one attachment is allowed")
            await msg.delete()
            return
    
        # if its not an image
        if attachment_count == 0:
            await msg.author.send("Please send an image. Not a text message!")
            await msg.delete()
            return

        print(msg.attachments)

        full_filename = msg.attachments[0].filename
        file_extension = full_filename.split('.')[1]

        allowed_extensions = ["apng", "avif", "gif", "jpeg", "jpg", "png", "svg", "webp", "bmp", "ico", "tiff"]
        user = msg.author
        if file_extension.lower() in allowed_extensions:
            
            embed=discord.Embed(title="Photo Submission",
                                description=f"Uploaded by: {user.mention}",
                                color=0xFF5733)
            embed.set_image(url=msg.attachments[0])
            await voting_channel.send(embed = embed)
            await msg.author.send("Photo uploaded successfully")
        else:
            await msg.author.send(f"Allowed extensions: {allowed_extensions}\nNote: iphone RAW photos (chujnia) aren't allowed")
        
        await msg.delete()

    # istorijos
    if msg.channel.id == SUBMISSIONS_CHANNEL_ID_ISTORIJOS:
        user = msg.author
        embed=discord.Embed(title="Short scawy story",
                                description=f"Uploaded by: {user.mention}",
                                color=0xFF5733)
        embed.add_field(name="Story", value = msg.content, inline=False)
        await voting_channel_istorijos.send(embed = embed)
        await msg.delete()




user_reactions = {}

@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    user_id = payload.user_id
    channel_id = payload.channel_id
    reaction = str(payload.emoji)

    if user_id == bot.user.id:
        return


    if not (reaction == "👍" or reaction == "💀") and channel_id == VOTING_CHANNEL_ID:
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.remove_reaction(payload.emoji, discord.Object(user_id))

    if payload.event_type == "REACTION_ADD" and channel_id == VOTING_CHANNEL_ID:
        if user_reactions.get(user_id, None) is None:
            user_reactions[user_id] = {}

        user_message_reactions = user_reactions[user_id]
        if user_message_reactions.get(message_id, None) is None:
            user_message_reactions[message_id] = 1
        else:
            user_message_reactions[message_id] += 1

        if user_message_reactions[message_id] == 2:
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



@bot.tree.command(name = "count", description = "pisi uzpisai davai")
async def count(interaction: discord.Interaction):

    if interaction.channel_id == VOTING_CHANNEL_ID:
        msgs = []
        
        async for msg in interaction.channel.history():
            if (len(msg.reactions) == 2):
                msgs.append(msg)

        def sort_by_like(e):
            return e.reactions[0].count

        def sort_by_skull(e):
            return e.reactions[1].count

        
        msgs.sort(reverse=True,key=sort_by_like)
        for msg in msgs:
                        
            print(msg.reactions)

        print('\n-------------------------\n')

        msgs.sort(reverse=True,key=sort_by_skull)
        for msg in msgs:
            print(msg.reactions)


        embed=discord.Embed(title="Sample Embed", description="This is an embed that will show how to build an embed and the different components", color=0xFF5733)
        await interaction.response.send_message(embed=embed)

        print(msgs[0])



    else:
        print("this only works in voting channel!")
    

bot.run(TOKEN)
