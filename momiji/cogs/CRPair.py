import discord
from discord.ext import commands


class CRPair(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        async with self.bot.db.execute("SELECT response_id FROM cr_pair WHERE command_id = ?",
                                       [int(payload.message_id)]) as cursor:
            lookup = await cursor.fetchone()
        if not lookup:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            response_message = await channel.fetch_message(int(lookup[0]))
            await response_message.delete()
        except discord.NotFound:
            pass

        await self.bot.db.execute("DELETE FROM cr_pair WHERE command_id = ?", [int(payload.message_id)])
        await self.bot.db.commit()


async def setup(bot):
    await bot.add_cog(CRPair(bot))
