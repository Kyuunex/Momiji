from modules import db
import discord
from discord.ext import commands


class VoiceLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_voice_log_channel_id = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_voice_log_channel", str(member.guild.id)]])
        if guild_voice_log_channel_id:
            voicelogchannel = self.bot.get_channel(int(guild_voice_log_channel_id[0][0]))
            if not before.channel == after.channel:
                if before.channel == None:  # Member joined a channel
                    await voicelogchannel.send(embed=await self.member_voice_join_left(member, after.channel, "joined"), delete_after=1800)
                else:
                    if after.channel == None:  # Member left channel
                        await voicelogchannel.send(embed=await self.member_voice_join_left(member, before.channel, "left"), delete_after=1800)
                    else:  # Member switched channel
                        await voicelogchannel.send(embed=await self.member_voice_switch(member, before.channel, after.channel), delete_after=1800)

    async def member_voice_join_left(self, member, channel, action):
        if member:
            embed = discord.Embed(
                color=0x419400,
                description="%s\nhas %s\n**%s**" % (member.mention, action, channel.name)
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None

    async def member_voice_switch(self, member, beforechannel, afterchannel):
        if member:
            embed = discord.Embed(
                color=0x419400,
                description="%s\nhas switched\nfrom **%s**\nto **%s**" % (member.mention, beforechannel.name, afterchannel.name)
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None


def setup(bot):
    bot.add_cog(VoiceLogging(bot))
