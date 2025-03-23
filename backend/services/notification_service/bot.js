// channel link: https://discord.com/channels/1353049034041851986/1353049034041851988
// tournament bot is able to send notifications in the channel in ESD server


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


// run node bot.js, and view the sent notfication in the server
//call sendMessage() in the relevant microservice when an event occurs.

