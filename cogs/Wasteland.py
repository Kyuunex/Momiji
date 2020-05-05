from discord.ext import commands
import discord


class Wasteland(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if str(wasteland_channel[0]) == str(guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                about_this_ban = await guild.fetch_ban(member)
                await channel.send(embed=await WastelandEmbeds.member_ban(member, about_this_ban.reason))

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if str(wasteland_channel[0]) == str(guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_unban(user))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if str(wasteland_channel[0]) == str(member.guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_remove(member))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()
        for wasteland_channel in wasteland_channels:
            if str(wasteland_channel[0]) == str(member.guild.id):
                channel = self.bot.get_channel(int(wasteland_channel[1]))
                await channel.send(embed=await WastelandEmbeds.member_join(member))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT channel_id FROM wasteland_ignore_channels") as cursor:
            wasteland_ignore_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT guild_id, user_id FROM wasteland_ignore_users") as cursor:
            wasteland_ignore_users = await cursor.fetchall()

        if wasteland_ignore_channels:
            for ignore_channel in wasteland_ignore_channels:
                if str(ignore_channel[0]) == str(before.channel.id):
                    return None

        if wasteland_ignore_users:
            for ignore_user in wasteland_ignore_users:
                if str(ignore_user[0]) == str(before.guild.id):
                    if str(ignore_user[1]) == str(before.author.id):
                        return None

        if not before.author.bot:
            if before.content != after.content:
                for wasteland_channel in wasteland_channels:
                    if str(wasteland_channel[0]) == str(before.guild.id):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        await channel.send(embed=await WastelandEmbeds.message_edit(before, after))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT channel_id FROM wasteland_ignore_channels") as cursor:
            wasteland_ignore_channels = await cursor.fetchall()
        async with self.bot.db.execute("SELECT guild_id, user_id FROM wasteland_ignore_users") as cursor:
            wasteland_ignore_users = await cursor.fetchall()

        if wasteland_ignore_channels:
            for ignore_channel in wasteland_ignore_channels:
                if str(ignore_channel[0]) == str(message.channel.id):
                    return None

        if wasteland_ignore_users:
            for ignore_user in wasteland_ignore_users:
                if str(ignore_user[0]) == str(message.guild.id):
                    if str(ignore_user[1]) == str(message.author.id):
                        return None

        if not message.author.bot:
            for wasteland_channel in wasteland_channels:
                if str(wasteland_channel[0]) == str(message.guild.id):
                    channel = self.bot.get_channel(int(wasteland_channel[1]))
                    await channel.send(embed=await WastelandEmbeds.message_delete(message))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # TODO: make this more efficient
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()

        if before.roles != after.roles:
            for wasteland_channel in wasteland_channels:
                if str(wasteland_channel[0]) == str(after.guild.id):
                    added = await self.compare_lists(before.roles, after.roles, reverse=True)
                    removed = await self.compare_lists(before.roles, after.roles, reverse=False)

                    if added:
                        role = added[0]
                        text = f"**Added**:\n{role.name}"
                    elif removed:
                        role = removed[0]
                        text = f"**Removed**:\n{role.name}"

                    async with self.bot.db.execute("SELECT role_id FROM voice_roles WHERE role_id = ?",
                                                 [str(role.id)]) as cursor:
                        voice_role = await cursor.fetchall()
                    async with self.bot.db.execute("SELECT role_id FROM regular_roles WHERE role_id = ?",
                                                 [str(role.id)]) as cursor:
                        regulars_role = await cursor.fetchall()
                    if (not voice_role) and (not regulars_role):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        await channel.send(embed=await WastelandEmbeds.role_change(after, text))

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name or before.discriminator != after.discriminator:
            async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
                wasteland_channels = await cursor.fetchall()

            for wasteland_channel in wasteland_channels:
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


class WastelandEmbeds:
    @staticmethod
    async def message_delete(message):
        if message:
            member = message.author
            embed = discord.Embed(
                description=message.content,
                color=0xAD6F49
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator} | {member.display_name} | {member.id}",
                icon_url=member.avatar_url
            )
            embed.set_footer(
                text=f"Message deleted in #{message.channel.name}"
            )
            return embed
        else:
            return None

    @staticmethod
    async def message_edit(before, after):
        if before:
            member = before.author
            embed = discord.Embed(
                description=f"**Before**:\n{before.content}\n\n**After:**\n{after.content}",
                color=0x9ACDA5
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator} | {member.display_name} | {member.id}",
                icon_url=member.avatar_url
            )
            embed.set_footer(
                text=f"Message edited in #{before.channel.name}"
            )
            return embed
        else:
            return None

    @staticmethod
    async def member_join(member):
        if member:
            embed = discord.Embed(
                description=f"{member.mention}\n{member.id}",
                color=0x299880
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="User joined"
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None

    @staticmethod
    async def member_remove(member):
        if member:
            embed = discord.Embed(
                description=f"{member.mention}\n{member.id}",
                color=0x523104
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="User left or got kicked"
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None

    @staticmethod
    async def member_ban(member, reason):
        if member:
            text = f"{member.mention}"
            text += f"\n{member.id}"
            text += f"\n\n{reason}"
            embed = discord.Embed(
                description=text,
                color=0x800000
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="Member banned"
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None

    @staticmethod
    async def member_unban(member):
        if member:
            embed = discord.Embed(
                description=f"{member.mention}\n{member.id}",
                color=0x00ff00
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="Member unbanned"
            )
            embed.set_thumbnail(url=member.avatar_url)
            return embed
        else:
            return None

    @staticmethod
    async def role_change(member, desc):
        if member:
            embed = discord.Embed(
                description=desc,
                color=0xAABBBB
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator} | {member.display_name} | {member.id}",
                icon_url=member.avatar_url
            )
            embed.set_footer(
                text="Role Changes"
            )
            return embed
        else:
            return None

    @staticmethod
    async def on_user_update(before, after):
        if after:
            embed = discord.Embed(
                description=f"**Old Username**:\n{before.name}#{before.discriminator}",
                color=0xAACCEE
            )
            embed.set_author(
                name=f"{after.name}#{after.discriminator} | {after.id}",
                icon_url=after.avatar_url
            )
            embed.set_footer(
                text="Username Change"
            )
            return embed
        else:
            return None


def setup(bot):
    bot.add_cog(Wasteland(bot))
