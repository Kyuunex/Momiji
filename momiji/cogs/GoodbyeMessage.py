import random
import discord
from momiji.modules import permissions
from momiji.reusables import send_large_message

from discord.ext import commands


class GoodbyeMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_goodbye_message", brief="Set a goodbye message")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def set_goodbye_message(self, ctx, *, goodbye_message):
        """
        Set a goodbye message in the channel this command is being called in.
        The message will be deleted.

        Example message:
        (name) has disappeared from (server), never to be seen again...
        """

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        await self.bot.db.execute("INSERT INTO goodbye_messages VALUES (?,?,?)",
                                  [int(ctx.guild.id), int(ctx.channel.id), str(goodbye_message)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:", delete_after=3)

    @commands.command(name="remove_goodbye_message", brief="Remove all goodbye messages")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def remove_goodbye_message(self, ctx):
        """
        Remove all goodbye messages from the channel this command is called in.
        The message will be deleted.
        """

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        await self.bot.db.execute("DELETE FROM goodbye_messages WHERE channel_id = ?", [int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:", delete_after=3)

    @commands.command(name="get_goodbye_messages", brief="Get all goodbye messages")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def get_goodbye_messages(self, ctx):
        """
        Prints out all goodbye messages in this guild.
        """

        async with self.bot.db.execute("SELECT channel_id, message FROM goodbye_messages WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            goodbye_messages = await cursor.fetchall()

        buffer = ":wave: **Goodbye messages in this guild.**\n\n"

        if goodbye_messages:
            for one_goodbye_message in goodbye_messages:
                buffer += f"<#{one_goodbye_message[0]}> | message:\n"
                buffer += "```\n"
                buffer += f"{one_goodbye_message[1]}\n"
                buffer += "```\n"
                buffer += "\n"
        else:
            buffer += "**Goodbye message list in this server is empty**\n"

        embed = discord.Embed(color=0xf76a8c)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # TODO: using this logic,
        #  if there are multiple goodbye messages in different channels,
        #  it may be a problem

        async with self.bot.db.execute("SELECT channel_id, message FROM goodbye_messages WHERE guild_id = ?",
                                       [int(member.guild.id)]) as cursor:
            goodbye_messages = await cursor.fetchall()
        if not goodbye_messages:
            return

        random_message = random.choice(goodbye_messages)

        channel = self.bot.get_channel(int(random_message[0]))
        await channel.send(await self.make_string(random_message[1], member))

    async def make_string(self, message_template, member):
        return message_template.replace("(mention)", member.mention)\
            .replace("(server)", member.guild.name)\
            .replace("(name)", member.name)


async def setup(bot):
    await bot.add_cog(GoodbyeMessage(bot))
