from discord.ext import commands
import discord
from momiji.modules import cooldown
from momiji.modules import permissions


class LobbyPingRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping_role", brief="Ping the ping role!", aliases=['pingrole'])
    @commands.check(permissions.is_not_ignored)
    async def minesweeper(self, ctx):
        """
        This command pings the ping roles and controls the cooldown.
        """

        if not ctx.author.voice:
            await ctx.reply("You are not connected to a voice channel.")
            return

        channel = ctx.author.voice.channel

        async with self.bot.db.execute("SELECT role_id, cooldown FROM ping_roles WHERE channel_id = ?",
                                       [int(channel.id)]) as cursor:
            role_id_list = await cursor.fetchall()
        if not role_id_list:
            await ctx.reply(f"no ping role is configured for {channel.mention}")
            return

        sorted_role_list = sorted(role_id_list, key=lambda x: x[1])

        if not await cooldown.check(str(channel.id), "last_pingrole_time", int(sorted_role_list[0][1])):
            if not await permissions.is_admin(ctx):
                await ctx.send("ping role can only be pinged every 2 hours per voice channel")
                return

        for role_id in role_id_list:
            role = discord.utils.get(ctx.guild.roles, id=int(role_id[0]))
            await ctx.reply(f"{role.mention}! {ctx.author.mention} calls upon you over at {channel.mention}")


async def setup(bot):
    await bot.add_cog(LobbyPingRole(bot))
