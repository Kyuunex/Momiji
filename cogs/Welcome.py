import random
from modules import permissions

from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_welcome_message", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def set_welcome_message(self, ctx, *, welcome_message):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        await self.bot.db.execute("INSERT INTO welcome_messages VALUES (?,?,?)",
                                  [str(ctx.guild.id), str(ctx.channel.id), str(welcome_message)])
        await self.bot.db.commit()
        await ctx.send(":ok_hand:", delete_after=3)

    @commands.command(name="set_goodbye_message", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def set_goodbye_message(self, ctx, *, goodbye_message):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        await self.bot.db.execute("INSERT INTO goodbye_messages VALUES (?,?,?)",
                                  [str(ctx.guild.id), str(ctx.channel.id), str(goodbye_message)])
        await self.bot.db.commit()
        await ctx.send(":ok_hand:", delete_after=3)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async with self.bot.db.execute("SELECT channel_id, message FROM goodbye_messages WHERE guild_id = ?",
                                       [str(member.guild.id)]) as cursor:
            goodbye_messages = await cursor.fetchall()
        if goodbye_messages:
            right_message = random.choice(goodbye_messages)
            channel = self.bot.get_channel(int(right_message[0]))
            await channel.send(await self.make_string(right_message[1], member))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        async with self.bot.db.execute("SELECT channel_id, message FROM welcome_messages WHERE guild_id = ?",
                                       [str(member.guild.id)]) as cursor:
            welcome_messages = await cursor.fetchall()
        if welcome_messages:
            right_message = random.choice(welcome_messages)
            channel = self.bot.get_channel(int(right_message[0]))
            await channel.send(await self.make_string(right_message[1], member))

    async def make_string(self, t, m):
        return t.replace("(mention)", m.mention).replace("(server)", m.guild.name).replace("(name)", m.name)


def setup(bot):
    bot.add_cog(Welcome(bot))
