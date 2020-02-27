### This is outdated btw

## Configuration
To configure momiji, you are mostly gonna need to use sql commands. Everything in the database is stored as a string. There are more config settings out there, I just don't have time to document all of them.

### config
In this table, various configs are stored. 
The table columns are:
+ `setting` - Identifies what setting is this row represents
+ `parent` - This almost always indicates what guild this setting is for. If the setting is guild independent, it does not matter what is specified but a value of `0` is what I recommend for consistency.
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
