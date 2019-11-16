from embeds import AuditLoggingEmbeds
from modules import db
import time
import discord
from discord.ext import commands


class AuditLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        try:
            guild_audit_log_channel = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(guild.id)]])
            if guild_audit_log_channel:
                channell = self.bot.get_channel(int(guild_audit_log_channel[0][0]))
                about_this_ban = await guild.fetch_ban(member)
                await channell.send(embed=await AuditLoggingEmbeds.member_ban(member, about_this_ban.reason))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_member_remove")
            print(e)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        try:
            guild_audit_log_channel = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(guild.id)]])
            if guild_audit_log_channel:
                channell = self.bot.get_channel(int(guild_audit_log_channel[0][0]))
                await channell.send(embed=await AuditLoggingEmbeds.member_unban(user))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_member_remove")
            print(e)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            guild_audit_log_channel = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(member.guild.id)]])
            if guild_audit_log_channel:
                channell = self.bot.get_channel(int(guild_audit_log_channel[0][0]))
                await channell.send(embed=await AuditLoggingEmbeds.member_remove(member))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_member_remove")
            print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            guild_audit_log_channel = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(member.guild.id)]])
            if guild_audit_log_channel:
                channell = self.bot.get_channel(int(guild_audit_log_channel[0][0]))
                await channell.send(embed=await AuditLoggingEmbeds.member_join(member))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_member_join")
            print(e)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            if not before.author.bot:
                if before.content != after.content:
                    guild_audit_log_channel = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(before.guild.id)]])
                    if guild_audit_log_channel:
                        channell = self.bot.get_channel(int(guild_audit_log_channel[0][0]))
                        await channell.send(embed=await AuditLoggingEmbeds.message_edit(before, after))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_message_edit")
            print(e)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            if not message.author.bot:
                guild_audit_log_channel = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(message.guild.id)]])
                if guild_audit_log_channel:
                    channell = self.bot.get_channel(int(guild_audit_log_channel[0][0]))
                    await channell.send(embed=await AuditLoggingEmbeds.message_delete(message))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_message_delete")
            print(e)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if before.roles != after.roles:
                guild_audit_log_channel = db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(after.guild.id)]])
                if guild_audit_log_channel:
                    added = await self.comparelists(before.roles, after.roles, reverse = True)
                    removed = await self.comparelists(before.roles, after.roles, reverse = False)

                    if added:
                        text = "**Added**:\n%s"
                        role = added[0]
                    elif removed:
                        text = "**Removed**:\n%s"
                        role = removed[0]

                    voicerole = db.query(["SELECT role_id FROM voice_roles WHERE role_id = ?", [str(role.id)]])
                    regularsrole = db.query(["SELECT value FROM config WHERE setting = ? AND value = ?", ["guild_regular_role", str(role.id)]])
                    if (not voicerole) and (not regularsrole): ## TODO: fix
                        channell = self.bot.get_channel(int(guild_audit_log_channel[0][0]))
                        await channell.send(embed=await AuditLoggingEmbeds.role_change(after, text % (role.name)))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_member_update")
            print(e)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        try:
            if before.name != after.name or before.discriminator != after.discriminator:
                guild_audit_log_channel_list = db.query(["SELECT parent,value FROM config WHERE setting = ?", ["guild_audit_log_channel"]])
                for guild_audit_log_channel in guild_audit_log_channel_list:
                    guild = self.bot.get_guild(int(guild_audit_log_channel[0]))
                    if guild:
                        if guild.get_member(after.id):
                            channell = self.bot.get_channel(int(guild_audit_log_channel[1]))
                            await channell.send(embed=await AuditLoggingEmbeds.on_user_update(before, after))
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in on_user_update")
            print(e)

    async def comparelists(self, list1, list2, reverse = False):
        difference = []
        if reverse:
            comparelist1 = list2
            comparelist2 = list1
        else:
            comparelist1 = list1
            comparelist2 = list2
        for i in comparelist1:
            if not i in comparelist2:
                difference.append(i)
        return difference


def setup(bot):
    bot.add_cog(AuditLogging(bot))
