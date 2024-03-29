from momiji.modules import permissions
from momiji.reusables import get_member_helpers
from momiji.reusables import send_large_message
import discord
from discord.ext import commands
import random
import asyncio
import time


class Clubs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.club_owner_default_permissions = discord.PermissionOverwrite(
            create_instant_invite=True,
            manage_channels=True,
            manage_roles=True,
            manage_webhooks=True,
            view_channel=True,
            send_messages=True,
            manage_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            mention_everyone=False
        )
        self.club_bot_default_permissions = discord.PermissionOverwrite(
            manage_channels=True,
            manage_roles=True,
            view_channel=True,
            send_messages=True,
            embed_links=True
        )

    @commands.command(name="show_club_members", brief="Print out a list of members who are in this club")
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def show_club_members(self, ctx):
        """
        This command print out members are in this club.
        """

        async with self.bot.db.execute("SELECT user_id, member_since_timestamp "
                                       "FROM club_members WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            member_list = await cursor.fetchall()
        if not member_list:
            await ctx.reply("this is not a club channel or this club has no members")
            return

        async with self.bot.db.execute("SELECT owner_user_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            club_owner_id = await cursor.fetchone()

        buffer = ""
        for member_id in member_list:
            member = ctx.guild.get_member(int(member_id[0]))
            if member:
                buffer += f"{member.display_name}"
            else:
                buffer += f"{member_id[0]}"

            buffer += f", joined <t:{member_id[1]}:R> "

            if int(member_id[0]) == int(club_owner_id[0]):
                buffer += f" :crown: "
            buffer += f"\n"

        embed = discord.Embed(color=0xadff2f)
        embed.set_author(name="Club members")
        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="club_info", brief="Show club info")
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def show_club_info(self, ctx):
        """
        This command prints out club information.
        """

        async with self.bot.db.execute("SELECT name, text_channel_id, voice_channel_id, role_id, "
                                       "owner_user_id, public, public_joinable, created_at_timestamp, guild_id "
                                       "FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            club_details = await cursor.fetchone()
        if not club_details:
            await ctx.reply("this is not a club channel or this club has no members")
            return

        async with self.bot.db.execute("SELECT COUNT(user_id) FROM club_members WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            member_amount = await cursor.fetchone()

        embed = discord.Embed(color=0xadff2f)
        embed.set_author(name="Club info")

        embed.add_field(name="Name", value=club_details[0])

        member = ctx.guild.get_member(int(club_details[4]))
        if member:
            owner_text = member.display_name
        else:
            owner_text = club_details[4]
        embed.add_field(name="Owner", value=owner_text)

        embed.add_field(name="Member amount", value=member_amount[0])

        embed.add_field(name="Created", value=f"<t:{club_details[7]}:R>", inline=False)

        embed.add_field(name="Text channel", value=f"<#{club_details[1]}>")
        embed.add_field(name="Voice channel", value=f"<#{club_details[2]}>")
        embed.add_field(name="Role", value=f"<@&{club_details[3]}>")

        if club_details[5] == 0:
            privacy_text = "members only read and write"
        elif club_details[5] == 1:
            privacy_text = "all access for members, read-only for everyone else"
        elif club_details[5] == 2:
            privacy_text = "public read and write"
        else:
            privacy_text = "this setting is misconfigured"

        embed.add_field(name="Privacy", value=privacy_text, inline=False)

        if club_details[6] == 0:
            joinable_text = "disabled, club not publicly join-able"
        elif club_details[6] == 1:
            joinable_text = "notify club if anyone wants to join, only owner approves"
        elif club_details[6] == 2:
            joinable_text = "anyone can join automatically with the command"
        else:
            joinable_text = "this setting is misconfigured"

        embed.add_field(name="`;join_club` command setting", value=joinable_text, inline=False)

        await ctx.reply(embed=embed)

    @commands.command(name="admit", brief="Add a user in the current club")
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def admit(self, ctx, *, user_name: str):
        """
        This command is used to add a user into a Club.
        """

        async with self.bot.db.execute("SELECT TRUE FROM clubs WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            is_club_owner = await cursor.fetchone()
        if not (is_club_owner or await permissions.channel_manage_guild(ctx)):
            await ctx.reply("this channel is not your club")
            return

        async with self.bot.db.execute("SELECT role_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            role_id_db = await cursor.fetchone()
        if not role_id_db:
            await ctx.reply(":skull:")
            return

        member = get_member_helpers.get_member_guaranteed(ctx, user_name)
        if not member:
            await ctx.reply("No member found with what you specified. Try using a Discord account ID.")
            return

        # if member is ctx.author:
        #     await ctx.reply("you can't add yourself to this channel, you are already in and this breaks the bot :(")
        #     return

        role = ctx.guild.get_role(int(role_id_db[0]))
        if not role:
            await ctx.reply("Looks like the role for this club no longer exists.")
            return

        try:
            await member.add_roles(role, reason="added to a club")
        except discord.Forbidden:
            await ctx.reply("I do not have permissions to add roles.")

        async with self.bot.db.execute("SELECT user_id FROM club_members WHERE user_id = ? AND text_channel_id = ?",
                                       [int(member.id), int(ctx.channel.id)]) as cursor:
            is_already_in_club = await cursor.fetchone()
        if is_already_in_club:
            await ctx.reply("the database records show this member is already in the club, "
                            "but i made sure they got the club role anyways, hope this helps?")
            return

        await self.bot.db.execute("INSERT INTO club_members VALUES (?, ?, ?, ?)",
                                  [int(ctx.channel.id), int(member.id), int(time.time()), int(ctx.guild.id)])
        await self.bot.db.commit()
        await ctx.reply(f"added {member.mention} in this club")

    @commands.command(name="expel", brief="Remove a user from the current club")
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def expel(self, ctx, *, user_name: str):
        """
        This command is used to remove a user from a Club.
        """

        async with self.bot.db.execute("SELECT TRUE FROM clubs WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            is_club_owner = await cursor.fetchone()
        if not (is_club_owner or await permissions.channel_manage_guild(ctx)):
            await ctx.reply("this channel is not your club")
            return

        async with self.bot.db.execute("SELECT role_id, owner_user_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            club_details_db = await cursor.fetchone()
        if not club_details_db:
            await ctx.reply(":skull:")
            return

        member = get_member_helpers.get_member_guaranteed(ctx, user_name)
        if not member:
            await ctx.reply("No member found with what you specified. Try using a Discord account ID.")
            return

        if member.id == int(club_details_db[1]):
            await ctx.reply("club owner can not be removed from the club until the ownership is transferred, "
                            "otherwise this breaks the bot :(")
            return

        role = ctx.guild.get_role(int(club_details_db[0]))
        if not role:
            await ctx.reply("Looks like the role for this club no longer exists.")
            return

        try:
            await member.remove_roles(role, reason="removed from a club")
        except discord.Forbidden:
            await ctx.reply("I do not have permissions to remove roles.")

        await self.bot.db.execute("DELETE FROM club_members WHERE text_channel_id = ? AND user_id = ?",
                                  [int(ctx.channel.id), int(member.id)])
        await self.bot.db.commit()
        await ctx.reply(f"removed {member.mention} from this club")

    @commands.command(name="leave_club", brief="Leave the club")
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def leave_club(self, ctx):
        """
        Intended to be used by a club member to leave a club they no longer want to be a part of.
        """

        async with self.bot.db.execute("SELECT role_id, owner_user_id FROM clubs "
                                       "WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            role_id_list = await cursor.fetchone()
        if not role_id_list:
            await ctx.reply("this channel is not a club")
            return

        if ctx.author.id == int(role_id_list[1]):
            await ctx.reply("club owner can not be removed from the club until the ownership is transferred, "
                            "otherwise this breaks the bot :(")
            return

        role = ctx.guild.get_role(int(role_id_list[0]))
        if not role:
            await ctx.reply("Looks like the role for this club no longer exists.")
            return

        try:
            await ctx.author.remove_roles(role, reason="removed from a club")
        except discord.Forbidden:
            await ctx.reply("I do not have permissions to remove roles.")

        await self.bot.db.execute("DELETE FROM club_members WHERE text_channel_id = ? AND user_id = ?",
                                  [int(ctx.channel.id), int(ctx.author.id)])
        await self.bot.db.commit()
        await ctx.reply(f"removed {ctx.author.mention} from this club")

    @commands.command(name="club_role_color", brief="Update the club role color")
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def club_role_color(self, ctx, *, color: str):
        """
        Update the club role color

        Examples:
        ;club_role_color: 0x00FFFF

        """

        async with self.bot.db.execute("SELECT TRUE FROM clubs WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            is_club_owner = await cursor.fetchone()
        if not (is_club_owner or await permissions.channel_manage_guild(ctx)):
            await ctx.reply("this channel is not your club")
            return

        async with self.bot.db.execute("SELECT role_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            role_id_db = await cursor.fetchone()
        if not role_id_db:
            await ctx.reply(":skull:")
            return

        role = ctx.guild.get_role(int(role_id_db[0]))
        if not role:
            await ctx.reply("Looks like the role for this club no longer exists.")
            return

        if color.startswith("0x") and len(color) == 8:
            try:
                precise_color = int(color, 16)
            except ValueError:
                await ctx.reply(f"you are using this command incorrectly")
                return
        else:
            await ctx.reply(f"you are using this command incorrectly")
            return

        try:
            await role.edit(color=precise_color)
        except discord.Forbidden:
            await ctx.reply("I do not have permissions to edit roles.")

        await ctx.reply(f"Club role color updated.")

    @commands.command(name="disband_club", brief="Abandon the club")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def disband_club(self, ctx):
        """
        Disband a club and move the channels to an archive category
        """

        async with self.bot.db.execute("SELECT category_id FROM categories WHERE setting = ? AND guild_id = ?",
                                       ["club_archive", int(ctx.guild.id)]) as cursor:
            guild_club_archive_category_id = await cursor.fetchone()
        if not guild_club_archive_category_id:
            await ctx.reply("no club archive category configured for this server")
            return

        async with self.bot.db.execute("SELECT owner_user_id FROM clubs "
                                       "WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            club_owner_check = await cursor.fetchone()

        async with self.bot.db.execute("SELECT text_channel_id, voice_channel_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            is_club_channel = await cursor.fetchone()

        if not is_club_channel:
            await ctx.reply("This is not a club")
            return

        if not (club_owner_check or await permissions.channel_manage_guild(ctx)):
            await ctx.reply(f"{ctx.author.mention} this is not your club")
            return

        archive_category = ctx.guild.get_channel(int(guild_club_archive_category_id[0]))
        if not archive_category:
            await ctx.reply("i am unable to locate the club archive category. it was probably deleted.")
            return

        voice_channel = self.bot.get_channel(int(is_club_channel[1]))

        try:
            await ctx.channel.edit(reason="club disbanded", category=archive_category)
            await voice_channel.edit(reason="club disbanded", category=archive_category)
            await ctx.reply("moved to archive")
        except (discord.Forbidden, discord.HTTPException):
            await ctx.reply("error moving channels to archive")

    @commands.command(name="rename_club", brief="Rename the club")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def rename_club(self, ctx, *, new_name: str):
        """
        Just rename the club
        """

        async with self.bot.db.execute("SELECT TRUE FROM clubs WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            is_club_owner = await cursor.fetchone()
        if not (is_club_owner or await permissions.channel_manage_guild(ctx)):
            await ctx.reply("this channel is not your club")
            return

        async with self.bot.db.execute("SELECT role_id, voice_channel_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            club_details_db = await cursor.fetchone()
        if not club_details_db:
            await ctx.reply(":skull:")
            return

        new_name = new_name.strip()

        await ctx.channel.edit(reason=None, name=new_name.replace(" ", "_").lower())

        voice_channel = self.bot.get_channel(int(club_details_db[1]))
        await voice_channel.edit(reason=None, name=new_name)

        role = ctx.guild.get_role(int(club_details_db[0]))
        await role.edit(name=new_name)

        await self.bot.db.execute("UPDATE clubs SET name = ? WHERE text_channel_id = ?",
                                  [str(new_name), int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.reply("club was renamed")

    @commands.command(name="set_club_owner", brief="Transfer club ownership to another discord account")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def set_club_owner(self, ctx, user_id: str):
        """
        Transfer the Club ownership to another Discord account.
        user_id can only be that discord account's id
        """
        async with self.bot.db.execute("SELECT TRUE FROM clubs WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            is_club_owner = await cursor.fetchone()
        if not (is_club_owner or await permissions.channel_manage_guild(ctx)):
            await ctx.reply("this channel is not your club")
            return

        if not user_id.isdigit():
            await ctx.reply("user_id must be all numbers")
            return

        member = ctx.guild.get_member(int(user_id))
        if not member:
            await ctx.reply("I can't find a member with that ID")
            return

        async with self.bot.db.execute("SELECT user_id FROM club_members WHERE user_id = ? AND text_channel_id = ?",
                                       [int(member.id), int(ctx.channel.id)]) as cursor:
            is_club_member = await cursor.fetchone()
        if not is_club_member:
            await ctx.reply("you can only transfer club ownership to a club member. make them a member first.")
            return

        await self.bot.db.execute("UPDATE clubs SET owner_user_id = ? WHERE text_channel_id = ?",
                                  [int(user_id), int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.channel.set_permissions(target=member, overwrite=self.club_owner_default_permissions)
        await ctx.reply("club owner updated for this channel")

    @commands.command(name="list_clubs", brief="List all clubs")
    @commands.check(permissions.channel_manage_guild)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def list_clubs(self, ctx):
        """
        Send an embed that contains information about all Clubs in my database
        """

        buffer = ""

        async with self.bot.db.execute("SELECT name, owner_user_id, text_channel_id, "
                                       "voice_channel_id, role_id, created_at_timestamp "
                                       "FROM clubs WHERE guild_id = ?", [(int(ctx.guild.id))]) as cursor:
            clubs = await cursor.fetchall()
        if not clubs:
            buffer += "no club channels in my database for this guild"

        for club in clubs:
            buffer += "%s by <@%s> : <#%s> + <#%s> | %s | <t:%s:R> \n" % club
            buffer += "\n"

        embed = discord.Embed(color=0xff6781)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="nuke_club", brief="Nuke a club")
    @commands.check(permissions.channel_manage_guild)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def nuke_club(self, ctx):
        """
        Nuke a requested club.
        """

        async with self.bot.db.execute("SELECT role_id, voice_channel_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            club = await cursor.fetchone()
        if not club:
            await ctx.reply("this is not a club channel")
            return

        try:
            await ctx.reply("nuking all channels and role in 5 seconds!")
            await asyncio.sleep(5)
            role = ctx.guild.get_role(int(club[0]))

            await self.bot.db.execute("DELETE FROM clubs WHERE text_channel_id = ?", [int(ctx.channel.id)])
            await self.bot.db.commit()

            await role.delete(reason="manually nuked the role due to abuse")
            await ctx.channel.delete(reason="manually nuked the channel due to abuse")

            voice_channel = self.bot.get_channel(int(club[1]))
            await voice_channel.delete(reason="manually nuked the channel due to abuse")

        except discord.Forbidden:
            await ctx.reply("no perms to do something idk")

    @commands.command(name="create_club", brief="Create a Club")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def create_club(self, ctx, *, club_name: str):
        """
        This command allows a user to create a Club.
        """

        async with self.bot.db.execute("SELECT category_id FROM categories WHERE setting = ? AND guild_id = ?",
                                       ["club", int(ctx.guild.id)]) as cursor:
            guild_club_category_id = await cursor.fetchone()

        if not guild_club_category_id:
            await ctx.reply("Not enabled in this server yet.")
            return

        await ctx.reply("sure, gimme a moment")

        club_name = club_name.strip()
        club_owner = ctx.author
        club_text_channel = None
        guild = ctx.guild

        if club_name.startswith("IMPORT_FOR:") and await permissions.channel_manage_guild(ctx):
            await ctx.reply("importing this channel as a club")
            args = club_name.split(":")
            club_owner_id = args[1]
            if not club_owner_id.isdigit():
                await ctx.reply("club_owner_id must be all numbers")
                return

            club_owner = ctx.guild.get_member(int(club_owner_id))
            if not club_owner:
                await ctx.reply("I can't find a member with that ID")
                return
            club_name = f"{club_owner.name}'s club"
            club_text_channel = ctx.channel

        club_role = await guild.create_role(
            name=club_name,
            colour=discord.Colour(random.randint(1, 16777215)),
            mentionable=True
        )

        channel_overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False,
                send_messages=False
            ),
            club_owner: self.club_owner_default_permissions,
            club_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            ),
            guild.me: self.club_bot_default_permissions
        }

        if not club_text_channel:
            club_text_channel = await guild.create_text_channel(
                name=club_name.replace(" ", "_").lower(),
                overwrites=channel_overwrites,
                category=self.bot.get_channel(int(guild_club_category_id[0]))
            )
        else:
            await club_text_channel.edit(
                name=club_name.replace(" ", "_").lower(),
                overwrites=channel_overwrites,
                category=self.bot.get_channel(int(guild_club_category_id[0]))
            )

        voice_channel = await guild.create_voice_channel(
            name=club_name,
            overwrites=channel_overwrites,
            category=self.bot.get_channel(int(guild_club_category_id[0]))
        )

        await club_owner.add_roles(club_role)

        await self.bot.db.execute("INSERT INTO clubs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  [club_name, int(club_text_channel.id), int(voice_channel.id), int(club_role.id),
                                   int(club_owner.id), 0, 0, int(time.time()), int(ctx.guild.id)])

        await self.bot.db.execute("INSERT INTO club_members VALUES (?, ?, ?, ?)",
                                  [int(club_text_channel.id), int(club_owner.id), int(time.time()), int(ctx.guild.id)])

        await self.bot.db.commit()

        await club_text_channel.send(content=f"{club_owner.mention} done! ")
        await ctx.reply("ok, i'm done!")

    @commands.command(name="set_club_privacy", brief="Set club privacy setting")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def set_club_privacy(self, ctx, privacy_str: str):
        """
        Set club privacy setting:

        - private - members only read and write
        - public-readonly - all access for members, read-only for everyone else
        - public - public read and write
        """

        async with self.bot.db.execute("SELECT TRUE FROM clubs WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            is_club_owner = await cursor.fetchone()
        if not (is_club_owner or await permissions.channel_manage_guild(ctx)):
            await ctx.reply("this channel is not your club")
            return

        async with self.bot.db.execute("SELECT voice_channel_id FROM clubs WHERE text_channel_id = ?",
                                       [int(ctx.channel.id)]) as cursor:
            club_details_db = await cursor.fetchone()
        if not club_details_db:
            await ctx.reply(":skull:")
            return

        if privacy_str.strip() == "private":
            privacy_int = 0
            text_channel_overwrite = discord.PermissionOverwrite(
                view_channel=False,
                send_messages=False
            )
            voice_channel_overwrite = discord.PermissionOverwrite(
                view_channel=False,
                send_messages=False,
                connect=False,
                speak=False
            )
        elif privacy_str.strip() == "public-readonly":
            privacy_int = 1
            text_channel_overwrite = discord.PermissionOverwrite(
                view_channel=None,
                send_messages=False
            )
            voice_channel_overwrite = discord.PermissionOverwrite(
                view_channel=None,
                send_messages=False,
                connect=False,
                speak=False
            )
        elif privacy_str.strip() == "public":
            privacy_int = 2
            text_channel_overwrite = discord.PermissionOverwrite(
                view_channel=None,
                send_messages=True
            )
            voice_channel_overwrite = discord.PermissionOverwrite(
                view_channel=None,
                send_messages=True,
                connect=True,
                speak=True
            )
        else:
            await ctx.reply("pick one: private, public-readonly, public")
            return

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=text_channel_overwrite,
        )

        voice_channel = self.bot.get_channel(int(club_details_db[0]))
        if not voice_channel:
            await ctx.reply("error, voice channel not found, skipping")
        else:
            await voice_channel.set_permissions(
                ctx.guild.default_role,
                overwrite=voice_channel_overwrite,
            )

        await self.bot.db.execute("UPDATE clubs SET public = ? WHERE text_channel_id = ?",
                                  [int(privacy_int), int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.reply("privacy settings updated")

    @commands.command(name="set_club_joinable", brief="Set club joinable setting")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def set_club_joinable(self, ctx, joinable_str: str):
        """
        Set club joinable setting:

        - disabled - disabled, club not publicly join-able
        - notify - notify club if anyone wants to join, only owner approves
        - automatic - anyone can join automatically with the command
        """

        async with self.bot.db.execute("SELECT TRUE FROM clubs WHERE owner_user_id = ? AND text_channel_id = ?",
                                       [int(ctx.author.id), int(ctx.channel.id)]) as cursor:
            is_club_owner = await cursor.fetchone()
        if not (is_club_owner or await permissions.channel_manage_guild(ctx)):
            await ctx.reply("this channel is not your club")
            return

        if joinable_str.strip() == "disabled":
            joinable_int = 0
        elif joinable_str.strip() == "notify":
            joinable_int = 1
        elif joinable_str.strip() == "automatic":
            joinable_int = 2
        else:
            await ctx.reply("pick one: disabled, notify, automatic")
            return

        await self.bot.db.execute("UPDATE clubs SET public_joinable = ? WHERE text_channel_id = ?",
                                  [int(joinable_int), int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.reply("joinable setting updated")

    @commands.command(name="join_club", brief="Join a club")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def join_club(self, ctx, *, club_name: str):
        """
        Join a club with this command, specify the club name after the command.
        """

        async with self.bot.db.execute("SELECT name, text_channel_id, voice_channel_id, role_id, "
                                       "owner_user_id, public, public_joinable, created_at_timestamp, guild_id "
                                       "FROM clubs WHERE name = ?",
                                       [str(club_name.strip())]) as cursor:
            club_details = await cursor.fetchone()
        if not club_details:
            await ctx.reply("i can't find a club with that name")
            return

        if club_details[6] == 0:
            await ctx.reply("this club not publicly join-able")
            return
        elif club_details[6] == 1:  # notify
            channel = self.bot.get_channel(int(club_details[1]))
            await channel.send(f"{ctx.author.mention} wants to join this club. "
                               f"Club owner can type `;admit {ctx.author.id}` to let them in.")

            await ctx.reply("join request sent to club.")
            return
        elif club_details[6] == 2:  # allow
            channel = self.bot.get_channel(int(club_details[1]))

            role = ctx.guild.get_role(int(club_details[3]))
            if not role:
                await ctx.reply("club role deleted, WHYYYY?")
                return

            await ctx.author.add_roles(role, reason="club member returned to the guild")

            async with self.bot.db.execute("SELECT user_id FROM club_members WHERE user_id = ? AND text_channel_id = ?",
                                           [int(ctx.author.id), int(club_details[1])]) as cursor:
                is_already_in_club = await cursor.fetchone()
            if is_already_in_club:
                await ctx.reply("the database records show you are already in the club, "
                                "but i made sure you got the club role anyways, hope this helps?")
            else:
                await self.bot.db.execute("INSERT INTO club_members VALUES (?, ?, ?, ?)",
                                          [int(club_details[1]), int(ctx.author.id), int(time.time()),
                                           int(ctx.guild.id)])
                await self.bot.db.commit()

            await ctx.reply("added you to the club!")

            await channel.send(f"{ctx.author.mention} has joined this club!")
        else:
            await ctx.reply("this setting is misconfigured for this club")
            return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, deleted_channel):
        async with self.bot.db.execute("SELECT name, text_channel_id, voice_channel_id, role_id FROM clubs "
                                       "WHERE text_channel_id = ?", [int(deleted_channel.id)]) as cursor:
            deleted_club = await cursor.fetchone()
        if not deleted_club:
            return

        await self.bot.db.execute("DELETE FROM clubs WHERE text_channel_id = ?", [int(deleted_club[1])])
        await self.bot.db.commit()
        print(f"club channel for {deleted_club[0]} was deleted")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with self.bot.db.execute("SELECT text_channel_id FROM club_members WHERE user_id = ? AND guild_id = ?",
                                       [int(member.id), int(member.guild.id)]) as cursor:
            text_channel_ids = await cursor.fetchall()
        if not text_channel_ids:
            return

        for text_channel_id in text_channel_ids:
            channel = self.bot.get_channel(int(text_channel_id[0]))
            if not channel:
                # if this is the case, the channel may have been deleted but there's still a DB record of it????
                continue

            async with self.bot.db.execute("SELECT role_id FROM clubs WHERE text_channel_id = ? AND guild_id = ?",
                                           [int(channel.id), int(member.guild.id)]) as cursor:
                role_id = await cursor.fetchone()
            if not role_id:
                continue

            role = channel.guild.get_role(int(role_id[0]))
            if not role:
                # if this is the case, the role may have been deleted but there's still a DB record of it????
                continue

            await member.add_roles(role, reason="club member returned to the guild")
            await channel.send(f"{member.display_name} has returned to the server "
                               f"and was automatically put back in this club")

            async with self.bot.db.execute("SELECT owner_user_id FROM clubs "
                                           "WHERE text_channel_id = ? AND owner_user_id = ? AND guild_id = ?",
                                           [int(channel.id), int(member.id), int(member.guild.id)]) as cursor:
                is_owner = await cursor.fetchone()
            if is_owner:
                await channel.set_permissions(target=member, overwrite=self.club_owner_default_permissions)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async with self.bot.db.execute("SELECT text_channel_id, voice_channel_id, owner_user_id FROM clubs "
                                       "WHERE owner_user_id = ? AND guild_id = ?",
                                       [int(member.id), int(member.guild.id)]) as cursor:
            clubs_user_owns = await cursor.fetchall()
        if not clubs_user_owns:
            return

        for club in clubs_user_owns:
            text_channel = self.bot.get_channel(int(club[0]))
            # voice_channel = self.bot.get_channel(int(club[1]))
            if not text_channel:
                # this should never happen
                continue

            await text_channel.send(f"{member.display_name}, the club owner has left the server")

            # async with self.bot.db.execute("SELECT category_id FROM categories WHERE setting = ? AND guild_id = ?",
            #                                ["club_archive", int(member.guild.id)]) as cursor:
            #     guild_club_archive_category_id = await cursor.fetchone()
            # if not guild_club_archive_category_id:
            #     continue

            # archive_category = self.bot.get_channel(int(guild_club_archive_category_id[0]))
            # await text_channel.edit(reason=None, category=archive_category)
            # await voice_channel.edit(reason=None, category=archive_category)
            # await text_channel.send("channel archived")

            async with self.bot.db.execute("SELECT user_id FROM club_members "
                                           "WHERE text_channel_id = ? AND guild_id = ? AND user_id != ?",
                                           [int(text_channel.id), int(member.guild.id), 0]) as cursor:
                next_club_owner = await cursor.fetchone()
            if next_club_owner:
                new_owner = member.guild.get_member(int(next_club_owner[0]))
                if new_owner:
                    await self.bot.db.execute("UPDATE clubs SET owner_user_id = ? WHERE text_channel_id = ?",
                                              [int(new_owner.id), int(text_channel.id)])
                    await text_channel.send(f"i have chosen {new_owner.mention} as the next club owner")
                    await text_channel.set_permissions(target=new_owner, overwrite=self.club_owner_default_permissions)
                return


async def setup(bot):
    await bot.db.execute("""
        CREATE TABLE IF NOT EXISTS "clubs" (
            "name"    TEXT NOT NULL,
            "text_channel_id"    INTEGER NOT NULL UNIQUE,
            "voice_channel_id"    INTEGER NOT NULL UNIQUE,
            "role_id"    INTEGER NOT NULL UNIQUE,
            "owner_user_id"    INTEGER NOT NULL,
            "public"    INTEGER NOT NULL,
            "public_joinable"    INTEGER NOT NULL,
            "created_at_timestamp"    INTEGER NOT NULL,
            "guild_id"    INTEGER NOT NULL
        )
        """)
    await bot.db.execute("""
        CREATE TABLE IF NOT EXISTS "club_members" (
            "text_channel_id"    INTEGER NOT NULL,
            "user_id"    INTEGER NOT NULL,
            "member_since_timestamp"    INTEGER NOT NULL,
            "guild_id"    INTEGER NOT NULL
        )
        """)
    await bot.add_cog(Clubs(bot))
