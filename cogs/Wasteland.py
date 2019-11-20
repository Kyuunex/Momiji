from embeds import WastelandEmbeds
from modules import db
from discord.ext import commands


class Wasteland(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wasteland_channels = db.query("SELECT guild_id, channel_id FROM wasteland_channels")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        for wasteland_channel in self.wasteland_channels:
            if str(wasteland_channel[0]) == str(guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                about_this_ban = await guild.fetch_ban(member)
                await channel.send(embed=await WastelandEmbeds.member_ban(member, about_this_ban.reason))

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        for wasteland_channel in self.wasteland_channels:
            if str(wasteland_channel[0]) == str(guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_unban(user))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        for wasteland_channel in self.wasteland_channels:
            if str(wasteland_channel[0]) == str(member.guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_remove(member))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for wasteland_channel in self.wasteland_channels:
            if str(wasteland_channel[0]) == str(member.guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_join(member))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.author.bot:
            if before.content != after.content:
                for wasteland_channel in self.wasteland_channels:
                    if str(wasteland_channel[0]) == str(before.guild.id):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        await channel.send(embed=await WastelandEmbeds.message_edit(before, after))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            for wasteland_channel in self.wasteland_channels:
                if str(wasteland_channel[0]) == str(message.guild.id):
                    channel = self.bot.get_channel(int(wasteland_channel[1]))
                    await channel.send(embed=await WastelandEmbeds.message_delete(message))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # TODO: make this more efficient
        if before.roles != after.roles:
            for wasteland_channel in self.wasteland_channels:
                if str(wasteland_channel[0]) == str(after.guild.id):
                    added = await self.compare_lists(before.roles, after.roles, reverse=True)
                    removed = await self.compare_lists(before.roles, after.roles, reverse=False)

                    if added:
                        text = "**Added**:\n%s"
                        role = added[0]
                    elif removed:
                        text = "**Removed**:\n%s"
                        role = removed[0]

                    voice_role = db.query(["SELECT role_id FROM voice_roles WHERE role_id = ?", [str(role.id)]])
                    regulars_role = db.query(["SELECT role_id FROM regular_roles WHERE role_id = ?", [str(role.id)]])
                    if (not voice_role) and (not regulars_role):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        await channel.send(embed=await WastelandEmbeds.role_change(after, text % role.name))

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name or before.discriminator != after.discriminator:
            for wasteland_channel in self.wasteland_channels:
                guild = self.bot.get_guild(int(wasteland_channel[0]))
                if guild:
                    if guild.get_member(after.id):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        await channel.send(embed=await WastelandEmbeds.on_user_update(before, after))

    async def compare_lists(self, list1, list2, reverse=False):
        difference = []
        if reverse:
            compare_list1 = list2
            compare_list2 = list1
        else:
            compare_list1 = list1
            compare_list2 = list2
        for i in compare_list1:
            if not i in compare_list2:
                difference.append(i)
        return difference


def setup(bot):
    bot.add_cog(Wasteland(bot))
