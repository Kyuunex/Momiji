# Momiji
The only Discord bot you'll ever need.

Momiji is a discord bot that actually learns from the messages it can see and responds you with the knowledge it obtained. Each channel has it's own personality, this is to prevent leaking stuff between channels and servers. Basically if a channel has a personality, Momiji would be it. How cancerous Momiji is really depends on stuff you guys talk about in the channel.

This bot is built using discord.py rewrite library and uses sqlite3 database.

---

## Installation Instructions

1. Clone this git (strongly recommended rather than downloading zip because it uses `git pull` for updates)
2. Install `python 3.6.7` or newer if you don't have it
3. Install `discord.py rewrite library` using this command `python -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]`
4. Before using, you need to create a folder called `data` and create `token.txt` in it. Then put your bot token in the file. 
5. Run `run.py` with command line, like `python momiji.py` on windows or `python3 momiji.py` on linux or use the batch file or however you want. It's recommended to run it in a loop so it restarts when it exists. Built-in updater requires this.

## Stuff

1. To use it's intelligent, after adding the bot, let it sit there for few days so it learns things from new messages posted in channels. To make it talk, simply include `momiji` in the message you send and it will respond. Alternatively, you can use `;import` command to import message from the channel. You'll have to do this in every channel you plan to use this bot in though if you don't want to wait.
2. Since I have implemented channel separation in the bot to prevent leaking, if you wanna speak to momiji in bot command channel but don't want it to respond with bot commands, you have to bridge that channel with a channel where users speak normally, to do that, you do in bot channel, `;bridge channel <channel id>` where `<channel id>` the ID of the channel you want it to take messages from.
3. The bot has no way of knowing when a message is deleted (for now), and it keeps every message it can use. Meaning if somebody said really against the rules stuff in a channel, momiji will learn that and may respond with it randomly. You can manually remove that message from the database though. This is the biggest problem I have to solve soon, probably using message IDs. Alternatively you can add more words to the blacklist. I'll write those docs later.
4. Of course there are some other Easter eggs in this bot.

---

## I'll write more docs and etc later.

---

## Data it uses

Every message this bot stores is pretty much essential because this is how the bot operates. Don't use this data for unethical things.

---

To see this bot in action or if you need help setting it up, you can join the support server https://discord.gg/KGjYZZg

---

Also, credits to whoever made `pinged.gif`, I don't know who made it sorry, or I would have put his name here. Therefore, license of this repository applies everything in here except `pinged.gif`.