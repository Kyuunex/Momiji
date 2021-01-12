from discord.ext import commands
import discord
import time
import datetime
from modules import permissions
from reusables import get_member_helpers


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge", brief="Purge X amount of messages")
    @commands.guild_only()
    @commands.check(permissions.channel_manage_messages)
    @commands.check(permissions.is_not_ignored)
    async def purge(self, ctx, amount, *authors):
        """
        The purge command

        amount: amount of messages to cycle through
        authors: optional mention(s) of users this purge should only apply to
        """

        if not amount.isdigit():
            await ctx.send("the amount specified must be a number")
            return

        try:
            await ctx.message.delete()

            if len(ctx.message.mentions) > 0:
                for one_member in ctx.message.mentions:
                    async with ctx.channel.typing():
                        def is_user(member):
                            return member.author == one_member

                        deleted = await ctx.channel.purge(limit=int(amount), check=is_user)
                    await ctx.send(f"Deleted {len(deleted)} message(s) by {one_member.display_name}")
            else:
                async with ctx.channel.typing():
                    deleted = await ctx.channel.purge(limit=int(amount))
                await ctx.send(f"Deleted {len(deleted)} message(s)")
        except Exception as e:
            await ctx.send(str(e).replace("@", ""))

    @commands.command(name="regex_purge", brief="Purge X amount of messages with regex checks")
    @commands.guild_only()
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def regex_purge(self, ctx, amount, string):
        """
        Purge messages based on their content aligning with the regex string
        
        amount: amount of messages to cycle through
        string: the regex string
        """

        if not amount.isdigit():
            await ctx.send("the amount specified must be a number")
            return

        try:
            await ctx.message.delete()

            async with ctx.channel.typing():
                def the_check(message):
                    # TODO: actually do some regex checks
                    return string in message.content

                deleted = await ctx.channel.purge(limit=int(amount), check=the_check)
            await ctx.send(f"Deleted {len(deleted)} message(s)")
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="mod_note", brief="Add a mod note about a server member")
    @commands.guild_only()
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    async def mod_note(self, ctx, user_id, *, note):
        """
        Stores information about a specific server member in the database for later retrieval

        user_id: user_id, name or nickname
        note: the note to store
        """

        member = get_member_helpers.get_member_guaranteed(ctx, user_id)

        if not member:
            await ctx.send("no member found with that name")
            return

        await self.bot.db.execute("INSERT INTO mod_notes VALUES (?, ?, ?, ?)",
                                  [int(ctx.guild.id), int(member.id), note, int(time.time())])
        await self.bot.db.commit()

        await ctx.send(f"note added for {member.name}")

    @commands.command(name="mod_notes", brief="Print mod notes")
    @commands.guild_only()
    @commands.check(permissions.channel_ban_members)
    @commands.check(permissions.is_not_ignored)
    async def mod_notes(self, ctx, *, user_id=""):
        """
        Print mod notes for this server
        
        user_id: filter by a specific user
        """

        # TODO: Currently, this may break if we try to filter out with an ID of a user who left. fix

        async with self.bot.db.execute("SELECT guild_id, user_id, note, timestamp FROM mod_notes "
                                       "WHERE guild_id = ?", [int(ctx.guild.id)]) as cursor:
            all_mod_notes = await cursor.fetchall()

        if user_id:
            check_member = get_member_helpers.get_member_guaranteed(ctx, user_id)
        else:
            check_member = None

        for one_note in all_mod_notes:
            if check_member:
                if check_member.id != int(one_note[1]):
                    continue
            member = ctx.guild.get_member(int(one_note[1]))
            timestamp = datetime.datetime.utcfromtimestamp(int(one_note[3]))
            embed = await self.mod_noted_member(member, one_note[2], timestamp)
            await ctx.send(embed=embed)

    async def mod_noted_member(self, member, note, timestamp):
        if member:
            embed = discord.Embed(
                description=note,
                color=member.colour.value
            )
            embed.set_author(
                name=member.display_name,
                icon_url=member.avatar_url
            )
            embed.set_footer(
                text=f"Noted on {timestamp}"
            )
            embed.add_field(name="member", value=member.mention, inline=False)
            embed.add_field(name="user_id", value=member.id, inline=False)
            embed.add_field(name="member_name", value=f"{member.name}#{member.discriminator}", inline=False)
            return embed
        else:
            return None


def setup(bot):
    bot.add_cog(Moderation(bot))
