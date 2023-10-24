import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import logging

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.members = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv('TOKEN')

### IDs
GUILD_ID = 1166408845342552115

SUBMISSIONS_CHANNEL_ID_OUTFITS = 1166409538824581120
VOTING_CHANNEL_ID_OUTFITS = 1166409591379202159

SUBMISSIONS_CHANNEL_ID_STORIES = 1166409184762409032
VOTING_CHANNEL_ID_STORIES = 1166409434621300776

IT_ROLE_ID = 1166408994710097950

EVERYONE_ROLE_ID = 1166408845342552115
###

no_reaction = False

GOOD_REACTION = "👍"
BAD_REACTION = "💀"

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

all_photos_messages = {}
all_stories_messages = {}


@bot.event
async def on_ready():
    global all_photos_messages
    global all_stories_messages

    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

    voting_channel_photos = bot.get_channel(VOTING_CHANNEL_ID_OUTFITS)
    voting_channel_stories = bot.get_channel(VOTING_CHANNEL_ID_STORIES)

    submission_channel_photos = bot.get_channel(SUBMISSIONS_CHANNEL_ID_OUTFITS)
    submission_channel_stories = bot.get_channel(SUBMISSIONS_CHANNEL_ID_STORIES)
    everyone_role = bot.get_guild(GUILD_ID).get_role(EVERYONE_ROLE_ID)

    await submission_channel_photos.set_permissions(everyone_role, send_messages=False)
    await submission_channel_stories.set_permissions(everyone_role, send_messages=False)

    await voting_channel_photos.set_permissions(everyone_role, read_messages=False)
    await voting_channel_stories.set_permissions(everyone_role, read_messages=False)
    await submission_channel_photos.send("Bot loading...")
    await submission_channel_stories.send("Bot loading...")

    msgs = [msg async for msg in voting_channel_photos.history(limit=1000)]
    logging.info("Messages in photos fetched")
    for msg in msgs:
        if len(msg.reactions) == 2:
            all_photos_messages[msg.id] = {"good_reactions": [], "bad_reactions": []}

            users = [user async for user in msg.reactions[0].users(limit=1000)]
            logging.info("users fetched")
            for user in users:
                all_photos_messages[msg.id]['good_reactions'].append(user.id)

            users = [user async for user in msg.reactions[1].users(limit=1000)]
            logging.info("users fetched")
            for user in users:
                all_photos_messages[msg.id]['bad_reactions'].append(user.id)

    msgs = [msg async for msg in voting_channel_stories.history(limit=1000)]
    logging.info("Messages in stories fetched")
    for msg in msgs:
        if len(msg.reactions) == 2:
            all_stories_messages[msg.id] = {"good_reactions": [], "bad_reactions": []}

            users = [user async for user in msg.reactions[0].users(limit=1000)]
            logging.info("users fetched")
            for user in users:
                all_stories_messages[msg.id]['good_reactions'].append(user.id)

            users = [user async for user in msg.reactions[1].users(limit=1000)]
            logging.info("users fetched")
            for user in users:
                all_stories_messages[msg.id]['bad_reactions'].append(user.id)

    logging.info("Reactions fetched")
    # await submission_channel_photos.purge()
    # await submission_channel_stories.purge()

    await submission_channel_photos.set_permissions(everyone_role, send_messages=True)
    await submission_channel_stories.set_permissions(everyone_role, send_messages=True)

    await voting_channel_photos.set_permissions(everyone_role, read_messages=True)
    await voting_channel_stories.set_permissions(everyone_role, read_messages=True)


user_submissions_costume = {}
user_submissions_story = {}


# fotkes
@bot.event
async def on_message(msg):
    global no_reaction
    if no_reaction:
        no_reaction = False
        return

    if msg.content.startswith('$hello'):
        await msg.author.send(f'Sw {msg.author} pashol naxui dalbajobe')

    if msg.author == bot.user:
        if msg.channel.id == VOTING_CHANNEL_ID_OUTFITS or msg.channel.id == VOTING_CHANNEL_ID_STORIES:
            await msg.add_reaction("👍")
            await msg.add_reaction("💀")
            logging.info(f"2req. Reactions to message added. Message: {msg.content}")
        else:
            return

    if msg.channel.id == VOTING_CHANNEL_ID_OUTFITS:
        all_photos_messages[msg.id] = {"good_reactions": [], "bad_reactions": []}

    if msg.channel.id == VOTING_CHANNEL_ID_STORIES:
        all_stories_messages[msg.id] = {"good_reactions": [], "bad_reactions": []}

    voting_channel = bot.get_channel(VOTING_CHANNEL_ID_OUTFITS)
    voting_channel_istorijos = bot.get_channel(VOTING_CHANNEL_ID_STORIES)

    attachment_count = len(msg.attachments)

    # fotkes
    if msg.channel.id == SUBMISSIONS_CHANNEL_ID_OUTFITS:
        # if more than one attachment
        if attachment_count > 1:
            await msg.author.send("Only one attachment is allowed")
            await msg.delete()
            logging.warning(f"2req. Too many attachments added to photo contest. User: {msg.author}")
            return

        # if its not an image
        if attachment_count == 0:
            await msg.author.send("Please send an image. Not a text message!")
            await msg.delete()
            logging.warning(f"2req. No attachments added to photo contest. User: {msg.author}")
            return

        full_filename = msg.attachments[0].filename
        file_extension = full_filename.split('.')[1]

        allowed_extensions = ["apng", "avif", "gif", "jpeg", "jpg", "png", "svg", "webp", "bmp", "ico", "tiff"]
        user = msg.author
        if file_extension.lower() in allowed_extensions:

            embed = discord.Embed(title="Photo Submission",
                                  description=f"Uploaded by: {user.mention}",
                                  color=0xFF5733)
            embed.set_image(url=msg.attachments[0])
            await voting_channel.send(embed=embed)
            logging.info(f"1req. Photo submission uploaded. User: {msg.author}")
            await msg.author.send("Photo uploaded successfully")
            logging.info(f"1req. Successful photo upload DM sent. User: {msg.author}")
        else:
            await msg.author.send(
                f"Allowed extensions: {allowed_extensions}\nNote: iphone RAW (ProRes) photos (chujnia) aren't allowed")
            logging.warning(f"1req. Extension not allowed. User: {msg.author}")

        await msg.delete()
        logging.info("1req. Message deleted")

    # istorijos
    if msg.channel.id == SUBMISSIONS_CHANNEL_ID_STORIES:
        # if more than one attachment
        if attachment_count > 0:
            await msg.author.send("Only plain text stowies allowed")
            await msg.delete()
            logging.warning(f"2req. File sent to story submissions. User: {msg.author}")
            return
        elif msg.content.startswith("http"):
            await msg.author.send("No links alowed")
            await msg.delete()
            logging.warning(f"2req. Link sent to story submissions. User: {msg.author}")
            return

        user = msg.author
        embed = discord.Embed(title="Short scawy story",
                              description=f"Uploaded by: {user.mention}",
                              color=0xFF5733)
        embed.add_field(name="Story", value=msg.content, inline=False)
        await voting_channel_istorijos.send(embed=embed)
        await msg.author.send("Story uploaded!")
        await msg.delete()
        logging.info(f"3req. Story uploaded. User: {msg.author}")


user_reactions = {}


@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    user_id = payload.user_id
    channel_id = payload.channel_id
    reaction = str(payload.emoji)

    if user_id == bot.user.id:
        return

    if not (reaction == "👍" or reaction == "💀") and (
            channel_id == VOTING_CHANNEL_ID_OUTFITS or channel_id == VOTING_CHANNEL_ID_STORIES):
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.remove_reaction(payload.emoji, discord.Object(user_id))
        logging.warning(f"2req. Incorrect reaction added. User: {user_id}")
        return

    if channel_id == VOTING_CHANNEL_ID_OUTFITS:
        if reaction == BAD_REACTION:
            if user_id in all_photos_messages[message_id]['good_reactions']:
                channel = bot.get_channel(channel_id)
                message = await channel.fetch_message(message_id)
                await message.remove_reaction(payload.emoji, discord.Object(user_id))
                logging.warning(f"2req. Incorrect reaction added. User: {user_id}")
                return
            else:
                all_photos_messages[message_id]['bad_reactions'].append(user_id)
        else:
            if user_id in all_photos_messages[message_id]['bad_reactions']:
                channel = bot.get_channel(channel_id)
                message = await channel.fetch_message(message_id)
                await message.remove_reaction(payload.emoji, discord.Object(user_id))
                logging.warning(f"2req. Incorrect reaction added. User: {user_id}")
                return
            else:
                all_photos_messages[message_id]['good_reactions'].append(user_id)
    else:
        if reaction == BAD_REACTION:
            if user_id in all_stories_messages[message_id]['good_reactions']:
                channel = bot.get_channel(channel_id)
                message = await channel.fetch_message(message_id)
                await message.remove_reaction(payload.emoji, discord.Object(user_id))
                logging.warning(f"2req. Incorrect reaction added. User: {user_id}")
                return
            else:
                all_stories_messages[message_id]['bad_reactions'].append(user_id)
        else:
            if user_id in all_stories_messages[message_id]['bad_reactions']:
                channel = bot.get_channel(channel_id)
                message = await channel.fetch_message(message_id)
                await message.remove_reaction(payload.emoji, discord.Object(user_id))
                logging.warning(f"2req. Incorrect reaction added. User: {user_id}")
                return
            else:
                all_stories_messages[message_id]['good_reactions'].append(user_id)


@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    user_id = payload.user_id
    channel_id = payload.channel_id
    reaction = str(payload.emoji)

    if user_id == bot.user.id:
        return

    try:
        if channel_id == VOTING_CHANNEL_ID_OUTFITS:
            if reaction == BAD_REACTION:
                all_photos_messages[message_id]['bad_reactions'].remove(user_id)
            else:
                all_photos_messages[message_id]['good_reactions'].remove(user_id)
        else:
            if reaction == BAD_REACTION:
                all_stories_messages[message_id]['bad_reactions'].remove(user_id)
            else:
                all_stories_messages[message_id]['good_reactions'].remove(user_id)
    except:
        logging.warning("Woopsie doopsie")


@bot.tree.command(name="purgis")
async def purgis(interaction: discord.Interaction):
    global no_reaction
    if str(IT_ROLE_ID) not in str(interaction.user.roles):
        no_reaction = True
        await interaction.response.send_message("You need to the the IT role to be able to use this command",
                                                ephemeral=True)
        return

    submission_channel_photos = bot.get_channel(SUBMISSIONS_CHANNEL_ID_OUTFITS)
    submission_channel_stories = bot.get_channel(SUBMISSIONS_CHANNEL_ID_STORIES)
    voting_channel_photos = bot.get_channel(VOTING_CHANNEL_ID_OUTFITS)
    voting_channel_stories = bot.get_channel(VOTING_CHANNEL_ID_STORIES)

    no_reaction = True
    await interaction.response.send_message("Purginu krc")

    await submission_channel_photos.purge()
    await submission_channel_stories.purge()
    await voting_channel_photos.purge()
    await voting_channel_stories.purge()


@bot.tree.command(name="count", description="pisi uzpisai davai ['winners', 'losers']")
async def count(interaction: discord.Interaction, nezinom_kaip_pavadinti: str):
    global no_reaction
    if str(IT_ROLE_ID) not in str(interaction.user.roles):
        no_reaction = True
        await interaction.response.send_message("You need to the the IT role to be able to use this command",
                                                ephemeral=True)
        return

    if interaction.channel_id in [VOTING_CHANNEL_ID_OUTFITS, VOTING_CHANNEL_ID_STORIES]:
        msgs = []

        if nezinom_kaip_pavadinti not in ["winners", "losers"]:
            no_reaction = True
            await interaction.response.send_message("Xuj cia pezi", ephemeral=True)
            return

        async for msg in interaction.channel.history():
            if len(msg.reactions) == 2:
                msgs.append(msg)

        def sort_by_like(e):
            return e.reactions[0].count

        def sort_by_skull(e):
            return e.reactions[1].count

        index = 0
        emoji = ''

        if nezinom_kaip_pavadinti == "winners":
            msgs.sort(reverse=True, key=sort_by_like)
            index = 0
            emoji = '👍'
        else:
            msgs.sort(reverse=True, key=sort_by_skull)
            index = 1
            emoji = '💀'

        winner_list = ''
        current_winner = 1
        for msg in msgs:
            msg_embeds = msg.embeds
            if current_winner > 10:
                break
            if msg.channel.id == VOTING_CHANNEL_ID_STORIES:
                winner_list += f"{current_winner}. {msg_embeds[0].description} [Scawy story](https://discord.com/channels/{GUILD_ID}/{interaction.channel_id}/{msg.id})  Votes received: {msg.reactions[index].count} {emoji}\n"
            if msg.channel.id == VOTING_CHANNEL_ID_OUTFITS:
                winner_list += f"{current_winner}. {msg_embeds[0].description} [Costume](https://discord.com/channels/{GUILD_ID}/{interaction.channel_id}/{msg.id})  Votes received: {msg.reactions[index].count} {emoji}\n"
            current_winner += 1

        embed = discord.Embed(title=nezinom_kaip_pavadinti.capitalize(),
                              description=winner_list,
                              color=0xFF5733)

        no_reaction = True
        await interaction.response.send_message(embed=embed)

    else:
        await interaction.response.send_message("this only works in voting channels!")


bot.run(TOKEN)
