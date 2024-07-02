from momiji.modules import permissions
from momiji.embeds import VoiceLogging as VoiceLoggingEmbeds
from discord.ext import commands


class VoiceLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vl_enable", brief="Enable voice logging in this server")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vl_enable(self, ctx, delete_after=0):
        await self.bot.db.execute("INSERT INTO voice_logging_channels VALUES (?, ?, ?)",
                                  [int(ctx.guild.id), int(ctx.channel.id), int(delete_after)])
        await self.bot.db.commit()
        await ctx.reply(f"Voice logging is now enabled in this server.")

    @commands.command(name="vl_disable", brief="Disable voice logging in this server")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vl_disable(self, ctx):
        await self.bot.db.execute("DELETE FROM voice_logging_channels WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.commit()
        await ctx.reply(f"Voice logging is now disabled in this server.")

    @commands.command(name="vl_check", brief="Check if voice logging is enabled in this server")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vl_check(self, ctx):
        async with self.bot.db.execute("SELECT delete_after FROM voice_logging_channels "
                                       "WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            voice_logging_enabled = await cursor.fetchone()
        if voice_logging_enabled:
            delete_after = voice_logging_enabled[0]
            await ctx.reply(f"Voice logging is enabled with delete time of {delete_after} seconds.")
        else:
            await ctx.reply(f"Voice logging is not enabled on this server.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async with self.bot.db.execute("SELECT delete_after FROM voice_logging_channels "
                                       "WHERE guild_id = ?", [int(member.guild.id)]) as cursor:
            voice_logging_enabled = await cursor.fetchone()

        if not voice_logging_enabled:
            return

        if voice_logging_enabled[0]:
            delete_after = int(voice_logging_enabled[0])
        else:
            delete_after = None

        if before.channel == after.channel:
            # User has not switched channels
            return

        if not before.channel:
            await after.channel.send(
                embed=VoiceLoggingEmbeds.member_voice_join(member, after.channel),
                delete_after=delete_after
            )
            return

        if not after.channel:
            await before.channel.send(
                embed=VoiceLoggingEmbeds.member_voice_left(member, before.channel),
                delete_after=delete_after
            )
            return

        if before.channel != after.channel:
            await before.channel.send(
                embed=VoiceLoggingEmbeds.member_voice_left(member, before.channel),
                delete_after=delete_after
            )
            await after.channel.send(
                embed=VoiceLoggingEmbeds.member_voice_join(member, after.channel),
                delete_after=delete_after
            )
            return


async def setup(bot):
    await bot.add_cog(VoiceLogging(bot))
