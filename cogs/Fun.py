from discord.ext import commands
import random
import discord
import pyminesweeper
from modules import wrappers
from modules import cooldown
from modules import permissions


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", brief="A very complicated roll command", description="")
    @commands.check(permissions.is_not_ignored)
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
    @commands.check(permissions.is_not_ignored)
    async def minesweeper(self, ctx, size=10):
        if not await cooldown.check(str(ctx.channel.id), "last_minesweeper_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return None

        if not 3 <= int(size) <= 19:
            await ctx.send("size range is from 3 to 19")
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

    @commands.command(name="choose", brief="", description="")
    @commands.check(permissions.is_not_ignored)
    async def choose(self, ctx, *, choices_str):
        async with ctx.channel.typing():
            if " or " in choices_str:
                choices = choices_str.split(" or ")
            elif ", " in choices_str:
                choices = choices_str.split(", ")
            else:
                await ctx.send(f"gimme more than one choice pls")
                return None

            random_choice = random.randint(0, len(choices) - 1)

            how_sure_list = [
                "definitely",
                "probably",
                "most likely",
                "i prefer",
                "i choose"
            ]
            random_sureness = random.randint(0, len(how_sure_list) - 1)

            embed = discord.Embed(color=0xff6781)
            contents = f"{how_sure_list[random_sureness]} {choices[random_choice]}"
        await wrappers.send_large_embed(ctx.channel, embed, contents)


def setup(bot):
    bot.add_cog(Fun(bot))
