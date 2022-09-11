from discord.ext import commands
import random
import discord
import pyminesweeper
from momiji.modules import cooldown
from momiji.modules import permissions


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", brief="A very complicated roll command")
    @commands.check(permissions.is_not_ignored)
    async def roll(self, ctx, maximum="100"):
        """
        Allows a user to roll a number.
        They can roll negative or a positive number
        depending on the parameter passed in.
        """

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

        player_name = ctx.message.author.display_name.replace("@", "")
        await ctx.send(f"**{player_name}** rolls **{random_number}** {point_str}")

    @commands.command(name="minesweeper", brief="Sends a randomly generated minesweeper game")
    @commands.check(permissions.is_not_ignored)
    async def minesweeper(self, ctx, size=10):
        """
        This command sends a randomly generated minesweeper game.
        This command makes use of Discord's spoiler feature.
        """

        if not await cooldown.check(str(ctx.channel.id), "last_minesweeper_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return

        if not 3 <= int(size) <= 19:
            await ctx.send("size range is from 3 to 19")
            return

        game_instance = pyminesweeper.MinesweeperMap(int(size))
        game_instance.generate_map(int(size) // 2, int(size) // 2)
        formatted_board = await self.format_board_for_discord(game_instance)

        description = f"{int(size)} x {int(size)} Minesweeper with {game_instance.num_mines} mines\n\n"

        await self.send_game(ctx.channel, description, size, formatted_board)

    @staticmethod
    async def format_board_for_discord(game_instance):
        emotes = {
            -1: "||:boom:||",
            0: "||:zero:||",
            1: "||:one:||",
            2: "||:two:||",
            3: "||:three:||",
            4: "||:four:||",
            5: "||:five:||",
            6: "||:six:||",
            7: "||:seven:||",
            8: "||:eight:||"
        }
        buffer = ""
        for i in range(game_instance.size):
            for j in range(game_instance.size):
                buffer += emotes[int(game_instance.map[i][j].val)]
            buffer += "\n"
        return buffer

    @staticmethod
    async def send_game(channel, description, size, formatted_board):
        return_messages = []
        content_lines = formatted_board.splitlines(True)
        output = description
        boxes = 0
        for line in content_lines:
            if boxes >= 81:
                return_messages.append(await channel.send(output))
                output = ""
                boxes = 0
            output += line
            boxes += size
        if boxes > 0:
            return_messages.append(await channel.send(output))
        return return_messages

    @commands.command(name="choose", brief="Momiji will solve a dilemma for you")
    @commands.check(permissions.is_not_ignored)
    async def choose(self, ctx, *, choices_str):
        """
        Can't decide on something? Momiji is here to help!
        Passed in parameters must be separated with " or " or ", " for this for work.
        """

        async with ctx.channel.typing():
            if " or " in choices_str:
                choices = choices_str.split(" or ")
            elif ", " in choices_str:
                choices = choices_str.split(", ")
            else:
                await ctx.send(f"gimme more than one choice pls")
                return

            how_sure_list = [
                "definitely",
                "probably",
                "most likely",
                "i prefer",
                "i choose"
            ]

            contents = f"{random.choice(how_sure_list)} {random.choice(choices)}"
            embed = discord.Embed(description=contents, color=0xff6781)

        response_msg = await ctx.send(content=ctx.author.mention, embed=embed)
        await self.bot.db.execute("INSERT INTO cr_pair VALUES (?, ?)", [int(ctx.message.id), int(response_msg.id)])
        await self.bot.db.commit()


def setup(bot):
    bot.add_cog(Fun(bot))
