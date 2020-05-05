from discord.ext import commands
import discord
from modules import wrappers


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
                try:
                    about_this_ban = await guild.fetch_ban(member)
                    ban_reason_string = about_this_ban.reason
                except:
                    ban_reason_string = "i have no permissions to fetch the ban reason"
                await channel.send(embed=await WastelandEmbeds.member_ban(member, ban_reason_string))

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
        async with self.bot.db.execute("SELECT guild_id, channel_id FROM wasteland_channels") as cursor:
            wasteland_channels = await cursor.fetchall()

        if before.roles != after.roles:
            for wasteland_channel in wasteland_channels:
                if str(wasteland_channel[0]) == str(after.guild.id):
                    added = await self.compare_roles(after.roles, before.roles)
                    removed = await self.compare_roles(before.roles, after.roles)

                    if added:
                        role = added[0]
                    else:
                        role = removed[0]

                    async with self.bot.db.execute("SELECT role_id FROM voice_roles WHERE role_id = ?",
                                                   [str(role.id)]) as cursor:
                        voice_role = await cursor.fetchall()
                    async with self.bot.db.execute("SELECT role_id FROM regular_roles WHERE role_id = ?",
                                                   [str(role.id)]) as cursor:
                        regulars_role = await cursor.fetchall()
                    if (not voice_role) and (not regulars_role):
                        channel = self.bot.get_channel(int(wasteland_channel[1]))
                        if added:
                            await channel.send(embed=await WastelandEmbeds.role_add(after, role))
                        else:
                            await channel.send(embed=await WastelandEmbeds.role_remove(after, role))

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

    async def compare_roles(self, list1, list2):
        difference = []
        for role in list1:
            if not role in list2:
                difference.append(role)
        return difference


class WastelandEmbeds:
    @staticmethod
    async def message_delete(message):
        if message:
            embed = discord.Embed(
                description=message.content,
                color=0xAD6F49
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.avatar_url
            )
            embed.set_footer(
                text="message deleted"
            )
            embed.add_field(name="channel", value=message.channel.mention)
            embed.add_field(name="member", value=message.author.mention)
            embed.add_field(name="user_id", value=message.author.id)
            embed.add_field(name="context", value=f"[(link)]({wrappers.make_message_link(message)})")
            return embed
        else:
            return None

    @staticmethod
    async def message_edit(before, after):
        if before:
            contents = f"**Before**:\n"
            contents += before.content
            contents += f"\n\n"
            contents += f"**After:**\n"
            contents += after.content
            embed = discord.Embed(
                description=contents,
                color=0x9ACDA5
            )
            embed.set_author(
                name=before.author.display_name,
                icon_url=before.author.avatar_url
            )
            embed.set_footer(
                text="message edited"
            )
            embed.add_field(name="channel", value=before.channel.mention)
            embed.add_field(name="member", value=before.author.mention)
            embed.add_field(name="user_id", value=before.author.id)
            embed.add_field(name="context", value=f"[(link)]({wrappers.make_message_link(before)})")
            return embed
        else:
            return None

    @staticmethod
    async def member_join(member):
        if member:
            embed = discord.Embed(
                color=0x299880
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="user joined"
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="member", value=member.mention)
            embed.add_field(name="user_id", value=member.id)
            return embed
        else:
            return None

    @staticmethod
    async def member_remove(member):
        if member:
            embed = discord.Embed(
                color=0x523104
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="user left or got kicked"
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="member", value=member.mention)
            embed.add_field(name="user_id", value=member.id)
            return embed
        else:
            return None

    @staticmethod
    async def member_ban(member, reason):
        if member:
            embed = discord.Embed(
                description=reason,
                color=0x800000
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="user banned"
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="member", value=member.mention)
            embed.add_field(name="user_id", value=member.id)
            return embed
        else:
            return None

    @staticmethod
    async def member_unban(member):
        if member:
            embed = discord.Embed(
                color=0x00ff00
            )
            embed.set_author(
                name=f"{member.name}#{member.discriminator}"
            )
            embed.set_footer(
                text="user unbanned"
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="member", value=member.mention)
            embed.add_field(name="user_id", value=member.id)
            return embed
        else:
            return None

    @staticmethod
    async def role_add(member, role):
        if member:
            embed = discord.Embed(
                color=0x57b3ff
            )
            embed.set_footer(
                text="role changes"
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="member", value=member.mention)
            embed.add_field(name="user_id", value=member.id)
            embed.add_field(name="role added", value=role.name, inline=False)
            return embed
        else:
            return None

    @staticmethod
    async def role_remove(member, role):
        if member:
            embed = discord.Embed(
                color=0x546a7d
            )
            embed.set_footer(
                text="role changes"
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="member", value=member.mention)
            embed.add_field(name="user_id", value=member.id)
            embed.add_field(name="role removed", value=role.name, inline=False)
            return embed
        else:
            return None

    @staticmethod
    async def on_user_update(before, after):
        if after:
            embed = discord.Embed(
                color=0xAACCEE
            )
            embed.set_footer(
                text="username change"
            )
            embed.set_thumbnail(url=before.avatar_url)
            embed.add_field(name="member", value=after.mention)
            embed.add_field(name="user_id", value=after.id)
            embed.add_field(name="old username", value=f"{before.name}#{before.discriminator}")
            embed.add_field(name="new username", value=f"{after.name}#{after.discriminator}")
            return embed
        else:
            return None


def setup(bot):
    bot.add_cog(Wasteland(bot))
