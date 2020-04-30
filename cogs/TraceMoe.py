import aiohttp
from discord.ext import commands
import discord
import urllib.request
import urllib.parse
import urllib
from modules import cooldown
from modules import permissions


class TraceMoe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = TraceMoeApi()

    @commands.command(name="sauce", brief="What anime is this?", aliases=["what_anime"])
    @commands.check(permissions.is_not_ignored)
    async def sauce(self, ctx):
        """
        Attach an image to the message containing the command to look it up
        """

        if not await cooldown.check(str(ctx.author.id), "last_trace_time", 600):
            if not await permissions.is_admin(ctx):
                await ctx.send("one use per 10 minutes per user")
                return None

        if not ctx.message.attachments:
            await ctx.send("the message has no attachments")
            return None

        async with ctx.channel.typing():
            attachment = ctx.message.attachments[0]

            search_results = await self.api.search(url=attachment.url)

            if not search_results:
                await ctx.send("nothing found")
                return None

            first_result = search_results.docs[0]
            embed = TraceEmbeds.result(first_result)
        await ctx.send(embed=embed)


class TraceEmbeds:
    @staticmethod
    def result(result):
        if result:
            description = f"Episode: {result.episode}\n"
            description += f"Season: {result.season}\n"
            description += f"Similarity: {result.similarity}\n"
            description += f"NSFW: {str(result.is_adult)}"

            embed = discord.Embed(
                description=description,
                title=result.title_romaji,
                url=f"https://anilist.co/anime/{result.anilist_id}",
                color=0xAD6F49,
            )
            if not result.is_adult:
                embed.set_image(url=result.thumbnail_url)
            return embed
        else:
            return None


class Result:
    def __init__(self, result):
        self.fromm = result["from"]
        self.to = result["to"]
        self.anilist_id = result["anilist_id"]
        self.at = result["at"]
        self.season = result["season"]
        self.anime = result["anime"]
        self.filename = result["filename"]
        self.episode = result["episode"]
        self.tokenthumb = result["tokenthumb"]
        self.similarity = result["similarity"]
        self.title = result["title"]
        self.title_native = result["title_native"]
        self.title_chinese = result["title_chinese"]
        self.title_english = result["title_english"]
        self.title_romaji = result["title_romaji"]
        self.mal_id = result["mal_id"]

        self.synonyms = []
        for synonym in result["synonyms"]:
            self.synonyms.append(synonym)

        self.synonyms_chinese = []
        for synonym_chinese in result["synonyms_chinese"]:
            self.synonyms_chinese.append(synonym_chinese)

        self.is_adult = result["is_adult"]
        thumbnail_args = {
            "anilist_id": self.anilist_id,
            "file": self.filename,
            "t": self.at,
            "token": self.tokenthumb,
        }
        self.thumbnail_url = "https://trace.moe/thumbnail.php?"+urllib.parse.urlencode(thumbnail_args)

    def __str__(self):
        return self.title_romaji


class SearchResponse:
    def __init__(self, search_response):
        self.RawDocsCount = search_response["RawDocsCount"]
        self.RawDocsSearchTime = search_response["RawDocsSearchTime"]
        self.ReRankSearchTime = search_response["ReRankSearchTime"]
        self.CacheHit = search_response["CacheHit"]
        self.trial = search_response["trial"]
        self.limit = search_response["limit"]
        self.limit_ttl = search_response["limit_ttl"]
        self.quota = search_response["quota"]
        self.quota_ttl = search_response["quota_ttl"]
        self.docs = []
        for doc in search_response["docs"]:
            self.docs.append(Result(doc))


class TraceMoeApi:
    def __init__(self, token=""):
        self._base_url = "https://trace.moe/api/"

    async def _raw_request(self, endpoint, parameters):
        url = self._base_url + endpoint + "?" + urllib.parse.urlencode(parameters)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_json = await response.json()
                return response_json

    async def search(self, **kwargs):
        result = await self._raw_request("search", kwargs)
        if result:
            return SearchResponse(result)
        else:
            return None


def setup(bot):
    bot.add_cog(TraceMoe(bot))
