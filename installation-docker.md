# Installation inside a Docker container
Only recently I started packaging the bot inside a docker container, so, 
these instructions are newly written and not thoroughly tested.

### Requirements: 
+ `git`
+ `docker`

### Intents
[Visit this page](https://discord.com/developers/applications/), locate your bot and enable 
- SERVER MEMBERS INTENT
- MESSAGE CONTENT INTENT

### Where is the bot's data folder
+ inside the container, `/root/.local/share/Momiji`  
If you are restoring a database backup, it goes into this folder.

### API keys and tokens
You need to either supply them via environment variables.
| environment variables | where to get |
| ------------- | ------------- |
| MOMIJI_TOKEN  | [create a new app, make a bot acc](https://discord.com/developers/applications/) |


### Building a docker container
These instructions are newly written and not thoroughly tested, but what you should be doing looks something like this: 

```bash
git clone https://github.com/Kyuunex/Momiji.git -b master # replace master with version from Releases tab
cd Momiji
docker build -t momiji .
docker run -e MOMIJI_TOKEN=your_bot_token_goes_here momiji # first run only

docker start container_name # subsequent runs
```

### Updating from inside the container
If you shell into the container, this is how you update the version, you typically shouldn't use docker like this.
```sh
python3 -m pip install git+https://github.com/Kyuunex/Momiji.git@master --upgrade
# wget -O $HOME/.local/share/Momiji/maindb.sqlite3 REPLACE_THIS_WITH_DIRECT_FILE_LINK # optional database backup restore
```
replace `master` with version from Releases tab
