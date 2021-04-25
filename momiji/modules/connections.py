import os
from momiji.modules.storage_management import dirs

if os.environ.get('MOMIJI_TOKEN'):
    bot_token = os.environ.get('MOMIJI_TOKEN')
else:
    try:
        with open(dirs.user_data_dir + "/token.txt", "r+") as token_file:
            bot_token = token_file.read().strip()
    except FileNotFoundError as e:
        print("i need a bot token. either set MOMIJI_TOKEN environment variable")
        print("or put it in token.txt in my AppData/.config folder")
        raise SystemExit
