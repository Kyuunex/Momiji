from momiji.modules import permissions
from momiji.embeds import VoiceLogging as VoiceLoggingEmbeds
from discord.ext import commands


class VoiceLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vl_add", brief="Make this channel get voice logs.")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vl_add(self, ctx, delete_after=0):
        await self.bot.db.execute("INSERT INTO voice_logging_channels VALUES (?,?,?)",
                                  [int(ctx.guild.id), int(ctx.channel.id), int(delete_after)])
        await self.bot.db.commit()
        await ctx.reply(f"{ctx.channel.mention} is now set as a voice logging channel.")

    @commands.command(name="vl_remove", brief="Make this channel no longer get voice logs.")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vl_remove(self, ctx):
        await self.bot.db.execute("DELETE FROM voice_logging_channels WHERE guild_id = ? AND channel_id = ?",
                                  [int(ctx.guild.id), int(ctx.channel.id)])
        await self.bot.db.commit()
        await ctx.reply(f"{ctx.channel.mention} will no longer get voice logs.")

    @commands.command(name="vl_check", brief="Check if this channel is set as a voice logging channel.")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vl_check(self, ctx):
        async with self.bot.db.execute("SELECT delete_after FROM voice_logging_channels "
                                       "WHERE guild_id = ? AND channel_id = ?",
                                       [int(ctx.guild.id), int(ctx.channel.id)]) as cursor:
            voice_logging_channels = await cursor.fetchall()
        if voice_logging_channels:
            delete_after = voice_logging_channels[0][0]
            await ctx.reply(f"{ctx.channel.mention} is indeed set to get voice logs with delete time of {delete_after}")
        else:
            await ctx.reply(f"{ctx.channel.mention} is not a voice logging channel.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async with self.bot.db.execute("SELECT channel_id, delete_after FROM voice_logging_channels "
                                       "WHERE guild_id = ?", [int(member.guild.id)]) as cursor:
            voice_logging_channels = await cursor.fetchall()

        for voice_logging_channel in voice_logging_channels:
            channel = self.bot.get_channel(int(voice_logging_channel[0]))

            if voice_logging_channel[1]:
                delete_after = int(voice_logging_channel[1])
            else:
                delete_after = None

            if not channel:
                # channel seems to be deleted
                await self.bot.db.execute("DELETE FROM voice_logging_channels "
                                          "WHERE channel_id = ?", [int(voice_logging_channel[0])])
                await self.bot.db.commit()
                continue

            if before.channel == after.channel:
                continue

            if not before.channel:
                await channel.send(embed=VoiceLoggingEmbeds.member_voice_join_left(member, after.channel, "joined"),
                                   delete_after=delete_after)
                continue

            if not after.channel:
                await channel.send(embed=VoiceLoggingEmbeds.member_voice_join_left(member, before.channel, "left"),
                                   delete_after=delete_after)
                continue

            await channel.send(embed=VoiceLoggingEmbeds.member_voice_switch(member, before.channel, after.channel),
                               delete_after=delete_after)


async def setup(bot):
    await bot.add_cog(VoiceLogging(bot))
