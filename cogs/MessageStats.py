from modules import cooldown
from modules import permissions
from modules import wrappers
import time
import discord
from discord.ext import commands
from collections import Counter
import operator


class MessageStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="user_stats", brief="Show user stats", description="", aliases=["userstats"])
    @commands.guild_only()
    async def user_stats(self, ctx, *args):
        if not await cooldown.check(str(ctx.author.id), "last_stat_time", 40):
            if not await permissions.is_admin(ctx):
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
            max_results = 40
            for arg in args:
                if "channel" in arg:
                    scope_key = "channel_id"
                    scope_value = str(ctx.channel.id)
                    if ":" in arg:
                        sub_args = arg.split(":")
                        scope_value = str(sub_args[1])
                if "limit" in arg:
                    if ":" in arg:
                        sub_args = arg.split(":")
                        max_results = int(sub_args[1])

            query_str = f"SELECT user_id FROM mmj_message_logs WHERE {scope_key} = ? AND bot = ? AND timestamp > ?"

            if "all_channels" not in args:
                async with self.bot.db.execute("SELECT * FROM mmj_stats_channel_blacklist") as cursor:
                    no_xp_channel_list = await cursor.fetchall()
                if no_xp_channel_list:
                    for one_no_xp_channel in no_xp_channel_list:
                        query_str += f" AND channel_id != '{one_no_xp_channel[0]}'"

            async with self.bot.db.execute(query_str, [str(scope_value), str("0"), str(after)]) as cursor:
                messages = await cursor.fetchall()

            stats = await self.list_sorter(messages)
            total_amount = len(messages)

            rank = 0
            contents = ""

            async with self.bot.db.execute("SELECT * FROM mmj_private_guilds WHERE guild_id = ?",
                                           [str(ctx.guild.id)]) as cursor:
                guild_privacy_check = await cursor.fetchall()
            if guild_privacy_check:
                contents += "I'm only collecting metadata from this server\n\n"

            for member_id in stats:
                async with self.bot.db.execute("SELECT username FROM mmj_message_logs WHERE user_id = ?",
                                               [str(member_id[0][0])]) as cursor:
                    user_info = await cursor.fetchall()
                member = ctx.guild.get_member(int(member_id[0][0]))
                if not member:
                    member_name = user_info[0][0]
                else:
                    member_name = member.name

                if not str(member_id[0][0]) == "456226577798135808":

                    rank += 1
                    contents += f"**[{rank}]**"
                    contents += " : "

                    contents += f"`{member_name.replace('`', '')}`"
                    contents += " : "

                    if member:
                        if "mention" in args:
                            contents += f"{member.mention}"
                            contents += " : "
                        else:
                            if member.nick:
                                if member.nick != member_name:
                                    contents += f"`{member.nick.replace('`', '')}`"
                                    contents += " : "

                    contents += f"{member_id[1]} msgs"
                    contents += "\n"
                    if rank == max_results:
                        break

            embed = discord.Embed(color=0xffffff)
            embed.set_author(name="User stats")
            embed.set_footer(text=f"Total amount of messages sent: {total_amount}")
        await wrappers.send_large_embed(ctx.channel, embed, contents)

    @commands.command(name="word_stats", brief="Word statistics", description="")
    @commands.check(permissions.is_owner)
    @commands.guild_only()
    async def word_stats(self, ctx, *args):
        async with self.bot.db.execute("SELECT * FROM mmj_private_guilds WHERE guild_id = ?",
                                       [str(ctx.guild.id)]) as cursor:
            is_private_guild = await cursor.fetchall()
        if is_private_guild:
            await ctx.send("impossible to do this in this guild because this is a private area "
                           "and I don\'t store messages from here")
            return None

        async with ctx.channel.typing():
            title = "Here are 40 most used words in server all time:"
            async with self.bot.db.execute("SELECT contents FROM mmj_message_logs WHERE guild_id = ?",
                                           [str(ctx.guild.id)]) as cursor:
                messages = await cursor.fetchall()

            max_results = 40
            for arg in args:
                if "limit" in arg:
                    if ":" in arg:
                        sub_args = arg.split(":")
                        max_results = int(sub_args[1])

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
                    amount = str(word_stat[1]) + " times"
                    contents += f"**[{rank}]** : `{word_stat[0]}` : {amount}\n"
                    if rank == max_results:
                        break

            embed = discord.Embed(color=0xffffff)
            embed.set_author(name="Word stats")
            embed.set_footer(text="Momiji is best wolf.")
        await wrappers.send_large_embed(ctx.channel, embed, contents)

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))


def setup(bot):
    bot.add_cog(MessageStats(bot))
