from modules import db
from modules import cooldown
from modules import permissions
import time
import discord
from discord.ext import commands
from collections import Counter
import operator


class MessageStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userstats", brief="Show user stats", description="")
    @commands.guild_only()
    async def user_stats(self, ctx, *args):
        if not await cooldown.check(str(ctx.author.id), "last_stat_time", 40):
            if not await permissions.is_owner(ctx):
                await ctx.send("slow down bruh")
                return None

        async with ctx.channel.typing():
            if "month" in args:
                after = int(time.time()) - 2592000
            elif "week" in args:
                after = int(time.time()) - 604800
            elif "day" in args:
                after = int(time.time()) - 86400
            else:
                after = 0

            scope_key = "guild_id"
            scope_value = str(ctx.guild.id)
            for arg in args:
                if "channel" in arg:
                    scope_key = "channel_id"
                    scope_value = str(ctx.channel.id)
                    if ":" in arg:
                        sub_args = arg.split(":")
                        scope_value = str(sub_args[1])

            query = ["SELECT user_id FROM mmj_message_logs "
                     f"WHERE {scope_key} = ? AND bot = ? AND timestamp > ?",
                     [str(scope_value), str("0"), str(after)]]

            if "all_channels" not in args:
                no_xp_channel_list = db.query("SELECT * FROM mmj_stats_channel_blacklist")
                if no_xp_channel_list:
                    for one_no_xp_channel in no_xp_channel_list:
                        query[0] += f" AND channel_id != '{one_no_xp_channel[0]}'"

            messages = db.query(query)

            stats = await self.list_sorter(messages)
            total_amount = len(messages)

            rank = 0
            contents = ""

            for member_id in stats:
                user_info = db.query(["SELECT username FROM mmj_message_logs WHERE user_id = ?",
                                      [str(member_id[0][0])]])
                member = ctx.guild.get_member(int(member_id[0][0]))
                if not member:
                    member_name = user_info[0][0]
                else:
                    member_name = member.name

                if not str(member_id[0][0]) == "456226577798135808":

                    rank += 1
                    contents += f"**[{rank}]**"
                    contents += " : "

                    contents += f"`{member_name}`"
                    contents += " : "

                    if member:
                        if member.nick:
                            if member.nick != member_name:
                                contents += f"`{member.nick}`"
                                contents += " : "

                    contents += f"{member_id[1]} msgs"
                    contents += "\n"
                    if rank == 40:
                        break

            embed = discord.Embed(description=contents, color=0xffffff)
            embed.set_author(name="User stats")
            embed.set_footer(text=f"Total amount of messages sent: {total_amount}")
        await ctx.send(embed=embed)

    @commands.command(name="word_stats", brief="Word statistics", description="")
    @commands.check(permissions.is_owner)
    @commands.guild_only()
    async def word_stats(self, ctx):
        if db.query(["SELECT * FROM mmj_private_guilds WHERE guild_id = ?", [str(ctx.guild.id)]]):
            await ctx.send("impossible to do this in this guild because this is a private area "
                           "and I don\'t store messages from here")
            return None

        async with ctx.channel.typing():
            title = "Here are 40 most used words in server all time:"
            messages = db.query(["SELECT contents FROM mmj_message_logs WHERE guild_id = ?", [str(ctx.guild.id)]])

            individual_words = []
            for message in messages:
                for one_word in (message[0]).split(" "):
                    individual_words.append(one_word.replace("`", "").lower())

            stats = await self.list_sorter(individual_words)

            rank = 0
            contents = title + "\n\n"
            blacklist = [
                "",
            ]

            for word_stat in stats:
                if not (any(c == word_stat[0] for c in blacklist)):
                    rank += 1
                    amount = str(word_stat[1])+" times"
                    contents += f"**[{rank}]** : `{word_stat[0]}` : {amount}\n"
                    if rank == 40:
                        break

            embed = discord.Embed(description=contents, color=0xffffff)
            embed.set_author(name="Word stats")
            embed.set_footer(text="Momiji is best wolf.")
        await ctx.send(embed=embed)

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))

def setup(bot):
    bot.add_cog(MessageStats(bot))
