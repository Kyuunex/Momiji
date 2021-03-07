from discord.ext import commands
from embeds import Wasteland as WastelandEmbeds


class Wasteland(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                       "WHERE event_name = 'on_member_ban' OR event_name = 'all'") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if int(wasteland_channel[0]) == int(guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                try:
                    about_this_ban = await guild.fetch_ban(member)
                    ban_reason_string = about_this_ban.reason
                except:
                    ban_reason_string = "i have no permissions to fetch the ban reason"
                await channel.send(embed=await WastelandEmbeds.member_ban(member, ban_reason_string))

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                       "WHERE event_name = 'on_member_unban' OR event_name = 'all'") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if int(wasteland_channel[0]) == int(guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_unban(user))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                       "WHERE event_name = 'on_member_remove' OR event_name = 'all'") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if int(wasteland_channel[0]) == int(member.guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_remove(member))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                       "WHERE event_name = 'on_member_join' OR event_name = 'all'") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if int(wasteland_channel[0]) == int(member.guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_join(member))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild:
            return

        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                       "WHERE event_name = 'on_message_edit' OR event_name = 'all'") as cursor:
            wasteland_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT channel_id FROM wasteland_ignore_channels") as cursor:
            wasteland_ignore_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT guild_id, user_id FROM wasteland_ignore_users") as cursor:
            wasteland_ignore_users = await cursor.fetchall()

        if wasteland_ignore_channels:
            for ignore_channel in wasteland_ignore_channels:
                if int(ignore_channel[0]) == int(before.channel.id):
                    return

        if wasteland_ignore_users:
            for ignore_user in wasteland_ignore_users:
                if int(ignore_user[0]) == int(before.guild.id):
                    if int(ignore_user[1]) == int(before.author.id):
                        return

        if not before.author.bot:
            if before.content != after.content:
                for wasteland_channel in wasteland_channels:
                    if int(wasteland_channel[0]) == int(before.guild.id):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        await channel.send(embed=await WastelandEmbeds.message_edit(before, after))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild:
            return

        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                       "WHERE event_name = 'on_message_delete' OR event_name = 'all'") as cursor:
            wasteland_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT channel_id FROM wasteland_ignore_channels") as cursor:
            wasteland_ignore_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT guild_id, user_id FROM wasteland_ignore_users") as cursor:
            wasteland_ignore_users = await cursor.fetchall()

        if wasteland_ignore_channels:
            for ignore_channel in wasteland_ignore_channels:
                if int(ignore_channel[0]) == int(message.channel.id):
                    return

        if wasteland_ignore_users:
            for ignore_user in wasteland_ignore_users:
                if int(ignore_user[0]) == int(message.guild.id):
                    if int(ignore_user[1]) == int(message.author.id):
                        return

        if not message.author.bot:
            for wasteland_channel in wasteland_channels:
                if int(wasteland_channel[0]) == int(message.guild.id):
                    channel = self.bot.get_channel(int(wasteland_channel[1]))
                    await channel.send(embed=await WastelandEmbeds.message_delete(message))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                       "WHERE event_name = 'on_member_update' OR event_name = 'all'") as cursor:
            wasteland_channels = await cursor.fetchall()

        if before.roles != after.roles:
            for wasteland_channel in wasteland_channels:
                if int(wasteland_channel[0]) == int(after.guild.id):
                    added = await self.compare_roles(after.roles, before.roles)
                    removed = await self.compare_roles(before.roles, after.roles)

                    if added:
                        role = added[0]
                    else:
                        role = removed[0]

                    async with self.bot.db.execute("SELECT role_id FROM voice_roles WHERE role_id = ?",
                                                   [int(role.id)]) as cursor:
                        voice_role = await cursor.fetchall()
                    async with self.bot.db.execute("SELECT role_id FROM regular_roles WHERE role_id = ?",
                                                   [int(role.id)]) as cursor:
                        regulars_role = await cursor.fetchall()
                    if (not voice_role) and (not regulars_role):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        if added:
                            await channel.send(embed=await WastelandEmbeds.role_add(after, role))
                        else:
                            await channel.send(embed=await WastelandEmbeds.role_remove(after, role))

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if not before.guild:
            return

        if before.name != after.name or before.discriminator != after.discriminator:
            async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels "
                                           "WHERE event_name = 'on_user_update' OR event_name = 'all'") as cursor:
                wasteland_channels = await cursor.fetchall()

            for wasteland_channel in wasteland_channels:
                guild = self.bot.get_guild(int(wasteland_channel[0]))
                if guild:
                    if guild.get_member(after.id):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        await channel.send(embed=await WastelandEmbeds.on_user_update(before, after))

    async def compare_roles(self, list1, list2):
        difference = []
        for role in list1:
            if not role in list2:
                difference.append(role)
        return difference


def setup(bot):
    bot.add_cog(Wasteland(bot))
