import json
import time
import discord
import asyncio
from collections import Counter
import operator
from modules import cooldown
from modules import dbhandler


async def timeconv(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds) 


async def measuretime(starttime, endtime):
    timeittook = int(endtime - starttime)
    return (await timeconv(timeittook))


async def messagecounter(messageadata):
    results = dict(Counter(messageadata))
    return reversed(sorted(results.items(), key=operator.itemgetter(1)))


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


async def exportjson(client, ctx, channelid: int = None, amount: int = 999999999):
    async with ctx.channel.typing():
        if channelid == None:
            channel = ctx.message.channel
            channelid = ctx.message.channel.id
        else:
            channel = client.get_channel(channelid)
        starttime = time.time()
        log_instance = channel.history(limit=amount)
        exportfilename = "data/export.%s.%s.%s.json" % (str(int(time.time())), str(channelid), str(amount))
        log_file = open(exportfilename, "a", encoding="utf8")
        collection = []
        logcounter = 0
        async for message in log_instance:
            logcounter += 1
            template = {
                'timestamp': str(message.created_at.isoformat()),
                'id': str(message.id),
                'author': {
                    'id': str(message.author.id),
                    'username': str(message.author.name),
                    'discriminator': str(message.author.discriminator),
                    'avatar': str(message.author.avatar),
                    'bot': bool(message.author.bot),
                },
                'content': str(message.content),
            }
            collection.append(template)
        log_file.write(json.dumps(collection, indent=4, sort_keys=True))
        endtime = time.time()
        exportembed = discord.Embed(color=0xadff2f)
        exportembed.set_author(
            name="Exporting finished", 
            url='https://github.com/Kyuunex/Momiji'
        )
        exportembed.add_field(
            name="Exported to:",
            value=exportfilename, 
            inline=False
        )
        exportembed.add_field(
            name="Channel:", 
            value=channel.name, 
            inline=False
        )
        exportembed.add_field(
            name="Number of messages:",
            value=logcounter, 
            inline=False
        )
        exportembed.add_field(name="Time taken while exporting:", value=await measuretime(starttime, endtime), inline=False)
    await ctx.send(embed=exportembed)

async def importmessages(client, ctx, channelids):
    for channelid in channelids:
        try:
            if channelid == "this":
                channel = ctx.message.channel
                channelid = ctx.message.channel.id
            else:
                channel = client.get_channel(int(channelid))
            starttime = time.time()
            log_instance = channel.history(limit=999999999)
            logcounter = 0
            whattocommit = []
            async for message in log_instance:
                logcounter += 1
                messageauthorjson = {
                    'id': str(message.author.id),
                    'username': str(message.author.name),
                    'discriminator': str(message.author.discriminator),
                    'avatar': str(message.author.avatar),
                    'bot': bool(message.author.bot),
                },
                whattocommit.append(
                    [
                        "INSERT INTO channellogs VALUES (?,?,?,?,?,?,?)",
                        [
                            str(message.guild.id),
                            str(message.channel.id),
                            str(message.author.id),
                            str(json.dumps(messageauthorjson)),
                            str(message.id),
                            str(message.content),
                            str(int(time.mktime(message.created_at.timetuple())))
                        ]
                    ]
                )
            await dbhandler.massquery(whattocommit)
            endtime = time.time()
            exportembed = discord.Embed(
                color=0xadff2f, description="Imported the channel into database.")
            exportembed.set_author(
                name="Importing finished", url='https://github.com/Kyuunex/Momiji')
            exportembed.add_field(
                name="Channel:", value=channel.name, inline=False)
            exportembed.add_field(
                name="Number of messages:", value=logcounter, inline=False)
            exportembed.add_field(name="Time taken while importing:", value=await measuretime(starttime, endtime), inline=False)
            await ctx.send(embed=exportembed)
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in importmessages")
            print(e)


async def bridge(client, ctx, bridgetype, value):
    if len(value) > 0:
        bridgedchannel = await dbhandler.query(["SELECT value FROM bridges WHERE channelid = ?", [str(ctx.message.channel.id)]])
        if not bridgedchannel:
            await dbhandler.query(["INSERT INTO bridges VALUES (?, ?, ?)", [str(ctx.message.channel.id), str(bridgetype), str(value)]])
            await ctx.send("`The bridge was created`")
        else:
            await ctx.send("`This channel is already bridged`")


async def userstats(client, ctx, where, arg):
    if await cooldown.check(str(ctx.author.id), 'laststattime', 40):
        async with ctx.channel.typing():
            if "channel" in where:
                wherekey = "channelid"
                if ":" in where:
                    wherevalue = str((where.split(':'))[1])
                    wherereadable = "<#%s>" % (wherevalue)
                else:
                    wherevalue = str(ctx.message.channel.id)
                    wherereadable = "this channel"
            else:
                wherekey = "guildid"
                wherevalue = str(ctx.message.guild.id)
                wherereadable = "this server"

            if arg == "month":  # 2592000
                title = "Here are 40 most active people in %s in last 30 days:" % (wherereadable)
                after = int(time.time()) - 2592000
                query = ["SELECT userid FROM channellogs WHERE %s = ? AND timestamp > ?;" % (wherekey), (wherevalue, str(after))]
                messages = await dbhandler.query(query)
            elif arg == "week":  # 604800
                title = "Here are 40 most active people in %s in last 7 days:" % (wherereadable)
                after = int(time.time()) - 604800
                query = ["SELECT userid FROM channellogs WHERE %s = ? AND timestamp > ?;" % (wherekey), (wherevalue, str(after))]
                messages = await dbhandler.query(query)
            elif arg == "day":  # 86400
                title = "Here are 40 most active people in %s in last 24 hours:" % (wherereadable)
                after = int(time.time()) - 86400
                query = ["SELECT userid FROM channellogs WHERE %s = ? AND timestamp > ?;" % (wherekey), (wherevalue, str(after))]
                messages = await dbhandler.query(query)
            else:
                title = "Here are 40 most active people in %s all time:" % (wherereadable)
                query = ["SELECT userid FROM channellogs WHERE %s = ?;" % (wherekey), (wherevalue,)]
                messages = await dbhandler.query(query)

            stats = await messagecounter(messages)

            rank = 0
            contents = title + "\n\n"

            for onemember in stats:
                memberobject = ctx.guild.get_member(int(onemember[0][0]))
                if not memberobject:
                    memberobject = client.get_user(int(onemember[0][0]))
                    if not memberobject:
                        userjson = await dbhandler.query(["SELECT userjson FROM channellogs WHERE userid = ?;", [str(onemember[0][0])]])
                        memberobject = json_to_user(userjson[0][0])
                        notice = " **(User not found)** "
                    else:
                        notice = " **(User left)** "
                else:
                    notice = ""

                messageamount = str(onemember[1])+" msgs"

                if not memberobject.bot:
                    try:
                        if memberobject.nick:
                            notice = " ("+memberobject.nick+") "
                    except:
                        print(memberobject.name+" broken nickname")
                    rank += 1
                    if memberobject.name == "Deleted User":
                        name = memberobject.id
                        notice = " **(Deleted User)** "
                    else:
                        name = memberobject.name
                    contents += "**[%s]** : %s%s : %s\n" % (rank, name, notice, messageamount)
                    if rank == 40:
                        break

            statsembed = discord.Embed(description=contents, color=0xffffff)
            statsembed.set_author(name="User stats")
            statsembed.set_footer(text="Momiji is best wolf.")
        await ctx.send(embed=statsembed)
    else:
        await ctx.send('slow down bruh')


async def wordstats(client, ctx, arg = None):
    if await cooldown.check(str(ctx.author.id), 'laststattime', 40):
        async with ctx.channel.typing():
            title = "Here are 40 most used words in server all time:"
            messages = await dbhandler.query(["SELECT contents FROM channellogs WHERE guildid = ?;", [str(ctx.guild.id),]])

            individualwords = []
            for message in messages:
                for oneword in (message[0]).split(" "):
                    individualwords.append(oneword.replace("`","").lower())

            stats = await messagecounter(individualwords)

            rank = 0
            contents = title + "\n\n"
            if arg:
                blacklist = [
                    "", "i", "the", "a", "to", "is", "it", "you", "and", "that", "in", "like", "this", "of", "just", "my", "but", "not", "no", "me", "have", "can", "so", "if", "do", "on", "are", "be", "u", "what", "with", "has", "-", "was", "it's", "im",
                ]
            else:
                blacklist = [
                    "",
                ]

            for wordstat in stats:
                if not (any(c == wordstat[0] for c in blacklist)):
                    rank += 1
                    amount = str(wordstat[1])+" times"
                    contents += "**[%s]** : `%s` : %s\n" % (rank, wordstat[0], amount)
                    if rank == 40:
                        break

            statsembed = discord.Embed(description=contents, color=0xffffff)
            statsembed.set_author(name="Word stats")
            statsembed.set_footer(text="Momiji is best wolf.")
        await ctx.send(embed=statsembed)
    else:
        await ctx.send('slow down bruh')


async def regulars(ctx):
    guildregularsrole = await dbhandler.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guildregularsrole", str(ctx.guild.id)]])
    if guildregularsrole:
        async with ctx.channel.typing():
            regularsrole = discord.utils.get(
                ctx.guild.roles, id=int(guildregularsrole[0][0]))

            for member in regularsrole.members:
                await member.remove_roles(regularsrole, reason="pruned role")

            after = int(time.time()) - 2592000
            query = ["SELECT userid FROM channellogs WHERE guildid = ? AND timestamp > ?;", (str(ctx.guild.id), str(after))]
            messages = await dbhandler.query(query)

            stats = await messagecounter(messages)

            rank = 0
            for onemember in stats:
                memberobject = ctx.guild.get_member(int(onemember[0][0]))
                if memberobject:
                    if not memberobject.bot:
                        rank += 1
                        try:
                            await memberobject.add_roles(regularsrole)
                        except Exception as e:
                            print(e)
                        if rank == int(guildregularsrole[0][1]):
                            break
        await ctx.send("Done")
    else:
        await ctx.send("This server has no Regular role configured in my database")