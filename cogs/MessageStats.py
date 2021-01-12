from modules import cooldown
from modules import permissions
from reusables import send_large_message
import time
import discord
from discord.ext import commands
from collections import Counter
import operator
from discord.utils import escape_markdown


class MessageStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="user_stats", brief="Show user stats", aliases=["userstats"])
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def user_stats(self, ctx, *args):
        """
        This command uses the message metadata stored in the database
        to calculate which members are active in given timescale/channel and etc.

        Passable arguments:
        month, week, day
        channel:channel_id
        limit:40
        """

        if not await cooldown.check(str(ctx.author.id), "last_stat_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return

        async with self.bot.db.execute("SELECT guild_id FROM mmj_enabled_guilds WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            is_enabled_guild = await cursor.fetchall()
        if not is_enabled_guild:
            await ctx.send("MomijiSpeak is not enabled in this guild.")
            return

        async with ctx.channel.typing():
            after = await self.parse_args_timescale(args)

            scope_key = "guild_id"
            scope_value = int(ctx.guild.id)
            max_results = 40
            for arg in args:
                if "channel" in arg:
                    scope_key = "channel_id"
                    scope_value = int(ctx.channel.id)
                    if ":" in arg:
                        sub_args = arg.split(":")
                        scope_value = int(sub_args[1])
                if "limit" in arg:
                    if ":" in arg:
                        sub_args = arg.split(":")
                        max_results = int(sub_args[1])

            query_str = f"SELECT user_id FROM mmj_message_logs WHERE {scope_key} = ? AND bot = ? AND timestamp > ?"

            if "all_channels" not in args:
                async with self.bot.db.execute("SELECT channel_id FROM mmj_stats_channel_blacklist") as cursor:
                    no_xp_channel_list = await cursor.fetchall()
                if no_xp_channel_list:
                    for one_no_xp_channel in no_xp_channel_list:
                        query_str += f" AND channel_id != {one_no_xp_channel[0]}"

            async with self.bot.db.execute(query_str, [int(scope_value), 0, int(after)]) as cursor:
                messages = await cursor.fetchall()

            stats = await self.list_sorter(messages)
            total_amount = len(messages)

            rank = 0
            contents = ""

            async with self.bot.db.execute("SELECT guild_id FROM mmj_private_guilds WHERE guild_id = ?",
                                           [int(ctx.guild.id)]) as cursor:
                guild_privacy_check = await cursor.fetchall()
            if guild_privacy_check:
                contents += "I'm only collecting metadata from this server\n\n"

            for member_id in stats:
                member = ctx.guild.get_member(int(member_id[0][0]))
                if not member:
                    async with self.bot.db.execute("SELECT username FROM mmj_message_logs "
                                                   "WHERE user_id = ? ORDER BY timestamp DESC",
                                                   [int(member_id[0][0])]) as cursor:
                        user_info = await cursor.fetchone()
                    member_name = user_info[0]
                else:
                    member_name = member.name

                if not int(member_id[0][0]) == 456226577798135808:

                    rank += 1
                    if not member:
                        contents += f"~~"
                    contents += f"**[{rank}]**"
                    contents += " : "

                    contents += f"{escape_markdown(member_name)}"
                    contents += " : "

                    if "show_id" in args:
                        contents += f"`{member_id[0][0]}`"
                        contents += " : "

                    if member:
                        if "mention" in args:
                            contents += f"{member.mention}"
                            contents += " : "
                        else:
                            if member.nick:
                                if member.nick != member_name:
                                    contents += f"{escape_markdown(member.nick)}"
                                    contents += " : "

                    contents += f"{member_id[1]} msgs"
                    if not member:
                        contents += f"~~"
                    contents += "\n"
                    if rank == max_results:
                        break

            embed = discord.Embed(color=0xffffff)
            embed.set_author(name="User stats")
            embed.set_footer(text=f"Total amount of messages sent: {total_amount}")
        await send_large_message.send_large_embed(ctx.channel, embed, contents)

    async def parse_args_timescale(self, args):
        for arg in args:
            if "months:" in arg:
                sub_args = arg.split(":")
                scope_value = int(sub_args[1])
                return int(time.time()) - (2592000 * scope_value)
            elif "month" in arg:
                return int(time.time()) - 2592000
            elif "weeks:" in arg:
                sub_args = arg.split(":")
                scope_value = int(sub_args[1])
                return int(time.time()) - (604800 * scope_value)
            elif "week" in arg:
                return int(time.time()) - 604800
            elif "days:" in arg:
                sub_args = arg.split(":")
                scope_value = int(sub_args[1])
                return int(time.time()) - (86400 * scope_value)
            elif "day" in arg:
                return int(time.time()) - 86400
        return 0

    @commands.command(name="word_stats", brief="Word statistics")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def word_stats(self, ctx, *args):
        """
        Show what are the most popular words spoken in this server.
        """

        async with self.bot.db.execute("SELECT guild_id FROM mmj_private_guilds WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            is_private_guild = await cursor.fetchall()
        if is_private_guild:
            await ctx.send("impossible to do this in this guild because this is a private area "
                           "and I don\'t store messages from here")
            return

        async with self.bot.db.execute("SELECT guild_id FROM mmj_enabled_guilds WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            is_enabled_guild = await cursor.fetchall()
        if not is_enabled_guild:
            await ctx.send("MomijiSpeak is not enabled in this guild.")
            return

        async with ctx.channel.typing():
            max_results = 40
            for arg in args:
                if "limit" in arg:
                    if ":" in arg:
                        sub_args = arg.split(":")
                        max_results = int(sub_args[1])

            title = f"Here are {max_results} most used words in server all time:"
            async with self.bot.db.execute("SELECT contents FROM mmj_message_logs WHERE guild_id = ?",
                                           [int(ctx.guild.id)]) as cursor:
                messages = await cursor.fetchall()

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
        await send_large_message.send_large_embed(ctx.channel, embed, contents)

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))


def setup(bot):
    bot.add_cog(MessageStats(bot))
