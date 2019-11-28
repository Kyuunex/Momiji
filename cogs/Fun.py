from discord.ext import commands
import random


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", brief="A very complicated roll command", description="")
    async def roll(self, ctx, maximum="100"):
        who = ctx.message.author.display_name.replace("@", "")
        try:
            maximum = int(maximum)
        except:
            maximum = 100
        if maximum < 0:
            random_number = random.randint(maximum, 0)
        else:
            random_number = random.randint(0, maximum)
        if random_number == 1:
            point_str = "point"
        else:
            point_str = "points"
        await ctx.send(f"**{who}** rolls **{random_number}** {point_str}")


def setup(bot):
    bot.add_cog(Misc(bot))
