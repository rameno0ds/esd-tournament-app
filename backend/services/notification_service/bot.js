// channel link: https://discord.com/channels/1353049034041851986/1353049034041851988
// run node bot.js, and view the sent notfication in the ESD server, under gernal channel

require('dotenv').config(); // This loads the .env file
const { Client, GatewayIntentBits } = require('discord.js');

// Use the token from the .env file
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages
  ]
});

// When the bot is ready
client.once('ready', () => {
  console.log('Bot is online!');
});

client.login(process.env.DISCORD_BOT_TOKEN);  // Get the token from the .env file

// Function to send a message to a channel
async function sendMessage(channelId, message) {
  try {
    const channel = await client.channels.fetch(channelId);
    channel.send(message);
  } catch (error) {
    console.error('Error sending message:', error);
  }
}


// Example: Sending a test message to a specific channel
client.once('ready', () => {
  const channelId = '1353049034041851988'; // Replace with the target channel ID
  const message = 'Hello, this is a test notification from the tournament!';
  sendMessage(channelId, message);
});

//Scenario 1: Team Assignment - player (private message)
// client.once('team assigned', () => {
//     const channelId = ''; #need to change to DM
//     const message = 'Hello {player/username}, {player/username} has joined your Team {team/teamId}.';
//     sendMessage(channelId, message);
//   });


//Scenario 2: Match making - tournament (server)
// client.once('match assigned', () => {
//     const channelId = '1353049034041851988'; 
//     const message = 'This is the upcoming schedule: {schedule}.';
//     sendMessage(channelId, message);
//   });


//Scenario 3: Dispute resolution - moderator (private message)
// client.once('dispute open', () => {
//     const channelId = ''; #need to change to DM
//     const message = 'Hello {moderator/username}, you have a new Dispute {dispute/disputeId} to review.';
//     sendMessage(channelId, message);
//   });


//Scenario 3: Dispute resolution - tournament (server)
// client.once('', () => {
//     const channelId = '1353049034041851988'; 
//     const message = 'Results for dispute for Match {match/matchId} is {dispute/status}.';
//     sendMessage(channelId, message);
//   });