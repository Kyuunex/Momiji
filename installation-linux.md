# Installation on Linux
NOTE: This is not recommended for production use. Instead, try [docker method](installation-docker.md) instead.

### Requirements:
+ `git`
+ `python3` (version 3.10 minimum)
+ `python3-venv`

### Intents
[Visit this page](https://discord.com/developers/applications/), locate your bot and enable 
- SERVER MEMBERS INTENT
- MESSAGE CONTENT INTENT

### Where is the bot's data folder
`/home/username/.local/share/Momiji`  
If you are restoring a database backup, it goes into this folder.

### API keys and tokens
You need to either put them in the respective text files in the bot's data folder or 
supply them via environment variables. if you do both, env vars will be used  

| text file  | environment variables | where to get |
| ------------- | ------------- | ------------- |
| token.txt  | MOMIJI_TOKEN  | [create a new app, make a bot acc](https://discord.com/developers/applications/) |

### Installation for production use
```sh
mkdir -p $HOME/.local/share/Momiji
python3 -m venv $HOME/.local/share/Momiji/venv
source $HOME/.local/share/Momiji/venv/bin/activate
python3 -m pip install git+https://github.com/Kyuunex/Momiji.git@master --upgrade  # You can replace this with a release if you want
```
Repeat the commands 3 and 4 for upgrading.

### Bot Configuration
```sh
# wget -O $HOME/.local/share/Momiji/maindb.sqlite3 REPLACE_THIS_WITH_DIRECT_FILE_LINK  # optional database backup restore
echo "your_bot_token_goes_here" | tee $HOME/.local/share/Momiji/token.txt
```

### Configuring the bot as a systemd service
The purpose of this is to make the bot start automatically on boot, useful for example after a power outage.  

Create the following file: `/lib/systemd/system/momiji.service`  
Inside it, put the following:
```ini
[Unit]
Description=Momiji
After=network.target
StartLimitIntervalSec=0

[Service]
Restart=always
RestartSec=5
User=pi
Type=simple
ExecStart=/home/pi/.local/share/Momiji/venv/bin/python3 -m momiji

[Install]
WantedBy=multi-user.target
```

The above assumes `pi` as a username of the user the bot will be run under. Change it if it's different. 
Make sure this is run under the same user the pip3 command was ran as.  
If you want, you can add env vars in this file in the `[Service]` section as per this example
```ini
[Service]
Environment="MOMIJI_TOKEN=your_bot_token_goes_here"
```  

After you are done, type `sudo systemctl enable --now momiji.service` to enable and start the service.
