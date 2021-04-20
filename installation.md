## Old Installation Method Instructions

1. Install `git` and [Python](https://www.python.org/) (version 3.6 or newer compatible) if you don't already have them.
2. Clone this repository. (`git clone https://github.com/Kyuunex/Momiji.git`)
3. Install requirements. (`python3 -m pip install -r requirements.txt`)
4. For your bot token, you first need to register an application on 
   [Discord's developer site](https://discord.com/developers/applications/) and creating a bot. 
   After that, you can either:
      + In this bot's `AppData`/`.config` folder, create `token.txt` file and put the bot token in.
      + Supply it with `MOMIJI_TOKEN` environment variable.
5. If you are restoring a backup, just put the database file in the this bot's `AppData`/`.config` folder.
6. To start the bot, run `run_momiji.py`. I recommend installing the bot as a `systemd` service though.
7. Figure out the rest yourself.

## Modern installation
After making sure you have `git` and Python 3.6+ installed, type the following in the command line  
`python3 -m pip install git+https://github.com/Kyuunex/Momiji.git`  
To run the bot, type `python3 -m momiji`

### If you are SSHing into a GNU/Linux server, you can just type these to achieve the same thing

```sh
python3 -m pip install git+https://github.com/Kyuunex/Momiji.git
mkdir -p $HOME/.local/share/Momiji
# wget -O $HOME/.local/share/Momiji/maindb.sqlite3 REPLACE_THIS_WITH_DIRECT_FILE_LINK # only do if you are restoring a backup
echo "REPLACE_THIS_WITH_BOT_TOKEN" | tee $HOME/.local/share/Momiji/token.txt
```


## Installing the bot as a systemd service

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
ExecStart=/usr/bin/python3 -m momiji

[Install]
WantedBy=multi-user.target
```

The above assumes `pi` as a username of the user the bot will be run under. Change it if it's different. 
Make sure to change the paths too. The default assumes you just clone the thing in the user's home folder.  
Make sure the requirements are installed under the user the bot will be run under.  
After you are done, type `sudo systemctl enable --now momiji.service` to enable and start the service.
