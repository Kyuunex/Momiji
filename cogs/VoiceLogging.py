import discord
from discord.ext import commands


class VoiceLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM voice_logging_channels") as cursor:
            voice_logging_channels = await cursor.fetchall()

        for voice_logging_channel in voice_logging_channels:
            if str(voice_logging_channel[0]) == str(member.guild.id):
                channel = self.bot.get_channel(int(voice_logging_channel[1]))
                if before.channel == after.channel:
                    return None

                if not before.channel:
                    await channel.send(embed=self.member_voice_join_left(member, after.channel, "joined"),
                                       delete_after=1800)
                else:
                    if not after.channel:
                        await channel.send(embed=self.member_voice_join_left(member, before.channel, "left"),
                                           delete_after=1800)
                    else:
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

    def member_voice_switch(self, member, before, after):
        if member:
            description = f"{member.mention}\n"
            description += "has switched\n"
            description += f"from **{before.name}**\n"
            description += f"to **{after.name}**"
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
