import discord
from discord.ext import commands


class VoiceLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async with self.bot.db.execute("SELECT channel_id FROM voice_logging_channels "
                                       "WHERE guild_id = ?", [int(member.guild.id)]) as cursor:
            voice_logging_channels = await cursor.fetchall()

        for voice_logging_channel in voice_logging_channels:
            channel = self.bot.get_channel(int(voice_logging_channel[0]))
            if not channel:
                # channel seems to be deleted
                await self.bot.db.execute("DELETE FROM voice_logging_channels "
                                          "WHERE channel_id = ?", [int(voice_logging_channel[0])])
                await self.bot.db.commit()
                continue

            if before.channel == after.channel:
                continue

            if not before.channel:
                await channel.send(embed=self.member_voice_join_left(member, after.channel, "joined"),
                                   delete_after=1800)
                continue

            if not after.channel:
                await channel.send(embed=self.member_voice_join_left(member, before.channel, "left"),
                                   delete_after=1800)
                continue

            await channel.send(embed=self.member_voice_switch(member, before.channel, after.channel),
                               delete_after=1800)

    def member_voice_join_left(self, member, channel, action):
        if member:
            description = f"{member.mention}\n"
            description += f"has {action}\n"
            description += f"**{channel.name}**"
            embed = discord.Embed(
                color=0x419400,
                description=description,
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None

    def member_voice_switch(self, member, before_channel, after_channel):
        if member:
            description = f"{member.mention}\n"
            description += "has switched\n"
            description += f"from **{before_channel.name}**\n"
            description += f"to **{after_channel.name}**"
            embed = discord.Embed(
                color=0x419400,
                description=description,
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None


def setup(bot):
    bot.add_cog(VoiceLogging(bot))
