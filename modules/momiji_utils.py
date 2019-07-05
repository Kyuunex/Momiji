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
    def __init__(self, user_info):
        jsondict = json.loads(user_info)
        self.id = jsondict[0]['id']
        self.discriminator = jsondict[0]['discriminator']
        self.avatar = jsondict[0]['avatar']
        self.name = jsondict[0]['username']
        self.nick = "User Left"
        if jsondict[0]['bot'] == True:
            self.bot = True
        elif jsondict[0]['bot'] == False:
            self.bot = False


async def exportjson(client, ctx, channel_id: int = None, amount: int = 999999999):
    async with ctx.channel.typing():
        if channel_id == None:
            channel = ctx.message.channel
            channel_id = ctx.message.channel.id
        else:
            channel = client.get_channel(channel_id)
        starttime = time.time()
        log_instance = channel.history(limit=amount)
        exportfilename = "data/export.%s.%s.%s.json" % (str(int(time.time())), str(channel_id), str(amount))
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

async def importmessages(client, ctx, channel_id_list):
    for channel_id in channel_id_list:
        if channel_id == "this":
            await import_channel(ctx, ctx.message.channel)
        elif channel_id == "server":
            for channel in ctx.guild.channels:
                if type(channel) is discord.TextChannel:
                    await import_channel(ctx, channel)
            await ctx.send("Finished importing everything")
        else:
            await import_channel(ctx, client.get_channel(int(channel_id)))
            

async def import_channel(ctx, channel):
    try:
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
                    "INSERT INTO message_logs VALUES (?,?,?,?,?,?,?)",
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
        importfinished = "Finished importing %s messages from %s. This took %s." % (logcounter, channel.mention, await measuretime(starttime, endtime))
        await ctx.send(importfinished)
    except Exception as e:
        print(e)


async def bridge(client, ctx, bridgetype, value):
    if len(value) > 0:
        bridgedchannel = await dbhandler.query(["SELECT value FROM bridges WHERE channel_id = ?", [str(ctx.message.channel.id)]])
        if not bridgedchannel:
            await dbhandler.query(["INSERT INTO bridges VALUES (?, ?, ?)", [str(ctx.message.channel.id), str(bridgetype), str(value)]])
            await ctx.send("`The bridge was created`")
        else:
            await ctx.send("`This channel is already bridged`")


async def userstats(client, ctx, where, arg, allchannels):
    if await cooldown.check(str(ctx.author.id), 'laststattime', 40):
        async with ctx.channel.typing():
            if "channel" in where:
                wherekey = "channel_id"
                if ":" in where:
                    wherevalue = str((where.split(':'))[1])
                    wherereadable = "<#%s>" % (wherevalue)
                else:
                    wherevalue = str(ctx.message.channel.id)
                    wherereadable = "this channel"
            else:
                wherekey = "guild_id"
                wherevalue = str(ctx.message.guild.id)
                wherereadable = "this server"

            if arg == "month":  # 2592000
                title = "Here are 40 most active people in %s in last 30 days:" % (wherereadable)
                after = int(time.time()) - 2592000
                query = ["SELECT user_id FROM message_logs WHERE %s = ? AND timestamp > ?" % (wherekey), (wherevalue, str(after))]
            elif arg == "week":  # 604800
                title = "Here are 40 most active people in %s in last 7 days:" % (wherereadable)
                after = int(time.time()) - 604800
                query = ["SELECT user_id FROM message_logs WHERE %s = ? AND timestamp > ?" % (wherekey), (wherevalue, str(after))]
            elif arg == "day":  # 86400
                title = "Here are 40 most active people in %s in last 24 hours:" % (wherereadable)
                after = int(time.time()) - 86400
                query = ["SELECT user_id FROM message_logs WHERE %s = ? AND timestamp > ?" % (wherekey), (wherevalue, str(after))]
            else:
                title = "Here are 40 most active people in %s all time:" % (wherereadable)
                query = ["SELECT user_id FROM message_logs WHERE %s = ?" % (wherekey), (wherevalue,)]
                
            if not allchannels:
                no_xp_channel_list = await dbhandler.query("SELECT * FROM stats_channel_blacklist")
                if no_xp_channel_list:
                    for one_no_xp_channel in no_xp_channel_list:
                        query[0] += " AND channel_id != '%s'" % (str(one_no_xp_channel[0]))

            messages = await dbhandler.query(query)

            stats = await messagecounter(messages)
            totalamount = len(messages)

            rank = 0
            contents = title + "\n\n"

            for onemember in stats:
                memberobject = ctx.guild.get_member(int(onemember[0][0]))
                if not memberobject:
                    user_info = await dbhandler.query(["SELECT user_info FROM message_logs WHERE user_id = ?;", [str(onemember[0][0])]])
                    memberobject = json_to_user(user_info[0][0])

                if not memberobject.bot and not memberobject.name == "Deleted User":

                    rank += 1
                    contents += "**[%s]**" % (rank)
                    contents += " : "

                    if memberobject.name == "Deleted User":
                        contents += "Deleted User: `%s`" % (memberobject.id)
                    else:
                        contents += "`%s`" % (memberobject.name)
                    contents += " : "

                    if memberobject.nick:
                        contents += "`%s`" % (memberobject.nick)
                        contents += " : "

                    contents += "%s msgs" % (str(onemember[1]))
                    contents += "\n"
                    if rank == 40:
                        break

            statsembed = discord.Embed(description=contents, color=0xffffff)
            statsembed.set_author(name="User stats")
            statsembed.set_footer(text="Total amount of messages sent: %s" %(totalamount))
        await ctx.send(embed=statsembed)
    else:
        await ctx.send('slow down bruh')


async def wordstats(client, ctx, arg = None):
    if await cooldown.check(str(ctx.author.id), 'laststattime', 40):
        async with ctx.channel.typing():
            title = "Here are 40 most used words in server all time:"
            messages = await dbhandler.query(["SELECT contents FROM message_logs WHERE guild_id = ?;", [str(ctx.guild.id),]])

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


async def print_role(ctx, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        output = "```\n"
        for member in role.members:
            output += "%s\n" % (member.display_name)
        output += "```\n"
        output += "Total: %s\n" % (len(role.members))
        output += "Role ID: %s\n" % (role.id)
        await ctx.send(output)
    else:
        await ctx.send("Role not found")


async def about_member(ctx, user_id):
    if user_id:
        member = ctx.guild.get_member(int(user_id))
    else:
        member = ctx.author
    output = "name: %s\n" % (str(member.name))
    output = "display_name: %s\n" % (str(member.display_name))
    output += "joined_at: %s\n" % (str(member.joined_at))
    output += "premium_since: %s\n" % (str(member.premium_since))
    output += "mobile_status: %s\n" % (str(member.mobile_status))
    output += "desktop_status: %s\n" % (str(member.desktop_status))
    output += "web_status: %s\n" % (str(member.web_status))
    output += "created_at: %s\n" % (str(member.created_at))
    # profile = member.profile()
    # output += "nitro: %s\n" % (str(profile.nitro))
    # output += "staff: %s\n" % (str(profile.staff))
    # output += "partner: %s\n" % (str(profile.partner))
    # output += "bug_hunter: %s\n" % (str(profile.bug_hunter))
    # output += "early_supporter: %s\n" % (str(profile.early_supporter))
    # output += "hypesquad: %s\n" % (str(profile.hypesquad))

    await ctx.send(output)


async def about_guild(ctx):
    guild = ctx.guild
    output = "name: %s\n" % (str(guild.name))
    output = "region: %s\n" % (str(guild.region))
    output += "id: %s\n" % (str(guild.id))
    output += "owner_id: %s\n" % (str(guild.owner_id))
    output += "max_presences: %s\n" % (str(guild.max_presences))
    output += "max_members: %s\n" % (str(guild.max_members))
    output += "verification_level: %s\n" % (str(guild.verification_level))
    output += "premium_tier: %s\n" % (str(guild.premium_tier))
    output += "premium_subscription_count: %s\n" % (str(guild.premium_subscription_count))
    output += "filesize_limit: %s\n" % (str(guild.filesize_limit))
    output += "created_at: %s\n" % (str(guild.created_at))
    await ctx.send(output)


async def regulars(ctx):
    # TODO: Make this more efficient, only apply changes, don't clear the role.
    guild_regular_role = await dbhandler.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guild_regular_role", str(ctx.guild.id)]])
    if guild_regular_role:
        async with ctx.channel.typing():
            regularsrole = discord.utils.get(
                ctx.guild.roles, id=int(guild_regular_role[0][0]))

            for member in regularsrole.members:
                await member.remove_roles(regularsrole, reason="pruned role")

            after = int(time.time()) - 2592000
            query = ["SELECT user_id FROM message_logs WHERE guild_id = ? AND timestamp > ?", (str(ctx.guild.id), str(after))]

            no_xp_channel_list = await dbhandler.query("SELECT * FROM stats_channel_blacklist")
            if no_xp_channel_list:
                for one_no_xp_channel in no_xp_channel_list:
                    query[0] += " AND channel_id != '%s'" % (str(one_no_xp_channel[0]))

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
                        if rank == int(guild_regular_role[0][1]):
                            break
        await ctx.send("Done")
    else:
        await ctx.send("This server has no Regular role configured in my database")


async def regulars_role_management(ctx, action, rolename, amount):
    role = discord.utils.get(ctx.guild.roles, name=rolename)
    if role:
        if action == "add":
            await dbhandler.query(["INSERT INTO config VALUES (?,?,?,?)", ["guild_regular_role", str(ctx.guild.id), str(role.id), str(amount)]])
            await ctx.send("%s role is now regulars role with top %s getting the role" % (role.name, amount))
        elif action == "remove":
            await dbhandler.query(["DELETE FROM config WHERE guild_id = ? AND setting = ? AND role_id = ?", [str(ctx.guild.id), "guild_regular_role", str(role.id)]])
            await ctx.send("%s is no longer the regulars role" % (role.name))
        else:
            await regulars(ctx)


async def on_message_delete(client, message):
    await dbhandler.query(["DELETE FROM message_logs WHERE message_id = ?", [str(message.id)]])


async def on_message_edit(client, before, after):
    await dbhandler.query(["UPDATE message_logs SET contents = ? WHERE message_id = ?", [str(after.content), str(after.id)]])