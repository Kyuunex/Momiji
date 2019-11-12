from modules import db
from modules import cooldown
from modules import permissions
import time
import discord
from discord.ext import commands
from collections import Counter
import operator


class MessageStats(commands.Cog, name="MessageStats"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userstats", brief="Show user stats", description="")
    @commands.guild_only()
    async def user_stats(self, ctx, where: str = "server", arg: str = None, allchannels=None):
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
                    query = ["SELECT user_id FROM mmj_message_logs WHERE %s = ? AND timestamp > ?" % (wherekey), (wherevalue, str(after))]
                elif arg == "week":  # 604800
                    title = "Here are 40 most active people in %s in last 7 days:" % (wherereadable)
                    after = int(time.time()) - 604800
                    query = ["SELECT user_id FROM mmj_message_logs WHERE %s = ? AND timestamp > ?" % (wherekey), (wherevalue, str(after))]
                elif arg == "day":  # 86400
                    title = "Here are 40 most active people in %s in last 24 hours:" % (wherereadable)
                    after = int(time.time()) - 86400
                    query = ["SELECT user_id FROM mmj_message_logs WHERE %s = ? AND timestamp > ?" % (wherekey), (wherevalue, str(after))]
                else:
                    title = "Here are 40 most active people in %s all time:" % (wherereadable)
                    query = ["SELECT user_id FROM mmj_message_logs WHERE %s = ?" % (wherekey), (wherevalue,)]
                    
                if not allchannels:
                    no_xp_channel_list = db.query("SELECT * FROM mmj_stats_channel_blacklist")
                    if no_xp_channel_list:
                        for one_no_xp_channel in no_xp_channel_list:
                            query[0] += " AND channel_id != '%s'" % (str(one_no_xp_channel[0]))

                messages = db.query(query)

                stats = await self.list_sorter(messages)
                totalamount = len(messages)

                rank = 0
                contents = title + "\n\n"

                for onemember in stats:
                    user_info = db.query(["SELECT username,bot FROM mmj_message_logs WHERE user_id = ?;", [str(onemember[0][0])]])
                    memberobject = ctx.guild.get_member(int(onemember[0][0]))
                    if not memberobject:
                        one_member_name = user_info[0][0]
                    else:
                        one_member_name = memberobject.name

                    if not bool(int(user_info[0][1])) and not one_member_name == "Deleted User":

                        rank += 1
                        contents += "**[%s]**" % (rank)
                        contents += " : "

                        contents += "`%s`" % (one_member_name)
                        contents += " : "

                        if memberobject:
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

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))


    @commands.command(name="wordstats", brief="Word statistics", description="")
    @commands.check(permissions.is_owner)
    @commands.guild_only()
    async def wordstats(self, ctx, arg=None):
        if await cooldown.check(str(ctx.author.id), 'laststattime', 40):
            if (not db.query(["SELECT * FROM mmj_private_areas WHERE id = ?", [str(ctx.guild.id)]])):
                async with ctx.channel.typing():
                    title = "Here are 40 most used words in server all time:"
                    messages = db.query(["SELECT contents FROM mmj_message_logs WHERE guild_id = ?;", [str(ctx.guild.id),]])

                    individualwords = []
                    for message in messages:
                        for oneword in (message[0]).split(" "):
                            individualwords.append(oneword.replace("`","").lower())

                    stats = await self.list_sorter(individualwords)

                    rank = 0
                    contents = title + "\n\n"
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
                await ctx.send('impossible to do this in this guild because this is a private area and I don\'t store messages from here')
        else:
            await ctx.send('slow down bruh')


def setup(bot):
    bot.add_cog(MessageStats(bot))