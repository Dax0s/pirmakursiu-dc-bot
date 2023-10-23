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

GUILD_ID = 1165580717204439121

SUBMISSIONS_CHANNEL_ID = 1165583893324382218
VOTING_CHANNEL_ID = 1165583928954978424

SUBMISSIONS_CHANNEL_ID_ISTORIJOS = 1166033643752407111
VOTING_CHANNEL_ID_ISTORIJOS = 1166033690158182470

IT_ROLE_ID = 1166056850899337259

no_reaction = False

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()


# fotkes
@bot.event
async def on_message(msg):

    global no_reaction
    if no_reaction:
        no_reaction = False
        return

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
    
    attachment_count = len(msg.attachments)

    # fotkes
    if msg.channel.id == SUBMISSIONS_CHANNEL_ID:
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
        # if more than one attachment
        if attachment_count > 0:
            await msg.author.send("Only plain text stowies allowed")
            await msg.delete()
            return
        elif msg.content.startswith("http"):
            await msg.author.send("No links alowed")
            await msg.delete()
            return

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


    if not (reaction == "👍" or reaction == "💀") and (channel_id == VOTING_CHANNEL_ID or channel_id == VOTING_CHANNEL_ID_ISTORIJOS):
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.remove_reaction(payload.emoji, discord.Object(user_id))

    if payload.event_type == "REACTION_ADD" and (channel_id == VOTING_CHANNEL_ID or channel_id == VOTING_CHANNEL_ID_ISTORIJOS):
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

    if user_id == bot.user.id and (channel_id != VOTING_CHANNEL_ID or channel_id != VOTING_CHANNEL_ID_ISTORIJOS):
        return
   
    if payload.event_type == "REACTION_REMOVE" and (channel_id == VOTING_CHANNEL_ID or channel_id == VOTING_CHANNEL_ID_ISTORIJOS):
        if user_reactions.get(user_id, None) is not None:
            user_message_reactions = user_reactions[user_id]
            if user_message_reactions.get(message_id, None) is not None:
                user_message_reactions[message_id] -= 1

@bot.tree.command(name = "count", description = "pisi uzpisai davai ['winners', 'losers']")
async def count(interaction: discord.Interaction, nezinom_kaip_pavadinti: str):

    global no_reaction
    if str(IT_ROLE_ID) not in str(interaction.user.roles):
        no_reaction = True
        await interaction.response.send_message("You need to the the IT role to be able to use this command", ephemeral = True)
        return

    if interaction.channel_id in [VOTING_CHANNEL_ID, VOTING_CHANNEL_ID_ISTORIJOS]:
        msgs = []

        if nezinom_kaip_pavadinti not in ["winners", "losers"]:
            no_reaction = True
            await interaction.response.send_message("Xuj cia pezi", ephemeral = True)
            return
        
        async for msg in interaction.channel.history():
            if (len(msg.reactions) == 2):
                msgs.append(msg)

        def sort_by_like(e):
            return e.reactions[0].count

        def sort_by_skull(e):
            return e.reactions[1].count
        
        index = 0
        emoji = ''
        
        if nezinom_kaip_pavadinti == "winners":
            msgs.sort(reverse = True, key = sort_by_like)
            index = 0
            emoji = '👍'
        else:
            msgs.sort(reverse = True, key = sort_by_skull)
            index = 1
            emoji = '💀'

            

        winner_list = ''
        current_winner = 1
        for msg in msgs:
            if current_winner > 10:
                break

            winner_list += f"{current_winner}. https://discord.com/channels/{GUILD_ID}/{interaction.channel_id}/{msg.id}  {msg.reactions[index].count} {emoji}\n"

            current_winner += 1

        embed=discord.Embed(title = nezinom_kaip_pavadinti.capitalize(),
                            description = winner_list,
                            color = 0xFF5733)


        
        no_reaction = True
        await interaction.response.send_message(embed = embed)
        # await interaction.response.send_message("@Dax0s")

    else:
        await interaction.response.send_message("this only works in voting channels!")
    

bot.run(TOKEN)
