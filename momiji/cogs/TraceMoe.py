from discord.ext import commands
from momiji.modules import cooldown
from momiji.modules import permissions
from momiji.apiwrappers.TraceMoe import *


class TraceMoe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = TraceMoeApi()

    @commands.command(name="sauce", brief="What anime is this?", aliases=["what_anime"])
    @commands.check(permissions.is_not_ignored)
    async def sauce(self, ctx, url=""):
        """
        Attach an image to the message containing the command to look it up
        """

        if not ctx.message.attachments and not (url and await permissions.is_admin(ctx)):
            await ctx.send("the message has no attachments")
            return

        if not await cooldown.check(str(ctx.author.id), "last_trace_time", 600):
            if not await permissions.is_admin(ctx):
                await ctx.send("one use per 10 minutes per user")
                return

        async with ctx.channel.typing():
            if url and await permissions.is_admin(ctx):
                search_results = await self.api.search(url=url)
            else:
                attachment = ctx.message.attachments[0]
                search_results = await self.api.search(url=attachment.url)

            if not search_results:
                await ctx.send("nothing found")
                return

            first_result = search_results.result[0]
            # embed = TraceEmbeds.result(first_result)

            response = f"|| https://anilist.co/anime/{first_result.anilist}/ ||"

            if first_result.episode:
                response += f"\nEpisode {str(first_result.episode)}"

        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(TraceMoe(bot))
