from discord.ext import commands
import discord
from modules import permissions
from modules import wrappers


class WastelandConfiguration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wasteland_ignore_channel", brief="Ignore audit logging for this channel")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def wasteland_ignore_channel(self, ctx):
        """
        Blacklist the current channel from being included in wasteland logs.
        """

        await self.bot.db.execute("INSERT INTO wasteland_ignore_channels VALUES (?, ?)",
                                  [str(ctx.guild.id), str(ctx.channel.id)])
        await self.bot.db.commit()
        await ctx.send(":ok_hand:")

    @commands.command(name="wasteland_ignore_user", brief="Ignore audit logging for a set user")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def wasteland_ignore_user(self, ctx, user_id):
        """
        Blacklist a user from being included in wasteland logs.
        """

        await self.bot.db.execute("INSERT INTO wasteland_ignore_users VALUES (?, ?)",
                                  [str(ctx.guild.id), str(user_id)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    @commands.command(name="set_wasteland_channel", brief="Set a wasteland message")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def set_wasteland_channel(self, ctx):
        """
        Set the channel the message is being called in as a wasteland channel.
        """

        await self.bot.db.execute("INSERT INTO wasteland_channels VALUES (?,?)",
                                  [str(ctx.guild.id), str(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.send("This channel is now a wasteland channel.")

    @commands.command(name="remove_wasteland_channel", brief="Remove a wasteland channel")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def remove_wasteland_channel(self, ctx, *args):
        """
        Remove the current channel from being a wasteland channel.
        """

        if "guild" in args:
            await self.bot.db.execute("DELETE FROM wasteland_channels WHERE guild_id = ?", [str(ctx.guild.id)])
            await ctx.send("If this server had a wasteland channel, there are none now.")
        else:
            await self.bot.db.execute("DELETE FROM wasteland_channels WHERE channel_id = ?", [str(ctx.channel.id)])
            await ctx.send("If this channel was a wasteland channel, it is not more.")
        await self.bot.db.commit()

    @commands.command(name="get_wasteland_channels", brief="Get all wasteland channels")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def get_welcome_messages(self, ctx):
        """
        Prints out all wasteland channels in this guild.
        """

        async with self.bot.db.execute("SELECT channel_id FROM wasteland_channels WHERE guild_id = ?",
                                       [str(ctx.guild.id)]) as cursor:
            wasteland_channels = await cursor.fetchall()

        buffer = ":wastebasket: **Wasteland channels in this server.**\n\n"

        if wasteland_channels:
            for one_wasteland_channel in wasteland_channels:
                buffer += f"<#{one_wasteland_channel[0]}>\n"
        else:
            buffer += "**There are no wasteland channels in this server.**\n"

        embed = discord.Embed(color=0xf76a8c)

        await wrappers.send_large_embed(ctx.channel, embed, buffer)


def setup(bot):
    bot.add_cog(WastelandConfiguration(bot))
