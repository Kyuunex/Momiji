import feedparser
import aiohttp
from aiohttp import client_exceptions as aiohttp_exceptions
import time
import asyncio
import discord
from discord.ext import commands
import re
from html import unescape

from momiji.modules import permissions
from momiji.reusables import send_large_message


class RSSFeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.REFRESH_INTERVAL = 3600
        self.INACTIVE_INTERVAL = 3600
        self.ERROR_INTERVAL = 1600
        self.bot.background_tasks.append(
            self.bot.loop.create_task(self.rssfeed_background_loop())
        )

    @commands.command(name="rss_add", brief="Subscribe to an RSS feed in the current channel")
    @commands.check(permissions.channel_manage_guild)
    @commands.check(permissions.is_not_ignored)
    async def add(self, ctx, *, url):
        """
        Subscribe to an RSS feed in the current channel.
        """

        url_raw_contents = await self.fetch(url)
        url_parsed_contents = feedparser.parse(url_raw_contents)
        feed_entries = url_parsed_contents["entries"]
        if not feed_entries:
            await ctx.send("i can't find a single entry from this url")
            return

        async with await self.bot.db.execute("SELECT url FROM rssfeed_tracklist WHERE url = ?", [str(url)]) as cursor:
            check_is_already_tracked = await cursor.fetchone()
        if not check_is_already_tracked:
            await self.bot.db.execute("INSERT INTO rssfeed_tracklist VALUES (?)", [str(url)])
            print(f"{url} not tracked anywhere, adding it to the main track list")

        for entry_metadata in feed_entries:
            entry_id = entry_metadata["link"]
            async with await self.bot.db.execute("SELECT entry_id FROM rssfeed_history WHERE url = ? AND entry_id = ?",
                                                 [str(url), str(entry_id)]) as cursor:
                check_is_entry_in_history = await cursor.fetchone()
            if not check_is_entry_in_history:
                await self.bot.db.execute("INSERT INTO rssfeed_history VALUES (?, ?)", [str(url), str(entry_id)])

        await self.bot.db.commit()

        print(f"{url} rss history check completed")

        async with await self.bot.db.execute("SELECT channel_id FROM rssfeed_channels WHERE channel_id = ? AND url = ?",
                                             [int(ctx.channel.id), str(url)]) as cursor:
            check_is_channel_already_tracked = await cursor.fetchone()
        if check_is_channel_already_tracked:
            await ctx.send(f"Feed `{url}` is already tracked in this channel")
            return

        await self.bot.db.execute("INSERT INTO rssfeed_channels VALUES (?, ?)", [str(url), int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.send(f"Feed `{url}` is now tracked in this channel")

    @commands.command(name="rss_remove", brief="Unsubscribe to an RSS feed in the current channel")
    @commands.check(permissions.channel_manage_guild)
    @commands.check(permissions.is_not_ignored)
    async def remove(self, ctx, *, url):
        """
        Unsubscribe to an RSS feed in the current channel
        """

        await self.bot.db.execute("DELETE FROM rssfeed_channels WHERE url = ? AND channel_id = ? ",
                                  [str(url), int(ctx.channel.id)])

        async with await self.bot.db.execute("SELECT channel_id FROM rssfeed_channels WHERE url = ?",
                                             [str(url)]) as cursor:
            channel_list = await cursor.fetchall()
        if not channel_list:
            await self.bot.db.execute("DELETE FROM rssfeed_tracklist WHERE url = ?", [str(url)])
            await self.bot.db.execute("DELETE FROM rssfeed_history WHERE url = ?", [str(url)])
            await ctx.send(f"Feed `{url}` seems not to be tracked anywhere so I'll completely delete it")

        await self.bot.db.commit()

        await ctx.send(f"Feed `{url}` is no longer tracked in this channel")

    @commands.command(name="rss_list", brief="Show a list of all RSS feeds being tracked")
    @commands.check(permissions.channel_manage_guild)
    @commands.check(permissions.is_not_ignored)
    async def tracklist(self, ctx, everywhere=None):
        """
        Show a list of all RSS feeds being tracked
        """

        if not await permissions.is_admin(ctx):
            everywhere = None

        async with await self.bot.db.execute("SELECT url FROM rssfeed_tracklist") as cursor:
            tracklist = await cursor.fetchall()
        if not tracklist:
            await ctx.send("RSS tracklist is empty")
            return

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
        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @staticmethod
    async def rss_entry_embed(rss_object, color=0xbd3661):
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

    @staticmethod
    async def fetch(url):
        headers = {"Connection": "Upgrade", "Upgrade": "http/1.1"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                http_contents = await response.text()
                if len(http_contents) > 4:
                    return http_contents
                else:
                    return None

    async def rssfeed_background_loop(self):
        await self.bot.wait_until_ready()
        print("RSSFeed loop started.")
        while True:
            await asyncio.sleep(10)

            if self.bot.is_closed():
                print("Bot is closed, RSSFeed loop skipped. Sleeping for 120 seconds.")
                await asyncio.sleep(120)
                continue

            async with await self.bot.db.execute("SELECT url FROM rssfeed_tracklist") as cursor:
                rssfeed_entries = await cursor.fetchall()
            if not rssfeed_entries:
                # RSS tracklist is empty
                await asyncio.sleep(self.INACTIVE_INTERVAL)
                continue

            for rssfeed_entry in rssfeed_entries:
                url = str(rssfeed_entry[0]).strip()
                async with await self.bot.db.execute("SELECT channel_id FROM rssfeed_channels WHERE url = ?",
                                                     [str(url)]) as cursor:
                    channel_list = await cursor.fetchall()
                if not channel_list:
                    # TODO: This is uncommented until it can be investigated
                    # await self.bot.db.execute("DELETE FROM rssfeed_tracklist WHERE url = ?", [str(url)])
                    # await self.bot.db.commit()
                    # print(f"{url} is not tracked in any channel so I am untracking it")
                    print(f"{url} is not tracked in any channel, so I will not be checking it.")
                    print(channel_list)
                    continue

                try:
                    url_raw_contents = await self.fetch(url)
                except aiohttp_exceptions.ClientConnectorError:
                    print("ClientConnectorError in rss feed loop. sleeping for 1600s")
                    await asyncio.sleep(self.ERROR_INTERVAL)
                    continue

                url_parsed_contents = feedparser.parse(url_raw_contents)

                if not url_parsed_contents:
                    print(f"RSSFeed connection issues with {url} ???")
                    await asyncio.sleep(10)
                    continue

                online_entries = url_parsed_contents["entries"]

                async with await self.bot.db.execute("SELECT entry_id FROM rssfeed_history WHERE url = ? ",
                                                     [str(url)]) as cursor:
                    rssfeed_history_for_this_url = await cursor.fetchone()
                if not rssfeed_history_for_this_url:
                    for entry_metadata in online_entries:
                        entry_id = entry_metadata["link"]
                        async with await self.bot.db.execute(
                                "SELECT entry_id FROM rssfeed_history WHERE url = ? AND entry_id = ?",
                                [str(url), str(entry_id)]) as cursor:
                            check_is_entry_in_history = await cursor.fetchone()
                        if not check_is_entry_in_history:
                            await self.bot.db.execute("INSERT INTO rssfeed_history VALUES (?, ?)",
                                                      [str(url), str(entry_id)])

                    await self.bot.db.commit()
                    continue

                for one_entry in online_entries:
                    entry_id = one_entry["link"]
                    async with await self.bot.db.execute("SELECT entry_id FROM rssfeed_history "
                                                         "WHERE url = ? AND entry_id = ?",
                                                         [str(url), str(entry_id)]) as cursor:
                        check_is_already_in_history = await cursor.fetchone()
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
                                                      [int(one_channel[0])])
                            await self.bot.db.commit()
                            print(f"channel with id {one_channel[0]} no longer exists "
                                  "so I am removing it from the list")
                            continue

                        await channel.send(embed=embed)

                    await self.bot.db.execute("INSERT INTO rssfeed_history VALUES (?, ?)",
                                              [str(url), str(entry_id)])
                    await self.bot.db.commit()

            print(time.strftime("%Y/%m/%d %H:%M:%S %Z"))
            print("finished rss check")
            await asyncio.sleep(self.REFRESH_INTERVAL)


async def setup(bot):
    await bot.add_cog(RSSFeed(bot))
