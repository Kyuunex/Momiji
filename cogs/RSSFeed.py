import feedparser
import aiohttp
import time
import asyncio
import discord
from discord.ext import commands
import re
from html import unescape

from modules import permissions
from modules import wrappers


class RSSFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.background_tasks.append(
            self.bot.loop.create_task(self.rssfeed_background_loop())
        )

    @commands.command(name="rss_add", brief="Subscribe to an RSS feed in the current channel", description="")
    @commands.check(permissions.is_admin)
    async def add(self, ctx, *, url):
        feed_entries = (feedparser.parse(await self.fetch(url)))["entries"]
        if not feed_entries:
            await ctx.send("can't check to this url")
            return None

        async with await self.bot.db.execute("SELECT * FROM rssfeed_tracklist WHERE url = ?", [str(url)]) as cursor:
            check_is_already_tracked = await cursor.fetchall()
        if not check_is_already_tracked:
            await self.bot.db.execute("INSERT INTO rssfeed_tracklist VALUES (?)", [str(url)])

        for entry_metadata in feed_entries:
            entry_id = entry_metadata["link"]
            async with await self.bot.db.execute("SELECT * FROM rssfeed_history WHERE url = ? AND entry_id = ?",
                                                 [str(url), str(entry_id)]) as cursor:
                check_is_entry_in_history = await cursor.fetchall()
            if not check_is_entry_in_history:
                await self.bot.db.execute("INSERT INTO rssfeed_history VALUES (?, ?)", [str(url), str(entry_id)])

        await self.bot.db.commit()

        async with await self.bot.db.execute("SELECT * FROM rssfeed_channels WHERE channel_id = ? AND url = ?",
                                             [str(ctx.channel.id), str(url)]) as cursor:
            check_is_channel_already_tracked = await cursor.fetchall()
        if check_is_channel_already_tracked:
            await ctx.send(f"Feed `{url}` is already tracked in this channel")
            return None

        await self.bot.db.execute("INSERT INTO rssfeed_channels VALUES (?, ?)", [str(url), str(ctx.channel.id)])
        await ctx.send(f"Feed `{url}` is now tracked in this channel")
        await self.bot.db.commit()

    @commands.command(name="rss_remove", brief="Unsubscribe to an RSS feed in the current channel", description="")
    @commands.check(permissions.is_admin)
    async def remove(self, ctx, *, url):
        await self.bot.db.execute("DELETE FROM rssfeed_channels WHERE url = ? AND channel_id = ? ",
                                  [str(url), str(ctx.channel.id)])
        await self.bot.db.commit()
        await ctx.send(f"Feed `{url}` is no longer tracked in this channel")

    @commands.command(name="rss_list", brief="Show a list of all RSS feeds being tracked", description="")
    @commands.check(permissions.is_admin)
    async def tracklist(self, ctx, everywhere=None):
        async with await self.bot.db.execute("SELECT * FROM rssfeed_tracklist") as cursor:
            tracklist = await cursor.fetchall()
        if not tracklist:
            await ctx.send("RSS tracklist is empty")
            return None

        buffer = ":notepad_spiral: **Track list**\n\n"
        for one_entry in tracklist:
            async with await self.bot.db.execute("SELECT channel_id FROM rssfeed_channels WHERE url = ?",
                                                 [str(one_entry[0])]) as cursor:
                destination_list = await cursor.fetchall()
            destination_list_str = ""
            for destination_id in destination_list:
                destination_list_str += f"<#{destination_id[0]}> "
            if (str(ctx.channel.id) in destination_list_str) or everywhere:
                buffer += f"url: `{one_entry[0]}` | channels: {destination_list_str}\n"
        embed = discord.Embed(color=0xff6781)
        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    async def rss_entry_embed(self, rss_object, color=0xbd3661):
        if rss_object:
            embed = discord.Embed(
                title=rss_object["title"],
                url=rss_object["link"],
                description=(unescape(re.sub("<[^<]+?>", "", rss_object["summary"]))).replace("@", ""),
                color=int(color)
            )
            if "author" in rss_object:
                embed.set_author(
                    name=rss_object["author"]
                )
            embed.set_footer(
                text=rss_object["published"]
            )
            return embed
        else:
            return None

    async def fetch(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    http_contents = (await response.text())
                    if len(http_contents) > 4:
                        return http_contents
                    else:
                        return None
        except Exception as e:
            print(time.strftime("%X %x %Z"))
            print("in rankfeed.fetch")
            print(e)
            return None

    async def rssfeed_background_loop(self):
        print("RSSFeed Loop launched!")
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await asyncio.sleep(10)

                async with await self.bot.db.execute("SELECT url FROM rssfeed_tracklist") as cursor:
                    rssfeed_entries = await cursor.fetchall()
                if not rssfeed_entries:
                    # RSS tracklist is empty
                    await asyncio.sleep(1600)
                    continue

                for rssfeed_entry in rssfeed_entries:
                    url = rssfeed_entry[0]
                    async with await self.bot.db.execute("SELECT channel_id FROM rssfeed_channels WHERE url = ?",
                                                         [str(url)]) as cursor:
                        channel_list = await cursor.fetchall()
                    if not channel_list:
                        await self.bot.db.execute("DELETE FROM rssfeed_tracklist WHERE url = ?", [str(url)])
                        await self.bot.db.commit()
                        print(f"{url} is not tracked in any channel so I am untracking it")
                        continue

                    print(f"checking {url}")

                    online_entries = feedparser.parse(await self.fetch(url))
                    if not online_entries:
                        print(f"RSSFeed connection issues with {url} ???")
                        await asyncio.sleep(10)
                        continue

                    for one_entry in online_entries["entries"]:
                        entry_id = one_entry["link"]
                        async with await self.bot.db.execute("SELECT * FROM rssfeed_history "
                                                             "WHERE url = ? AND entry_id = ?",
                                                             [str(url), str(entry_id)]) as cursor:
                            check_is_already_in_history = await cursor.fetchall()
                        if check_is_already_in_history:
                            continue

                        embed = await self.rss_entry_embed(one_entry)
                        if not embed:
                            print("RSSFeed embed returned nothing. this should not happen")
                            continue

                        for one_channel in channel_list:
                            channel = self.bot.get_channel(int(one_channel[0]))
                            if not channel:
                                await self.bot.db.execute("DELETE FROM rssfeed_channels WHERE channel_id = ?",
                                                          [str(one_channel[0])])
                                await self.bot.db.commit()
                                print(f"channel with id {one_channel[0]} no longer exists "
                                      "so I am removing it from the list")
                                continue

                            await channel.send(embed=embed)

                        await self.bot.db.execute("INSERT INTO rssfeed_history VALUES (?, ?)",
                                                  [str(url), str(entry_id)])
                        await self.bot.db.commit()

                print(time.strftime("%X %x %Z"))
                print("finished rss check")
                await asyncio.sleep(1200)
            except Exception as e:
                print(time.strftime("%X %x %Z"))
                print("in rssfeed_background_loop")
                print(e)
                await asyncio.sleep(1200)


def setup(bot):
    bot.add_cog(RSSFeed(bot))
