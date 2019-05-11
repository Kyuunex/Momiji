import aiohttp
import urllib.request
from urllib.parse import urlparse
import asyncio
import discord
import time
import os
import random
import imghdr
import json
from modules import dbhandler
from modules import cooldown


async def art(ctx):
    try:
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
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in art")
        print(e)


async def neko(ctx):
    try:
        if await cooldown.check(str(ctx.author.id), 'lastarttime', 1):
            url = 'https://www.nekos.life/api/v2/img/neko'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as jsonresponse:
                    imageurl = (await jsonresponse.json())['url']
                    if (len(imageurl) > 20) and ("https://cdn.nekos.life/" in imageurl):
                        await ctx.send(imageurl)
        else:
            await ctx.send('slow down bruh')
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in neko")
        print(e)


async def gis(ctx, searchquery): #TODO: fix
    try:
        if ctx.channel.is_nsfw():
            if await cooldown.check(str(ctx.author.id), 'lastimgtime', 40):
                if len(searchquery) > 0:
                    googleapikey = (await dbhandler.query(["SELECT value FROM config WHERE setting = ?", ["googleapikey"]]))
                    googlesearchengineid = (await dbhandler.query(["SELECT value FROM config WHERE setting = ?", ["googlesearchengineid"]]))
                    if googleapikey:
                        query = {
                            'q': str(searchquery),
                            'key': str(googleapikey[0][0]),
                            'searchType': 'image',
                            'cx': str(googlesearchengineid[0][0]),
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
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in img")
        print(e)