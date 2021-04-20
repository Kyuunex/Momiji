from momiji.modules import permissions
from discord.ext import commands


class AIMod(commands.Cog):
    """
    This module is about automatic message moderation.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="aimod_add", brief="Ban a word")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def aimod_add(self, ctx, *, word):
        """
        This command will add a passed string into a blacklist.
        Every message will be checked for this string,
        and if the message contains this string,
        the message will be automatically deleted.
        Checks are case-insensitive.
        """

        if ctx.guild:
            guild_id = ctx.guild.id
        else:
            guild_id = 0

        try:
            await ctx.message.delete()
        except:
            pass

        await self.bot.db.execute("INSERT INTO aimod_blacklist VALUES (?, ?, ?)",
                                  [(str(word).lower().strip()), int(guild_id), 1])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:", delete_after=3)

    @commands.command(name="aimod_remove", brief="Unban a word")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def aimod_remove(self, ctx, *, word):
        """
        Un-blacklist a previously blacklisted string.
        """

        if ctx.guild:
            guild_id = ctx.guild.id
        else:
            guild_id = 0

        await self.bot.db.execute("DELETE FROM aimod_blacklist WHERE word = ?",
                                  [(str(word).lower().strip()), int(guild_id)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    async def content_filter(self, message):
        async with await self.bot.db.execute("SELECT word, action FROM aimod_blacklist "
                                             "WHERE guild_id = ? OR guild_id = 0", [int(message.guild.id)]) as cursor:
            aimod_blacklist = await cursor.fetchall()

        for word in aimod_blacklist:
            if not (word[0] in message.content.lower()):
                continue

            try:
                await self.perform_actions(message, word[1])
            except Exception as e:
                print(e)

    async def perform_actions(self, message, action_id):
        if action_id == 1:
            await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        await self.content_filter(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.guild:
            return

        await self.content_filter(after)


def setup(bot):
    bot.add_cog(AIMod(bot))
