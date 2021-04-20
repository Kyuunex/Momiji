from discord.ext import commands
from momiji.modules import permissions


class UserPreferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_timezone", brief="Set your timezone")
    @commands.check(permissions.is_not_ignored)
    async def set_timezone(self, ctx, offset):
        """
        Let the bot know which timezone you are in
        so the bot can offset time related messages accordingly

        example:
        ;set_timezone -8 [this sets your timezone to -8:00]
        ;set_timezone 3.5 [this sets your timezone to +3:30]
        """

        await self.bot.db.execute("INSERT OR REPLACE INTO user_timezones VALUES (?, ?)",
                                  [int(ctx.author.id), int(offset)])
        await self.bot.db.commit()

        await ctx.send(f"your timezone has been updated!")


def setup(bot):
    bot.add_cog(UserPreferences(bot))
