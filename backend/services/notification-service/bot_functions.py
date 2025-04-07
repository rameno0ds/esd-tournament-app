import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)
ready_event = False

@client.event
async def on_ready():
    global ready_event
    print(f"✅ Bot is ready. Logged in as {client.user}")
    ready_event = True

async def get_user_id_from_username(username):
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        return None
    await guild.chunk()
    for member in guild.members:
        if member.name == username or member.display_name == username:
            return member.id
    print(f"User {username} not found in guild")
    return None

async def send_private_message_by_username(username, message):
    user_id = await get_user_id_from_username(username)
    if user_id is None:
        return
    user = await client.fetch_user(user_id)
    await user.send(message)
    print(f"📨 Sent DM to {username} (ID: {user_id})")

#Scenario 1
async def team_assignment(player_name, team_id): 
    username = player_name
    message = f"Hello {player_name}, you have joined team {team_id}."
    print(message)
    await send_private_message_by_username(username, message)

# # Secnario 2: Match making
# async def match_making():
#     print(f'Logged in as {client.user}')
#     channel_id = int(os.getenv('CHANNEL_ID'))  
#     channel = client.get_channel(channel_id)
#     # Send a message to the channel in Scenario 2: Match making
#     if channel:
#         message = f"This is the upcoming schedule: {{schedule}}."
#         await channel.send(message)

#scenario 3: notify moderator
async def new_dispute(match_id, raised_by):
    username = "bossman"
    message = f"New dispute raised by {raised_by} for match {match_id}"
    print(message)
    await send_private_message_by_username(username, message)

# #scenario 3: dispute resolution
# async def resolution_result():
#     print(f'Logged in as {client.user}')
#     channel_id = int(os.getenv('CHANNEL_ID'))  
#     channel = client.get_channel(channel_id)
#     # Send a message to the channel in Scenario 3: Dispute resolution
    
#     if channel:
#         message = f"Results for dispute for {{matchId}} is {{status}}."
#         await channel.send(message)