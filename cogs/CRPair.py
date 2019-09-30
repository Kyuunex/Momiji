from modules import db
import discord
from discord.ext import commands

class CRPair(commands.Cog, name="CRPair"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        lookup = db.query(["SELECT response_id FROM cr_pair WHERE command_id = ?", [str(message.id)]])
        if lookup:
            response_message = await message.channel.fetch_message(int(lookup[0][0]))
            try:
                await response_message.delete()
            except:
                print("can't delete")

def setup(bot):
    bot.add_cog(CRPair(bot))