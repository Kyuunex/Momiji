import aiohttp
import discord
from discord.ext import commands
import os
import random
from momiji.modules import cooldown
from momiji.modules import permissions
from momiji.modules.storage_management import BOT_ART_DIRECTORY


class Img(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="art", brief="Post a random picture")
    @commands.check(permissions.is_not_ignored)
    async def art(self, ctx):
        """
        Upload a random picture from ~/.local/share/Momiji/art/ folder
        """
        if not await cooldown.check(str(ctx.author.id), "last_art_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return

        if not os.path.exists(BOT_ART_DIRECTORY):
            await ctx.send("This command is not enabled")
            return

        list_of_art = os.listdir(BOT_ART_DIRECTORY)

        if len(list_of_art) == 0:
            await ctx.send("This command is not enabled")
            return

        count = 0
        while True:
            random_picture = random.choice(list_of_art)
            file_extension = (random_picture.split("."))[-1]
            if file_extension == "png" or file_extension == "jpg":
                break

            count += 1

            if count > 10:
                await ctx.send("i tried 10 times to find an image to post for you something went wrong...")
                return

        await ctx.send(file=discord.File(os.path.join(BOT_ART_DIRECTORY, random_picture)))

    @commands.command(name="neko", brief="Post a random neko")
    @commands.check(permissions.is_not_ignored)
    async def neko(self, ctx, tag="neko"):
        """
        Grab an image from nekos.life
        Seriously though? WHY ARE THESE NOT REAL??????
        """

        if not await cooldown.check(str(ctx.author.id), "last_art_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return

        if tag != "neko" and not ctx.channel.is_nsfw():
            await ctx.send("Tags other than `neko` only work in a NSFW channel.")
            return

        url = f"https://www.nekos.life/api/v2/img/{tag}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as json_response:
                api_response = await json_response.json()

        if not api_response:
            return

        image_url = api_response["url"]
        if not "https://cdn.nekos.life/" in image_url:
            return

        await ctx.send(f"|| {image_url} ||")

    @commands.command(name="gis", brief="Google image search")
    @commands.check(permissions.is_not_ignored)
    async def gis(self, ctx, search_query):
        """
        Search for a phrase on Google images and post a random result
        """
        # This one's for you, UC-sama

        async with self.bot.db.execute("SELECT key FROM api_keys WHERE service = ?", ["google_api_key"]) as cursor:
            google_api_key = await cursor.fetchone()
        async with self.bot.db.execute("SELECT key FROM api_keys WHERE service = ?",
                                       ["google_search_engine_id"]) as cursor:
            google_search_engine_id = await cursor.fetchone()

        if not google_api_key:
            await ctx.send("This command is not enabled")
            return

        if not ctx.channel.is_nsfw():
            await ctx.send("This command works in NSFW channels only.")
            return

        if not await cooldown.check(str(ctx.author.id), "last_gis_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return

        if len(search_query) < 1:
            return

        query = {
            "q": str(search_query),
            "key": str(google_api_key[0]),
            "searchType": "image",
            "cx": str(google_search_engine_id[0]),
            "start": str(random.randint(1, 5))
        }

        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.googleapis.com/customsearch/v1", params=query) as json_response:
                response_dict = await json_response.json()
                if "error" in response_dict:
                    await ctx.send(response_dict["error"]["message"])
                    return
                items = response_dict["items"]
                random_item_id = random.randint(0, 9)
                image_url = items[random_item_id]["link"]
                await ctx.send(image_url)

        # if len(image_url) > 1:
        #     async with aiohttp.ClientSession() as second_session:
        #         async with second_session.get(image_url) as image_response:
        #             buffer = await image_response.read()
        #             ext = imghdr.what("", h=buffer)
        #             # if (any(c in ext for c in ["jpg", "jpeg", "png", "gif"])):
        #             await ctx.send(file=discord.File(buffer, f"{search_query}.{ext}"))


async def setup(bot):
    await bot.add_cog(Img(bot))
