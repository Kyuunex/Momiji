from modules import dbhandler
import time
import json
import discord
from collections import Counter
import operator


async def msgfilter(message, isobject):
    if isobject:
        contents = message.content
    else:
        contents = message
    if len(contents) > 0:
        blacklist = await dbhandler.query("SELECT value FROM blacklist")
        if not (any(c[0] in contents.lower() for c in blacklist)):
            if not (any(contents.startswith(c) for c in (";", "'", "!", ",", ".", "=", "-"))):
                if isobject:
                    if not message.author.bot:
                        return contents
                    else:
                        return None
                else:
                    return contents
            else:
                return None
        else:
            return None


async def isntbotcheck(userjson):
    jsondict = json.loads(userjson)
    if jsondict[0]['bot'] == True:
        return False
    elif jsondict[0]['bot'] == False:
        return True


async def get_channel(channels, channel_id):  # client.get_all_channels()
    for channel in channels:
        if channel.id == channel_id:
            return channel
    return None


class json_to_user:
    def __init__(self, userjson):
        jsondict = json.loads(userjson)
        self.id = jsondict[0]['id']
        self.discriminator = jsondict[0]['discriminator']
        self.avatar = jsondict[0]['avatar']
        self.name = jsondict[0]['username']
        self.nick = None
        if jsondict[0]['bot'] == True:
            self.bot = True
        elif jsondict[0]['bot'] == False:
            self.bot = False


async def cooldowncheck(setting, howlong):
    # TODO: make the cooldowns guild by guild basis
    if not await dbhandler.query(["SELECT value FROM temp WHERE setting = ?", [setting]]):
        await dbhandler.query(["INSERT INTO temp VALUES (?, ?, ?)", [setting, str("0"), str("0")]])
    lasttime = (await dbhandler.query(["SELECT value FROM temp WHERE setting = ?", [setting]]))[0][0]
    if float(time.time())-float(lasttime) > int(howlong):
        await dbhandler.query(["UPDATE temp SET value = ? WHERE setting = ? ", [str(time.time()), setting]])
        return True
    else:
        return None


async def measuretime(starttime, endtime):
    timeittook = int(endtime - starttime)
    if timeittook > 120:
        minutes = int(timeittook / 60)
        seconds = int(timeittook % 60)
        return "%s minutes and %s seconds" % (str(minutes), str(seconds))
    else:
        return "%s seconds" % (str(timeittook))


async def messageembed(message):
    if message:
        if message.embeds:
            embed = message.embeds[0]
        else:
            embed = discord.Embed(
                description=message.content,
                color=0xFFFFFF
            )
            if message.attachments:
                attachment = (message.attachments)[0]
                embed.set_image(
                    url=attachment.url
                )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.avatar_url
            )
        return embed
    else:
        return None


async def messagecounter(messageadata):
    results = dict(Counter(messageadata))
    return reversed(sorted(results.items(), key=operator.itemgetter(1)))
