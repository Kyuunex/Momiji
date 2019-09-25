import aiohttp
import urllib.request
from urllib.parse import urlparse
import discord
from discord.ext import commands
import os
import random
import imghdr
import json
from modules import db
from modules import cooldown

class Img(commands.Cog, name="Picture related commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="art", brief="", description="", pass_context=True)
    async def art(self, ctx):
        if await cooldown.check(str(ctx.author.id), 'lastarttime', 40):
            artdir = "data/art/"
            if os.path.exists(artdir):
                a = True
                while a:
                    randompicture = random.choice(os.listdir(artdir))
                    if (randompicture.split("."))[-1] == "png" or (randompicture.split("."))[-1] == "jpg":
                        a = False
                await ctx.send(file=discord.File(artdir+randompicture))
        else:
            await ctx.send('slow down bruh')

    @commands.command(name="neko", brief="", description="", pass_context=True)
    async def neko(self, ctx):
        if await cooldown.check(str(ctx.author.id), 'lastarttime', 40):
            url = 'https://www.nekos.life/api/v2/img/neko'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as jsonresponse:
                    imageurl = (await jsonresponse.json())['url']
                    if (len(imageurl) > 20) and ("https://cdn.nekos.life/" in imageurl):
                        await ctx.send(imageurl)
        else:
            await ctx.send('slow down bruh')

    @commands.command(name="gis", brief="", description="", pass_context=True)
    async def gis(self, ctx, searchquery):
        if ctx.channel.is_nsfw():
            if await cooldown.check(str(ctx.author.id), 'lastimgtime', 40):
                if len(searchquery) > 0:
                    google_api_key = (db.query(["SELECT value FROM config WHERE setting = ?", ["google_api_key"]]))
                    google_search_engine_id = (db.query(["SELECT value FROM config WHERE setting = ?", ["google_search_engine_id"]]))
                    if google_api_key:
                        query = {
                            'q': str(searchquery),
                            'key': str(google_api_key[0][0]),
                            'searchType': 'image',
                            'cx': str(google_search_engine_id[0][0]),
                            'start': str(random.randint(1, 21))
                        }
                        url = "https://www.googleapis.com/customsearch/v1?" + \
                            urllib.parse.urlencode(query)

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as jsonresponse:
                                imageurl = (await jsonresponse.json())['items'][(random.randint(0, 9))]['link']
                                if len(imageurl) > 1:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(imageurl) as imageresponse:
                                            buffer = (await imageresponse.read())
                                            ext = imghdr.what("", h=buffer)
                                            # if (any(c in ext for c in ["jpg", "jpeg", "png", "gif"])):
                                            await ctx.send(file=discord.File(buffer, "%s.%s" % (searchquery, ext)))
                    else:
                        await ctx.send("This command is not enabled")
            else:
                await ctx.send('slow down bruh')
        else:
            await ctx.send("This command works in NSFW channels only.")

def setup(bot):
    bot.add_cog(Img(bot))