from modules import permissions
import discord
from discord.ext import commands
import time


class MomijiChannelImporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="init", brief="Initialize in this guild")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def init_server(self, ctx):
        """
        This commands imports all visible channels in this guild and then enables MomijiSpeak
        """

        for channel in ctx.guild.channels:
            if type(channel) is discord.TextChannel:
                await self.import_channel(ctx, channel)

        await self.bot.db.execute("INSERT INTO mmj_enabled_guilds VALUES (?)", [str(ctx.guild.id)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    @commands.command(name="import", brief="Import the chat")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def import_messages(self, ctx, *channel_id_list):
        """
        This command allows importing specific channels
        You can pass in multiple channel IDs to this command.
        """

        for channel_id in channel_id_list:
            if channel_id == "this":
                await self.import_channel(ctx, ctx.channel)
            else:
                await self.import_channel(ctx, self.bot.get_channel(int(channel_id)))

    async def import_channel(self, ctx, channel):
        try:
            # TODO: This is inefficient, fix
            async for message in channel.history(limit=999999999):
                if await self.check_privacy(ctx):
                    content = None
                else:
                    content = str(message.content)
                await self.bot.db.execute("INSERT INTO mmj_message_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                          [str(message.guild.id), str(message.channel.id), str(message.author.id),
                                           str(message.id), str(message.author.name), str(int(message.author.bot)),
                                           content, str(int(time.mktime(message.created_at.timetuple()))), str("0")])
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    async def check_privacy(self, message):
        """
        Checks if the message belongs to a private guild or a channel
        :param message: discord.py's message object
        :return: True if the message belongs to a private guild or a channel, False if not.
        """

        if message.guild:
            async with self.bot.db.execute("SELECT * FROM mmj_private_guilds WHERE guild_id = ?",
                                           [str(message.guild.id)]) as cursor:
                private_guild_check = await cursor.fetchall()
            if private_guild_check:
                return True
        async with self.bot.db.execute("SELECT * FROM mmj_private_channels WHERE channel_id = ?",
                                       [str(message.channel.id)]) as cursor:
            private_channel_check = await cursor.fetchall()
        if private_channel_check:
            return True
        return False


def setup(bot):
    bot.add_cog(MomijiChannelImporting(bot))
