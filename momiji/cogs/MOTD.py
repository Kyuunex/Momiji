import random

import discord
from discord.ext import commands
from momiji.modules import permissions


class MOTD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="manual_motd")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def manual_motd(self, ctx):
        async with await self.bot.db.execute("SELECT channel_id FROM motd_config WHERE guild_id = ?",
                                             [ctx.guild.id]) as cursor:
            motd_configs = await cursor.fetchone()

        if not motd_configs:
            await ctx.reply("MOTD is not configured for this guild!")
            return

        async with await self.bot.db.execute("SELECT message FROM motds WHERE guild_id = ?", [ctx.guild.id]) as cursor:
            motd_entries = await cursor.fetchall()

        if not motd_entries:
            await ctx.reply("There are no MOTD entries for this guild!")
            return

        channel = self.bot.get_channel(int(motd_configs[0]))

        if not channel:
            await ctx.reply("MOTD is incorrectly configured for this guild! I can't find the channel.")
            return

        random_message = random.choice(motd_entries)

        try:
            await channel.edit(topic="MOTD: " + random_message[0])
        except discord.Forbidden:
            await ctx.reply("I have no `manage_channels` permissions!")
            return

        await ctx.reply("MOTD updated!")


async def setup(bot):
    await bot.add_cog(MOTD(bot))
