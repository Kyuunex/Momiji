import json
import time
import discord
from modules import utils
from modules import dbhandler

async def exportjson(client, ctx, channelid: int = None, amount: int = 999999999):
    if channelid == None:
        channel = ctx.message.channel
        channelid = ctx.message.channel.id
    else:
        channel = client.get_channel(channelid)
    starttime = time.process_time()
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
    endtime = time.process_time()
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
    exportembed.add_field(name="Time taken while exporting:", value=await utils.measuretime(starttime, endtime), inline=False)
    await ctx.send(embed=exportembed)

async def importmessages(client, ctx, channelids):
    for channelid in channelids:
        try:
            if channelid == "this":
                channel = ctx.message.channel
                channelid = ctx.message.channel.id
            else:
                channel = client.get_channel(int(channelid))
            starttime = time.process_time()
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
            endtime = time.process_time()
            exportembed = discord.Embed(
                color=0xadff2f, description="Imported the channel into database.")
            exportembed.set_author(
                name="Importing finished", url='https://github.com/Kyuunex/Momiji')
            exportembed.add_field(
                name="Channel:", value=channel.name, inline=False)
            exportembed.add_field(
                name="Number of messages:", value=logcounter, inline=False)
            exportembed.add_field(name="Time taken while importing:", value=await utils.measuretime(starttime, endtime), inline=False)
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
    if await utils.cooldowncheck('laststatstime', 20):
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

        stats = await utils.messagecounter(messages)

        rank = 0
        contents = title + "\n\n"

        for onemember in stats:
            memberobject = ctx.guild.get_member(int(onemember[0][0]))
            if not memberobject:
                memberobject = client.get_user(int(onemember[0][0]))
                if not memberobject:
                    userjson = await dbhandler.query(["SELECT userjson FROM channellogs WHERE userid = ?;", [str(onemember[0][0])]])
                    memberobject = utils.json_to_user(userjson[0][0])
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