import aiohttp
import urllib.request
from urllib.parse import urlparse
import discord
from discord.ext import commands
import os
import random
import imghdr
from modules import cooldown
from modules import permissions


class Img(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.art_dir = "data/art/"

    @commands.command(name="art", brief="Post a random picture",
                      description="Upload a random picture from ./data/art/ folder")
    @commands.check(permissions.is_not_ignored)
    async def art(self, ctx):
        if not await cooldown.check(str(ctx.author.id), "last_art_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return None

        if not os.path.exists(self.art_dir):
            await ctx.send("This command is not enabled")
            return None

        list_of_art = os.listdir(self.art_dir)

        if len(list_of_art) == 0:
            await ctx.send("This command is not enabled")
            return None

        while True:
            random_picture = random.choice(list_of_art)
            if (random_picture.split("."))[-1] == "png" or (random_picture.split("."))[-1] == "jpg":
                break
        await ctx.send(file=discord.File(self.art_dir + random_picture))

    @commands.command(name="neko", brief="Post a random neko", description="Grab an image from nekos.life")
    @commands.check(permissions.is_not_ignored)
    async def neko(self, ctx):
        if not await cooldown.check(str(ctx.author.id), "last_art_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return None

        url = "https://www.nekos.life/api/v2/img/neko"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as json_response:
                image_url = (await json_response.json())["url"]
                if "https://cdn.nekos.life/" in image_url:
                    await ctx.send(f"|| {image_url} ||")

    @commands.command(name="gis", brief="Google image search",
                      description="Search for a phrase on Google images and post a random result")
    @commands.check(permissions.is_not_ignored)
    async def gis(self, ctx, search_query):
        # This one's for you, UC-sama

        async with self.bot.db.execute("SELECT value FROM config WHERE setting = ?", ["google_api_key"]) as cursor:
            google_api_key = await cursor.fetchall()
        async with self.bot.db.execute("SELECT value FROM config WHERE setting = ?",
                                     ["google_search_engine_id"]) as cursor:
            google_search_engine_id = await cursor.fetchall()

        if not google_api_key:
            await ctx.send("This command is not enabled")
            return None

        if not ctx.channel.is_nsfw():
            await ctx.send("This command works in NSFW channels only.")
            return None

        if not await cooldown.check(str(ctx.author.id), "last_gis_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return None

        if len(search_query) < 1:
            return None

        query = {
            "q": str(search_query),
            "key": str(google_api_key[0][0]),
            "searchType": "image",
            "cx": str(google_search_engine_id[0][0]),
            "start": str(random.randint(1, 21))
        }
        url = "https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode(query)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as json_response:
                image_url = (await json_response.json())["items"][(random.randint(0, 9))]["link"]
                if len(image_url) > 1:
                    async with aiohttp.ClientSession() as second_session:
                        async with second_session.get(image_url) as image_response:
                            buffer = (await image_response.read())
                            ext = imghdr.what("", h=buffer)
                            # if (any(c in ext for c in ["jpg", "jpeg", "png", "gif"])):
                            await ctx.send(file=discord.File(buffer, f"{search_query}.{ext}"))


def setup(bot):
    bot.add_cog(Img(bot))
