import discord
from discord.ext import commands


class CRPair(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # TODO: maybe use raw version of this at some point?
        async with self.bot.db.execute("SELECT response_id FROM cr_pair WHERE command_id = ?",
                                       [int(message.id)]) as cursor:
            lookup = await cursor.fetchone()
        if not lookup:
            return

        response_message = await message.channel.fetch_message(int(lookup[0]))
        if not response_message:
            return

        try:
            await response_message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass
        await self.bot.db.execute("DELETE FROM cr_pair WHERE command_id = ?", [int(message.id)])
        await self.bot.db.commit()


async def setup(bot):
    await bot.add_cog(CRPair(bot))
