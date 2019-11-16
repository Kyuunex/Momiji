from modules import db
from modules import permissions
import discord
from discord.ext import commands
import time


class MomijiChannelImporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="init", brief="Initialize in this guild", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def init_server(self, ctx):
        for channel in ctx.guild.channels:
            if type(channel) is discord.TextChannel:
                await self.import_one_channel(ctx, channel)
        await ctx.send(":ok_hand:")

    @commands.command(name="import", brief="Import the chat", description="Imports stuff")
    @commands.check(permissions.is_admin)
    async def import_messages(self, ctx, *channel_id_list):
        for channel_id in channel_id_list:
            if channel_id == "this":
                await self.import_one_channel(ctx, ctx.message.channel)
            elif channel_id == "server":
                for channel in ctx.guild.channels:
                    if type(channel) is discord.TextChannel:
                        await self.import_one_channel(ctx, channel)
                await ctx.send(":ok_hand:")
            else:
                await self.import_one_channel(ctx, self.bot.get_channel(int(channel_id)))

    async def import_one_channel(self, ctx, channel):
        try:
            #starttime = time.time()
            log_instance = channel.history(limit=999999999)
            #logcounter = 0
            if await self.check_privacy(ctx):
                private_area = True
            else:
                private_area = False
            whattocommit = []
            async for message in log_instance:
                #logcounter += 1
                if private_area:
                    content = None
                else:
                    content = str(message.content)
                whattocommit.append(
                    [
                        "INSERT INTO mmj_message_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        [
                            str(message.guild.id),
                            str(message.channel.id), 
                            str(message.author.id), 
                            str(message.id),
                            str(message.author.name),
                            str(int(message.author.bot)),
                            content,
                            str(int(time.mktime(message.created_at.timetuple()))) 
                        ]
                    ]
                )
            db.mass_query(whattocommit)
            #endtime = time.time()
            #importfinished = "Finished importing %s messages from %s. This took %s." % (logcounter, channel.mention, await measuretime(starttime, endtime))
            #await ctx.send(importfinished)
        except Exception as e:
            print(e)

    async def check_privacy(self, message):
        if (not db.query(["SELECT * FROM mmj_private_areas WHERE id = ?", [str(message.guild.id)]])) and (not db.query(["SELECT * FROM mmj_private_areas WHERE id = ?", [str(message.channel.id)]])):
            # Not a private channel
            return False
        else:
            # Private channel
            return True


def setup(bot):
    bot.add_cog(MomijiChannelImporting(bot))
