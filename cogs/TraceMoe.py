# TODO: improve this
import aiohttp
from discord.ext import commands
import time
import urllib.request
import urllib
from modules import cooldown
from modules import permissions


class TraceMoe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://trace.moe/api"

    @commands.command(name="sauce", brief="What anime is this?", aliases=["what_anime"])
    async def sauce(self, ctx):
        """
        Attach an image to the message containing the command to look it up
        """

        if not await cooldown.check(str(ctx.author.id), "last_trace_time", 600):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return None

        if not ctx.message.attachments:
            await ctx.send("the message has no attachments")
            return None

        attachment = ctx.message.attachments[0]

        search_results = await self.search(attachment.url)

        if not search_results:
            await ctx.send("nothing found")
            return None

        first_result = search_results['docs'][0]
        await ctx.send(f"the anime seems to be `{first_result['title_english']}`, "
                       f"which came out in `{first_result['season']}`")

    async def request(self, query):
        try:
            url = self.base_url+"/search?"+urllib.parse.urlencode(query)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()
        except Exception as e:
            print(time.strftime("%X %x %Z"))
            print("in request")
            print(e)
            return None

    async def search(self, url):
        query = {
            "url": url,
        }
        request_object = await self.request(query)
        if request_object:
            return request_object
        else:
            return None


def setup(bot):
    bot.add_cog(TraceMoe(bot))
