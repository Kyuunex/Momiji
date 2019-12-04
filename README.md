# Momiji
The only Discord bot you'll ever need. Built using discord.py and uses sqlite3 database.

Momiji is a fake AI Discord bot that actually learns from the messages it can see and responds you with the knowledge it obtained from that channel, when it is triggered. Basically, if a channel has a personality, Momiji would be it. How cancerous Momiji is in a given channel really depends on the messages sent in that channel.

---

![](https://i.imgur.com/v0kgBww.png)

---

# By the way I tend to make database related changes which can break the bot after updating if you don't adjust the database accordingly
I am sorry, but this happens when you want to add new features and accounting for this is a waste of time on my end.

---

## Installation Instructions

1. Install `git` and `Python 3.6` (or newer) if you don't already have them.
2. Clone this repository using this command `git clone https://github.com/Kyuunex/Momiji.git`
3. Install requirements using this command `python3 -m pip install -r requirements.txt`.
4. Create a folder named `data`, then create `token.txt` inside it. Then put your bot token in it. 
5. To start the bot, run `momiji.bat` if you are on windows or `momiji.sh` if you are on linux. Alternatively, you can manually run `momiji.py` file but I recommend using the included launchers because it starts the bot in a loop which is required by the `;restart` and `;update` commands.

---

## Configuration
To configure momiji, you are mostly gonna need to use sql commands. Everything in the database is stored as a string. There are more config settings out there, I just don't have time to document all of them.

### config
In this table, various configs are stored. 
The table columns are:
+ `setting` - Identifies what setting is this row represents
+ `parent` - This almost always indicates what guild this setting is for. If the setting is guild independent, it does not matter what is specified but a value of `0` is what I recommend for consistencey.
+ `value` - This indicates the value of the setting. This almost always stores a channel id/role id/api key. 
+ `flag` - Another value for this config that specifies something else regarding this setting. This column is not always used.

#### `setting` column can be any of these things
+ `google_api_key` - This setting stores google api key. It enables `;img` command. You can keep this setting absent if you don't wanna use the `;img` command.
    + `value` column for this setting must contain a google api key.
+ `google_search_engine_id` - This setting stores google search engine id. This setting is required for `;img` command to work.
    + `value` column for this setting must contain a google search engine id.

To set a config, follow this example command `;sql INSERT INTO config VALUES ("<setting>", "<parent>", "<value>", "<flag>")`. If a setting does not require a specific column, set that column to `0`. I moved most things to other tables, I'll get to documenting these or maybe adding commands.

### Bridging
Bridging feature ties the specified channel to a module or to another channel. This is used when you wanna grab messages from another channel, or use a custom module to generate custom messages.
To bridge a channel, type `;bridge [module/channel] [<channel_id>/<module_name>]`

### Blacklist
Blacklist is used to blacklist words what you never want the bot to respond with. I highly recommend blacklisting offensive words just to stay away from trouble.
To blacklist a word, type `;blacklist <whatever you want to blacklist>`

### Blacklist channels from pinning
By default, if a `guild_pin_channel` is configured for a guild, every channel the bot sees is eligible to have it's messages pinned in the pin channel. Blacklisting a channel will make messages from that channel unpinnable in the pin channel.
To blacklist a channel, type `;sql INSERT INTO pin_channel_blacklist VALUES ("<channel_id>")`

### Music playback
Momiji's music functionality is playlist based. In the `data` folder, you create a folder named `audio` and put you `mp3`, `ogg` or `flac` files in. Currently, only bot admins can play music with this bot.
For music to play, the bot must be in the voice channel, duh.  
`;vc_[join/leave]` - Join/Leave voice chat  
`;m_[play/stop/next]` - Music controls

---

## Stuff to note

+ Momiji's main functionality is taking a random message that has been said by someone else and replying with it once someone triggers Momiji. When Momiji first joins a server, it has no collection of chat logs. It's highly recommended import messages from the channel immediately so Momiji can get to working as intended. To import messages from every channel the bot sees, type `;import server`. This will import old messages. This may take a very very long time depending on how many messages there are to import. Newer messages are automatically stored.
+ To prevent leaking information between channels, Momiji will pick a message that has been said in that current channel before.
+ I recommend blacklisting some offensive words with this command `;blacklist <whatever you want to blacklist>`.
+ To bring up the admin help menu type `;help admin`.

---

## Data it uses

For Momiji to work, it collects chat logs. It is essential for operation. While this can be done in other ways, I opted for this because some current and future functionality won't work without this. In my hosted instace of this bot, any data collected through this bot stays on my server, and is not given to anyone else. If you are self hosting, don't give the data you collect to anyone.

---

Also, credits to whoever made `pinged.gif`, I don't know who made it, sorry, or I would have put his name here. Therefore, license of this repository applies everything in here except `pinged.gif`.
