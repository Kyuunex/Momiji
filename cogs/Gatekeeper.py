import random
import discord
from modules import permissions
from modules import wrappers

from discord.ext import commands


class Gatekeeper(commands.Cog):
    def __init__(self, bot):
        """
        The Gatekeeper module is designed to enforce the invite-only nature of a given server.
        With this enabled, if a user who is not whitelisted joins the server,
        they will be removed there and then.
        To enable this functionality, at least one user must be in a whitelist.
        Having an empty whitelist will disable this functionality.
        """

        self.bot = bot

    @commands.command(name="gatekeeper_whitelist_user", brief="Whitelist a user to join this server")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def gatekeeper_whitelist_user(self, ctx, *user_id_list):
        """
        Add one or multiple users to a gatekeeper whitelist for this server.
        """

        for user_id in user_id_list:
            await self.bot.db.execute("INSERT INTO gatekeeper_whitelist VALUES (?,?)",
                                      [str(ctx.guild.id), str(user_id)])
        await self.bot.db.commit()

        await ctx.send("done")

    @commands.command(name="gatekeeper_unwhitelist_user", brief="Unwhitelist a user from joining this server")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def gatekeeper_unwhitelist_user(self, ctx, *user_id_list):
        """
        Remove one or multiple users from a gatekeeper whitelist for this server.
        """

        for user_id in user_id_list:
            await self.bot.db.execute("DELETE FROM gatekeeper_whitelist WHERE user_id = ?", [str(user_id)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    @commands.command(name="get_gatekeeper_whitelisted_users", brief="Get whitelisted users for this server")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def get_gatekeeper_whitelisted_users(self, ctx):
        """
        Print out users IDs of everyone who is whitelisted in this server
        """

        async with self.bot.db.execute("SELECT user_id FROM gatekeeper_whitelist WHERE guild_id = ?",
                                       [str(ctx.guild.id)]) as cursor:
            whitelisted_users = await cursor.fetchall()

        if whitelisted_users:
            buffer = ":wave: **User IDs that are whitelisted to join this server.**\n\n"
            for whitelisted_user in whitelisted_users:
                buffer += f"<@{whitelisted_user[0]}> "
                buffer += f"`{whitelisted_user[0]}` "
                buffer += f"`{await self.get_cached_username(ctx, whitelisted_user[0])}`"
                buffer += "\n"
        else:
            buffer = "Gatekeeper is disabled in this server because nobody is whitelisted.\n"

        embed = discord.Embed(color=0xf76a8c)

        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        async with self.bot.db.execute("SELECT user_id FROM gatekeeper_whitelist WHERE guild_id = ?",
                                       [str(member.guild.id)]) as cursor:
            is_gatekeeper_enabled = await cursor.fetchall()
        if not is_gatekeeper_enabled:
            # gatekeeper is disabled
            return

        async with self.bot.db.execute("SELECT * FROM gatekeeper_whitelist "
                                       "WHERE guild_id = ? AND user_id = ?",
                                       [str(member.guild.id), str(member.id)]) as cursor:
            is_user_whitelisted = await cursor.fetchone()
        if is_user_whitelisted:
            # user is whitelisted and allowed to remain here
            return

        # if we are here, the user is not allowed here

        deny_message = "i saw you coming from a thousand ri away. " \
                       "unfortunately for you, this is a private server and " \
                       "you are not allowed to join this server because " \
                       "it has a whitelist enabled in which you are not in. " \
                       "if you think you should be whitelisted, contact an admin."

        try:
            await member.send(content=deny_message)
            await member.ban(reason="banned by the gatekeeper for not being whitelisted")
        except Exception as e:
            print(e)

        async with self.bot.db.execute("SELECT channel_id FROM guild_event_report_channels WHERE guild_id = ?",
                                       [str(member.guild.id)]) as cursor:
            event_report_channel_id = await cursor.fetchone()
        if not event_report_channel_id:
            return

        event_report_channel = self.bot.get_channel(int(event_report_channel_id[0]))

        await event_report_channel.send(f"user `{member.name}` with id `{member.id}` tried to join this server "
                                        f"but was removed for not being whitelisted")

    async def get_cached_username(self, ctx, user_id):
        member = ctx.guild.get_member(int(user_id))
        if not member:
            async with self.bot.db.execute("SELECT username FROM mmj_message_logs WHERE user_id = ?",
                                           [str(user_id)]) as cursor:
                user_info = await cursor.fetchone()
            return user_info[0]
        else:
            return member.name


def setup(bot):
    bot.add_cog(Gatekeeper(bot))
