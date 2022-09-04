import discord
from momiji.modules import permissions
from momiji.reusables import send_large_message

from discord.ext import commands


class Gatekeeper(commands.Cog):
    """
    The Gatekeeper module is designed to enforce the invite-only nature of a given server.
    With this enabled, if a user who is not whitelisted joins the server,
    they will be removed there and then.
    To enable this functionality, type ;gatekeeper_enable
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gatekeeper_enable", brief="Enable Gatekeeper in this guild")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def gatekeeper_enable(self, ctx):
        """
        Enable Gatekeeper in this guild
        """

        try:
            async with self.bot.db.execute("SELECT guild_id FROM gatekeeper_enabled_guilds WHERE guild_id = ?",
                                           [int(ctx.guild.id)]) as cursor:
                is_gatekeeper_enabled = await cursor.fetchall()
            if is_gatekeeper_enabled:
                await ctx.send(f"gatekeeper is already enabled in this server")
                return

            await self.bot.db.execute("INSERT INTO gatekeeper_enabled_guilds VALUES (?)", [int(ctx.guild.id)])
            await self.bot.db.commit()
            await ctx.send(f"gatekeeper is now enabled in this server")
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=str(e)))

    @commands.command(name="gatekeeper_disable", brief="Disable Gatekeeper in this guild")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def gatekeeper_disable(self, ctx):
        """
        Disable Gatekeeper in this guild
        """

        try:
            async with self.bot.db.execute("SELECT guild_id FROM gatekeeper_enabled_guilds WHERE guild_id = ?",
                                           [int(ctx.guild.id)]) as cursor:
                is_gatekeeper_enabled = await cursor.fetchall()
            if not is_gatekeeper_enabled:
                await ctx.send(f"gatekeeper is not enabled in this server")
                return

            await self.bot.db.execute("DELETE FROM gatekeeper_enabled_guilds WHERE guild_id = ?", [int(ctx.guild.id)])
            await self.bot.db.commit()
            await ctx.send(f"gatekeeper is now disabled in this server")
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=str(e)))

    @commands.command(name="gatekeeper_whitelist_user", brief="Whitelist a user to join this server")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def gatekeeper_whitelist_user(self, ctx, *user_id_list):
        """
        Add one or multiple users to a gatekeeper whitelist for this server.
        """

        for user_id in user_id_list:
            async with self.bot.db.execute("SELECT * FROM gatekeeper_whitelist "
                                           "WHERE guild_id = ? AND user_id = ?",
                                           [int(ctx.guild.id), int(user_id)]) as cursor:
                is_user_whitelisted = await cursor.fetchone()
            if is_user_whitelisted:
                await ctx.send(f"user with id `{user_id}` is already whitelisted")
            else:
                await self.bot.db.execute("INSERT INTO gatekeeper_whitelist VALUES (?,?,?)",
                                          [int(ctx.guild.id), int(user_id), int(ctx.author.id)])
        await self.bot.db.commit()

        await ctx.send("done")

    @commands.command(name="vouch", brief="Vouch for a user to be allowed on this server")
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vouch(self, ctx, user_id):
        """
        Vouch for a user to be allowed on this server
        """

        async with self.bot.db.execute("SELECT guild_id FROM gatekeeper_vouchable_guilds WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            is_guild_vouchable = await cursor.fetchall()
        if not is_guild_vouchable:
            await ctx.send("this is not configured in this guild")
            return

        if not user_id.isdigit():
            await ctx.send("user_id must be all digits")
            return

        try:
            bans = await ctx.guild.bans()
            for ban in bans:
                if ban.user.id == int(user_id):
                    await ctx.guild.unban(user=ban.user,
                                          reason=f"unbanned by a vouch by {ctx.author} aka {str(ctx.author.id)}")
        except discord.Forbidden:
            await ctx.send("no permissions to unban, manual action by admin required")

        async with self.bot.db.execute("SELECT * FROM gatekeeper_whitelist "
                                       "WHERE guild_id = ? AND user_id = ?",
                                       [int(ctx.guild.id), int(user_id)]) as cursor:
            is_user_whitelisted = await cursor.fetchone()
        if is_user_whitelisted:
            await ctx.send(f"user with id `{user_id}` is already vouched for")
            return

        await self.bot.db.execute("INSERT INTO gatekeeper_whitelist VALUES (?,?,?)",
                                  [int(ctx.guild.id), int(user_id), int(ctx.author.id)])
        await self.bot.db.commit()

        await ctx.send(f"you have sucessfully vouched for user with id `{user_id}` to be allowed on this server")

    @commands.command(name="gatekeeper_unwhitelist_user", brief="Unwhitelist a user from joining this server")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def gatekeeper_unwhitelist_user(self, ctx, *user_id_list):
        """
        Remove one or multiple users from a gatekeeper whitelist for this server.
        """

        for user_id in user_id_list:
            await self.bot.db.execute("DELETE FROM gatekeeper_whitelist WHERE user_id = ?", [int(user_id)])
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

        async with self.bot.db.execute("SELECT user_id, vouched_by_id FROM gatekeeper_whitelist WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            whitelisted_users = await cursor.fetchall()

        if whitelisted_users:
            buffer = ":wave: **User IDs that are whitelisted to join this server.**\n\n"
            for whitelisted_user in whitelisted_users:
                buffer += f"<@{whitelisted_user[0]}> "
                buffer += f"`{whitelisted_user[0]}` "
                buffer += f"`{await self.get_cached_username(ctx, whitelisted_user[0])}` "
                buffer += f"vouched by `{await self.get_cached_username(ctx, whitelisted_user[1])}` "
                buffer += "\n"
        else:
            buffer = "Gatekeeper whitelist is empty.\n"

        async with self.bot.db.execute("SELECT guild_id FROM gatekeeper_enabled_guilds WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            is_gatekeeper_enabled = await cursor.fetchall()
        if not is_gatekeeper_enabled:
            buffer += "\nAlso, Gatekeeper whitelist is disabled for this guild.\n"

        try:
            await ctx.guild.bans()
        except discord.Forbidden:
            buffer += "\nAlso, this won't work properly because I don't have permissions to ban in this guild.\n"

        embed = discord.Embed(color=0xf76a8c)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="get_getekeeper_delta", brief="Get users who are in the server but forgot to be whitelisted")
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def get_getekeeper_delta(self, ctx):
        """
        Print out users who are in the server but forgot to be whitelisted
        """

        async with self.bot.db.execute("SELECT user_id FROM gatekeeper_whitelist WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            whitelisted_users = await cursor.fetchall()

        if whitelisted_users:
            member_list = ctx.guild.members
            buffer = ":wave: **Users who are in this server but have been forgotten to be whitelisted.**\n\n"
            for member in member_list:
                async with self.bot.db.execute("SELECT * FROM gatekeeper_whitelist "
                                               "WHERE guild_id = ? AND user_id = ?",
                                               [int(ctx.guild.id), int(member.id)]) as cursor:
                    is_whitelisted = await cursor.fetchone()
                if not is_whitelisted:
                    buffer += f"{member.mention} "
                    buffer += f"`{member.id}` "
                    buffer += "\n"
        else:
            buffer = "Gatekeeper whitelist is empty.\n"

        embed = discord.Embed(color=0xf76a8c)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        async with self.bot.db.execute("SELECT guild_id FROM gatekeeper_enabled_guilds WHERE guild_id = ?",
                                       [int(member.guild.id)]) as cursor:
            is_gatekeeper_enabled = await cursor.fetchall()
        if not is_gatekeeper_enabled:
            # gatekeeper is disabled
            return

        async with self.bot.db.execute("SELECT * FROM gatekeeper_whitelist "
                                       "WHERE guild_id = ? AND user_id = ?",
                                       [int(member.guild.id), int(member.id)]) as cursor:
            is_user_whitelisted = await cursor.fetchone()
        if is_user_whitelisted:
            # user is whitelisted and allowed to remain here
            return

        # if we are here, the user is not allowed here

        async with self.bot.db.execute("SELECT channel_id FROM guild_event_report_channels WHERE guild_id = ?",
                                       [int(member.guild.id)]) as cursor:
            event_report_channel_id = await cursor.fetchone()
        if not event_report_channel_id:
            return

        event_report_channel = self.bot.get_channel(int(event_report_channel_id[0]))

        try:
            await member.guild.bans()
        except discord.Forbidden:
            await event_report_channel.send(f"{member.mention} has joined, "
                                            f"but is not whitelisted and I don't have permissions to ban them")
            return

        try:
            await member.send(embed=await self.deny_embed(member.guild, member))
            await member.ban(reason="banned by the gatekeeper for not being whitelisted")
            await event_report_channel.send(f"user `{member.name}` with id `{member.id}` tried to join this server "
                                            f"but was removed for not being whitelisted")
        except Exception as e:
            await event_report_channel.send(f"GATEKEEPER ERROR {str(e)}")

    async def get_cached_username(self, ctx, user_id):
        member = ctx.guild.get_member(int(user_id))
        if member:
            return member.name

        user = self.bot.get_user(user_id)
        if user:
            return user.name

        async with self.bot.db.execute("SELECT username FROM mmj_message_logs WHERE user_id = ?",
                                       [int(user_id)]) as cursor:
            user_info = await cursor.fetchone()
        if user_info:
            return user_info[0]

        return ":"

    async def deny_embed(self, guild, member):
        deny_message = "the server you just joined is a private server that has a member whitelist enabled. " \
                       "unfortunately you are not in it, so you are not allowed to join. "

        async with self.bot.db.execute("SELECT guild_id FROM gatekeeper_vouchable_guilds WHERE guild_id = ?",
                                       [int(guild.id)]) as cursor:
            is_guild_vouchable = await cursor.fetchall()
        if not is_guild_vouchable:
            deny_message += "if you think you should be whitelisted, contact an admin."
        else:
            deny_message += "if you think you should be whitelisted, " \
                            "contact any of the members of this server" \
                            f" and ask them to vouch for you by typing this command \n" \
                            f"```\n;vouch {member.id}\n```"

        embed = discord.Embed(
            description=deny_message,
            color=0x800000
        )
        embed.set_author(
            name=guild.name,
            icon_url=guild.icon_url
        )
        embed.set_footer(
            text="i saw you coming from a thousand ri away."
        )
        return embed


async def setup(bot):
    await bot.add_cog(Gatekeeper(bot))
