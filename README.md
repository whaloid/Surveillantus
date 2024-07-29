# Surveillantus
Discord SIGINT and OSINT Bot for anti-vandal protection.
invitation url: [https://discord.com/oauth2/authorize?client_id=1267002222299058298](https://discord.com/oauth2/authorize?client_id=1267002222299058298)

## What is this?
Surveillantus is a discord SIGINT system for protection from vandals.
This system is consisted from 3 components:
- Many self-bot logger

  many selfbots are running ```run_selfspybot.py``` to log the messages sent from the servers where they are embedded in.
  The logged messages are sent to data server by touching its API. 
- Database and reference API

  The API receives and sends logged messages. The API is implemented in ```surveillantus_api.php```.
  This API reads and writes a database using MySQL.
- Front-end search bot

  You can search the activities of discord users including vandals by sending commands to this bot.
  Invitation URL is available above.
  Search bot provides many function like below:
  - Search messages from word, username, channels, etc.
  - Get the basical information of channels and members in a certain server
  - Summerize the logged message sent by certain users or channels using LLM
  - etc.
