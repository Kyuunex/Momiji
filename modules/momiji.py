import random
import discord
import asyncio
import time
import json
from modules import db
from modules import cr_pair


async def isntbotcheck(user_info):
    jsondict = json.loads(user_info)
    if jsondict[0]['bot'] == True:
        return False
    elif jsondict[0]['bot'] == False:
        return True


async def bridgecheck(channel_id):
    bridgedchannel = db.query(["SELECT value FROM bridges WHERE channel_id = ? AND type = ?", [str(channel_id), "channel"]])
    if bridgedchannel:
        return str(bridgedchannel[0][0])
    else:
        return str(channel_id)


async def msgfilter(message, isobject):
    if isobject:
        contents = message.content
    else:
        contents = message
    if len(contents) > 0:
        blacklist = db.query("SELECT word FROM word_blacklist")
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


async def pickmessage(channel_id):
    dbrequest = db.query(["SELECT user_info, contents FROM message_logs WHERE channel_id = ?", (str(channel_id),)])
    # TODO: break the loops with return instead
    loop = True
    counter = 0
    while loop:
        if counter > 100:
            print("something is wrong. VERY WRONG")
            loop = False
            return None
        counter += 1
        if dbrequest:
            message = random.choice(dbrequest)
            if (await msgfilter(message[1], False) != None) and (await isntbotcheck(message[0])):
                loop = False
                return message[1]
        else:
            print("no messages in specified channel, counted %s times" % (str(counter)))
            loop = False
            return None


async def momijispeak(message):
    channel = message.channel
    channeltouse = int(await bridgecheck(channel.id))
    async with channel.typing():
        messagetosend = await pickmessage(channeltouse)
    if messagetosend:
        responsemsg = await channel.send(messagetosend)
        await cr_pair.pair(message.id, responsemsg.id)
        return True
    else:
        return None


async def spammessage(message):
    counter = 0
    async for previous_message in message.channel.history(limit=2+random.randint(1, 4)):
        if (message.content == previous_message.content) and (message.author.id != previous_message.author.id):
            if message.author.bot:
                counter = -500
            else:
                counter += 1
    if counter == 3:
        filtered = await msgfilter(message.content, False)
        if filtered != None:
            await message.channel.send(filtered)


async def logmessage(message):
    # Please use the data logged through this responsibly
    messageauthorjson = {
        'id': str(message.author.id),
        'username': str(message.author.name),
        'discriminator': str(message.author.discriminator),
        'avatar': str(message.author.avatar),
        'bot': bool(message.author.bot),
    },
    db.query(
        [
            "INSERT INTO message_logs VALUES (?,?,?,?,?,?,?)",
            [
                str(message.guild.id), # for userstats
                str(message.channel.id), # for userstats and so the message can be randomly picked with channel id
                str(message.author.id), # to identify message author when doing userstats
                str(json.dumps(messageauthorjson)), # to identify easily who wrote the message and whether it was a bot or not if the user left the guild
                str(message.id), # maybe in future we can auto delete messages from DB when they are deleted on discord or update them when they are edited
                str(message.content), # duh. Yes, we can get away by just logging message ID, however I actually need contents for what I have planned in future update
                str(int(time.mktime(message.created_at.timetuple()))) # to make userstats day/week/month command to work as intended and not send 1000000 api requests
            ]
        ]
    )


async def on_message(client, message):
    if not message.author.bot:
        msg = message.content.lower()
        if '@everyone' in msg:
            await message.channel.send(file=discord.File('res/pinged.gif'))
        else:
            if 'momiji' in msg:
                await momijispeak(message)
            else:
                await spammessage(message)

                if (
                        (client.user.mention in message.content) or
                        (msg.startswith('...')) or
                        (msg.startswith('omg')) or
                        (msg.startswith('wut')) or
                        (msg.startswith('wat')) or
                        (message.content.isupper() and len(message.content) > 1)
                ):
                    await momijispeak(message)

                # TODO: grab these from db, allow searching by guild
                responsedb = [
                    ["^", "I agree!"],
                    ["gtg", "nooooo don\'t leaveeeee!"],
                    ["kakushi", "kotoga"],
                    ["kasanari", "AAAAAAAAAAAAUUUUUUUUUUUUUUUUU"],
                    ["giri giri", "EYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"],
                    ["awoo", "awoooooooooooooooooooooooooo"],
                    ["cya", "nooooo don\'t leaveeeee!"],
                    ["bad bot", ";w;"],
                    ["stupid bot", ";w;"],
                    ["good bot", "^w^"],
                    ["sentient", "yes ^w^"],
                    ["it is self aware", "yes"],
                ]

                for oneresponse in responsedb:
                    if msg.startswith(oneresponse[0]):
                        responsemsg = await message.channel.send(oneresponse[1])
                        await cr_pair.pair(message.id, responsemsg.id)

                #if ("birthday" in msg or "i turn" in msg) and "today" in msg and "my" in msg:
                #    await message.channel.send('Happy Birthday %s!' % (message.author.mention))
    await logmessage(message)
