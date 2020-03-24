from discord.ext import commands
import random
import pyminesweeper
from modules import wrappers


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

    @commands.command(name="minesweeper", brief="Sends a randomly generated minesweeper game", description="")
    async def minesweeper(self, ctx, size=10):
        if not 3 < int(size) < 20:
            await ctx.send("size must be between 3 and 20")
            return None

        instance = pyminesweeper.MinesweeperMap(int(size))
        instance.generate_map(int(size) // 2, int(size) // 2)
        board_str = instance.map_revealed()\
            .replace("X", "||:boom:||")\
            .replace(" ", "")\
            .replace("0", "||:zero:||")\
            .replace("1", "||:one:||")\
            .replace("2", "||:two:||")\
            .replace("3", "||:three:||")\
            .replace("4", "||:four:||")\
            .replace("5", "||:five:||")\
            .replace("6", "||:six:||")\
            .replace("7", "||:seven:||")\
            .replace("8", "||:eight:||")

        output = f"{int(size)} x {int(size)} Minesweeper with {instance.num_mines} mines\n\n{board_str}"

        await wrappers.send_large_text(ctx.channel, output)


def setup(bot):
    bot.add_cog(Misc(bot))
