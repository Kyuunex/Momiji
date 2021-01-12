import random
import discord
from modules import permissions
from reusables import send_large_message

from discord.ext import commands


class WelcomeMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_welcome_message", brief="Set a welcome message")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def set_welcome_message(self, ctx, *, welcome_message):
        """
        Set a welcome message in the channel this command is being called in.
        The message will be deleted.

        Example message:
        (mention) has just joined (server)! Seeing a new member fills you with determination!
        """

        try:
            await ctx.message.delete()
        except:
            pass

        await self.bot.db.execute("INSERT INTO welcome_messages VALUES (?,?,?)",
                                  [int(ctx.guild.id), int(ctx.channel.id), str(welcome_message)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:", delete_after=3)

    @commands.command(name="remove_welcome_message", brief="Remove all welcome messages")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def remove_welcome_message(self, ctx):
        """
        Remove all welcome messages from the channel this command is called in.
        The message will be deleted.
        """

        try:
            await ctx.message.delete()
        except:
            pass

        await self.bot.db.execute("DELETE FROM welcome_messages WHERE channel_id = ?", [int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:", delete_after=3)

    @commands.command(name="get_welcome_messages", brief="Get all welcome messages")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def get_welcome_messages(self, ctx):
        """
        Prints out all welcome messages in this guild.
        """

        async with self.bot.db.execute("SELECT channel_id, message FROM welcome_messages WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            welcome_messages = await cursor.fetchall()

        buffer = ":wave: **Welcome messages in this guild.**\n\n"

        if welcome_messages:
            for one_welcome_message in welcome_messages:
                buffer += f"<#{one_welcome_message[0]}> | message:\n"
                buffer += "```\n"
                buffer += f"{one_welcome_message[1]}\n"
                buffer += "```\n"
                buffer += "\n"
        else:
            buffer += "**Welcome message list in this server is empty**\n"

        embed = discord.Embed(color=0xf76a8c)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # TODO: using this logic,
        #  if there are multiple welcome messages in different channels,
        #  it may be a problem

        async with self.bot.db.execute("SELECT channel_id, message FROM welcome_messages WHERE guild_id = ?",
                                       [int(member.guild.id)]) as cursor:
            welcome_messages = await cursor.fetchall()
        if not welcome_messages:
            return

        right_message = random.choice(welcome_messages)

        channel = self.bot.get_channel(int(right_message[0]))
        await channel.send(await self.make_string(right_message[1], member))

    async def make_string(self, message_template, member):
        return message_template.replace("(mention)", member.mention)\
            .replace("(server)", member.guild.name)\
            .replace("(name)", member.name)


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
