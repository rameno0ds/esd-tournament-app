#retrieves the giuld id and channel id from the env file
#retrieves dicord player_id from username/ display name of player in the server channel
#sends a direct message to plyaer using the discord player_id

import discord
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Setup Discord client
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# Track bot readiness
ready_event = False

@client.event
async def on_ready():
    global ready_event
    print(f"Bot is ready. Logged in as {client.user}")
    ready_event = True

# Utility to get user ID from username
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

# Utility to send a private message to user
async def send_private_message_by_username(username, message):
    user_id = await get_user_id_from_username(username)
    if user_id is None:
        return
    user = await client.fetch_user(user_id)
    await user.send(message)
    print(f"Sent DM to {username} (ID: {user_id})")

#player_name is the username of player on our website (which has to match with the discord username/ display name)
#team_id is the team that the player joined
async def team_assignment(player_name, team_id): 

    username = player_name
    message = f"Hello {username}, you have joined team {team_id}."
    await send_private_message_by_username(username, message)

# # Scenario 3: Dispute Resolution - moderator (dm)
# async def view_dispute(): 
#     print(f'Logged in as {client.user}')
#     username = "sadhana_123_smu"  # Replace with your actual Discord username - need to fetch from moderator microservice
#     message = f'Hello {{username}}, you have a new {{disputeId}} to review.'
#     await send_private_message_by_username(username, message)

