# Momiji
The only Discord bot you'll ever need. Built using discord.py rewrite library and uses sqlite3 database.

Momiji is a discord bot that actually learns from the messages it can see and responds you with the knowledge it obtained when it is triggered. Each channel has it's own personality, this is to prevent leaking stuff between channels and servers. Basically if a channel has a personality, Momiji would be it. How cancerous Momiji is really depends on stuff you guys talk about in the channel.
![](https://i.imgur.com/fzYwxUr.png)

---

## Installation Instructions

1. Install `git` if you don't already have it.
2. Clone this repo using this command `git clone https://github.com/Kyuunex/Momiji.git`
3. Install `Python 3.5.3` or newer if you don't have it
4. Install `discord.py rewrite library` using this command `python -m pip install -U discord.py[voice]` for Windows and `python3 -m pip install -U discord.py[voice]` for Linux.
5. Create a folder called `data` and create `token.txt` in it. Then put your bot token in the file. 
6. To start the bot, run `momiji.bat` if you are on windows or `momiji.sh` if you are on linux. Alternatively, you can manually run `run.py` file but I recommend using the included launchers because it starts the bot in a loop which is required by the `;restart` and `;gitpull` commands.

---

## Configuration
To configure momiji, you are mostly gonna need to use sql commands.   Everything in the database is stored as a string.

### config
In this table, various configs are stored. 
The table columns are:
+ `setting` - Identifies what setting is this row represents
+ `parent` - This almost always indicates what guild this setting is for. If the setting is guild independent, it does not matter what is specified but a value of `0` is what I recommend for consistencey.
+ `value` - This indicates the value of the setting. This almost always stores a channel id/role id/api key. 
+ `flag` - Another value for this config that specifies something else regarding this setting. This column is not always used.

#### `setting` column can be any of these things
+ `guildregularsrole` - This setting enables "Regulars" functionality in the guild. It enables `;regulars` command. 
    + `parent` column for this setting must contain a guild id. 
    + `value` column for this setting must contain a role id for the regular role.
    + `flag` column for this setting must contain the amount of members the role can be asigned to. For example, a value of `20` will give top 20 mebers this role.
+ `googleapikey` - This setting stores google api key. It enables `;img` command. You can keep this setting absent if you don't wanna use the `;img` command.
    + `value` column for this setting must contain a google api key.
+ `googlesearchengineid` - This setting stores google search engine id. This setting is required for `;img` command to work.
    + `value` column for this setting must contain a google search engine id.
+ `guildpinchannelid` - This setting enables pin functionality in the guild. When a message gets 6 of the same reactions, it will be pinned in the pin channel.
    + `parent` column for this setting must contain a guild id. 
    + `value` column for this setting must contain a channel id where messages will be posted by the bot.
    + `flag` column for this setting is unused for now but will contain amount of reactions required for pinning.
+ `guildlogchannel` - This setting enables logging functionality in the guild. When this is enabled, User Leave, User Join, Message Delete, Message Edit notifications will be posted in the specified channel. 
    + `parent` column for this setting must contain a guild id. 
    + `value` column for this setting must contain a channel id where the logs go.
+ `guildvoicelogchannel` - This setting enables voice join/leave logging functionality in the guild. When this is enabled, User Join, User Leave, User Switch Voice channel notifications will be posted in the specified channel. 
    + `parent` column for this setting must contain a guild id. 
    + `value` column for this setting must contain a channel id where the logs go.

To set a config, follow this example command `;sql INSERT INTO config VALUES ("<setting>", "<parent>", "<value>", "<flag>")`. If a setting does not require a specific column, set that column to `0`.

### Bridging
Bridging feature ties the specified channel to a module or to another channel. This is used when you wanna grab messages from another channel, or use a custom module to generate custom messages.
To bridge a channel, type `;bridge [module/channel] [<channelid>/<modulename>]`

### Blacklist
Blacklist is used to blacklist words what you never want the bot to respond with. I highly recommend blacklisting offensive words just to stay away from trouble.
To blacklist a word, type `;blacklist <whatever you want to blacklist>`

### Blacklist channels from pinning
By default, if a `guildpinchannelid` is configured for a guild, every channel the bot sees is eligable to have it's messages pinned in the pin channel. Blacklisting a channel will make messages from that channel unpinnable in the pin channel.
To blacklist a channel, type `;sql INSERT INTO pinchannelblacklist VALUES ("<channel id>")`

### Music playback
Momiji's music functionality is playlist based. In the `data` folder, you create a folder named `audio` and put you `mp3`, `ogg` or `flac` files in. Currently, only bot admins can play music with this bot.
For music to play, the bot must be in the voice channel, duh.  
`;vc [join/leave]` - Join/Leave voice chat  
`;music [play/stop/next]` - Music controls

---

## Stuff to note

+ Momiji's main functionality is taking a random message that has been said by someone else and replying with it once someone triggers Momiji. When Momiji first joins a server, it has no collection of chat logs. It's highly recommended import messages from the channel immediately so Momiji can get to working as intended. To import messages, type `;import` in each channel you are importing or if you wanna import multiple channels at once, type `;import <channel id> <channel id> <channel id> <channel id>...`. Basically, a list of channel ids separated by space. This will import old messages. This may take a very very long time depending on how many messages there are to import. Newer messages are automatically stored.
+ To prevent leaking information between channels, Momiji will pick a message that has been said in that current channel before.
+ The bot has no way of knowing when a message is deleted (for now), and it keeps every message it can use. Meaning if somebody said really against the rules stuff in a channel, momiji will learn that and may respond with it randomly. This is why I recommend blacklisting some offensive words with this command `;blacklist <whatever you want to blacklist>`.
+ To bring up the admin help menu type `;help admin`.

---

## Data it uses

For Momiji to work, it collects chat logs. It is essential for operation. While this can be done in other ways, I opted for this because a future update I am planning cannot work if I don't collect chat logs. In my hosted instace of this bot, any data collected through this bot stays on my server, and is not given to anyone else. If you are self hosting, don't give the data you collect to anyone.

---

## Support

To see this bot in action or if you need help setting it up, you can join the support server https://discord.gg/KGjYZZg but please, before you ask me anything, try to figure out how to make it work yourself.

---

Also, credits to whoever made `pinged.gif`, I don't know who made it sorry, or I would have put his name here. Therefore, license of this repository applies everything in here except `pinged.gif`.
