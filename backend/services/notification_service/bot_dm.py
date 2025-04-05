import discord
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve bot token and guild ID
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))  # Ensure it's an integer

intents = discord.Intents.default()
intents.members = True  # Required to fetch users from the server
intents.dm_messages = True  # Required for sending DMs

client = discord.Client(intents=intents)

GUILD_ID = 1353049034041851986  # Replace with your server's actual ID

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    guild = client.get_guild(GUILD_ID)  # Get the Discord server
    if guild is None:
        print("Bot is not in the specified server!")
        return
    print(f"Connected to guild: {guild.name}")

async def get_user_id_from_username(username):
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        return None
    
    # Force bot to load all members
    await guild.chunk()

    # Search for user in the server
    for member in guild.members:
        if member.name == username or member.display_name == username:
            return member.id  # Return the Discord User ID
    return None  # User not found

async def send_private_message_by_username(username, message):
    user_id = await get_user_id_from_username(username)
    if user_id is None:
        print(f"User {username} not found in the server.")
        return

    user = await client.fetch_user(user_id)
    await user.send(message)
    print(f"Sent message to {username} (ID: {user_id})")

# Scenario 1: Team Assignment - player (dm)
@client.event
async def team_assignment(username, teamId): 
    print(f'Logged in as {client.user}')
    message = f'Hello {{{username}}}, you have joined {{{teamId}}}.'
    await send_private_message_by_username(username, message)

# # Scenario 3: Dispute Resolution - moderator (dm)
# @client.event
# async def on_ready(): #--> need to change function
#     print(f'Logged in as {client.user}')
#     username = "sadhana_123_smu"  # Replace with your actual Discord username - need to fetch from moderator microservice
#     message = f'Hello {{username}}, you have a new {{disputeId}} to review.'
#     await send_private_message_by_username(username, message)

client.run(TOKEN)  
