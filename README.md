# Momiji
The only Discord bot you'll ever need. Built using discord.py rewrite library and uses sqlite3 database.

Momiji is a discord bot that actually learns from the messages it can see and responds you with the knowledge it obtained. Each channel has it's own personality, this is to prevent leaking stuff between channels and servers. Basically if a channel has a personality, Momiji would be it. How cancerous Momiji is really depends on stuff you guys talk about in the channel.

---

## This documentation is incomplete. 
## I regularly change database structure so I can add features so updating and keeping the old database will break the bot sometimes. You are gonna have to start from scratch and use ;import command to import messages

---

## Installation Instructions

1. Clone this git (strongly recommended rather than downloading zip because it uses `git pull` for updates)
2. Install `Python 3.5.3` or newer if you don't have it
3. Install `discord.py rewrite library` using this command `python -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]`
4. Before using, you need to create a folder called `data` and create `token.txt` in it. Then put your bot token in the file. 
5. Run `run.py` with command line, like `python run.py` on windows or `python3 run.py` on linux or use the batch file or however you want. It's recommended to run it in a loop so it restarts when it exists. Built-in updater requires this.

## Stuff

+ Momiji's main functionality is taking a random message that has been said by someone else and replying with it once someone triggers Momiji.
+ When Momiji first joins a server, it has no collection of chat logs. It's highly recommended import messages from the channel immediately so Momiji can get to working as intended. To import messages, type `;import` in each channel you are importing or if you wanna import multiple channels at once, type `;import <channel id> <channel id> <channel id> <channel id>...`. Basically, a list of channel ids separated by space. This will import old messages. Newer messages are automatically stored.
+ To prevent leaking information between channels, Momiji will pick a message that has been said in that current channel before.
+ The bot has no way of knowing when a message is deleted (for now), and it keeps every message it can use. Meaning if somebody said really against the rules stuff in a channel, momiji will learn that and may respond with it randomly. You can manually remove that message from the database though. This is the biggest problem I have to solve soon, probably using message IDs. Alternatively you can add more words to the blacklist. I'll write those docs later.
+ To bring up the admin help menu type `;help admin`.
+ Configuration is done through sql commands. I'll write those docs later.

---

## Data it uses

For Momiji to work, it collects chat logs. It is essential for operation. While this can be done in other ways, I opted for this because a future update I am planning cannot work if I don't collect chat logs. Any data collected through this bot stays on my server, and is not given to anyone else. Don't give the data you collect to anyone.

---

To see this bot in action or if you need help setting it up, you can join the support server https://discord.gg/KGjYZZg

---

Also, credits to whoever made `pinged.gif`, I don't know who made it sorry, or I would have put his name here. Therefore, license of this repository applies everything in here except `pinged.gif`.