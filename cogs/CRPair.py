from discord.ext import commands


class CRPair(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        async with self.bot.db.execute("SELECT response_id FROM cr_pair WHERE command_id = ?",
                                     [str(message.id)]) as cursor:
            lookup = await cursor.fetchall()
        if lookup:
            response_message = await message.channel.fetch_message(int(lookup[0][0]))
            try:
                await response_message.delete()
            except:
                pass


def setup(bot):
    bot.add_cog(CRPair(bot))
