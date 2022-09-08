import time
import asyncio
import discord
from discord.ext import commands

from momiji.modules import permissions
from momiji.reusables import send_large_message
from momiji.modules import cooldown
import operator
from aiocovidapi import COVID19APIClient


class COVID19(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = COVID19APIClient()
        self.summary_cache = None
        self.bot.background_tasks.append(
            self.bot.loop.create_task(self.covid19_summary_cache_loop())
        )

    @commands.command(name="c19summary", brief="Get COVID-19 summary", aliases=['c19s'])
    @commands.check(permissions.is_not_ignored)
    async def c19summary(self, ctx, *args):
        """
        Shows a summary of COVID-19 worldwide.
        Example args: sort, limit:50
        """

        # TODO: Add sort by something with optional args

        if not await cooldown.check(str(ctx.author.id), "last_covid_time", 400):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return

        if not self.summary_cache:
            await ctx.send("I have not pulled the data from the internet yet. Try again in 10 seconds.")
            return

        summary = self.summary_cache
        buffer = f"**Global info:**\n"

        buffer += f":thermometer_face: **Confirmed:** {summary.Global.TotalConfirmed} "
        buffer += f"({summary.Global.NewConfirmed} recent)\n"

        buffer += f":coffin: **Dead:** {summary.Global.TotalDeaths} "
        buffer += f"({summary.Global.NewDeaths} recent)\n"

        buffer += f":ok_hand: **Recovered:** {summary.Global.TotalRecovered} "
        buffer += f"({summary.Global.NewRecovered} recent)\n"

        buffer += f"\n"
        buffer += f"**Countries:**\n"

        if "sort:alphabetical" in args:
            correct_sort = summary.Countries
        else:
            correct_sort = sorted(summary.Countries, key=operator.attrgetter('TotalConfirmed'), reverse=True)

        max_results = 0
        for arg in args:
            if "limit" in arg:
                if ":" in arg:
                    sub_args = arg.split(":")
                    max_results = int(sub_args[1])

        count = 1
        for country in correct_sort:
            if max_results:
                if count >= max_results:
                    break
            else:
                if count >= 20:
                    break
            buffer += f":flag_{country.CountryCode.lower()}: **{country.Country}:** "
            buffer += f":thermometer_face: {country.TotalConfirmed} ({country.NewConfirmed}) / "
            buffer += f":coffin: {country.TotalDeaths} ({country.NewDeaths}) / "
            buffer += f":ok_hand: {country.TotalRecovered} ({country.NewRecovered})"
            buffer += f"\n"
            count += 1

        embed = discord.Embed(
            color=0xAD6F49,
        )
        embed.set_author(name="COVID-19 Summary")
        embed.set_footer(text=f"Last update: {str(self.summary_cache.Date.isoformat(' '))}")
        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="c19country", brief="Get COVID-19 info for a country", aliases=['c19c', 'c19'])
    @commands.check(permissions.is_not_ignored)
    async def c19country(self, ctx, *, country_code):
        """
        Get some info about the Covid-19 situation in a specific country
        Takes Alpha-2 codes and country names.
        If you are not sure what this means, have a look at this
        https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        """

        if not self.summary_cache:
            await ctx.send("I have not pulled the data from the internet yet. Try again in 10 seconds.")
            return

        embed = await self.get_country_embed(country_code)
        if not embed:
            await ctx.send(f"{ctx.author.mention}, Country not found. \n"
                           "You can also try searching with Alpha-2 codes. \n"
                           "If you are not sure what this means, have a look at this "
                           "<https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>")
            return

        if embed:
            await ctx.send(embed=embed)

    async def get_country_embed(self, country_code):
        if len(country_code) == 2:
            for country in self.summary_cache.Countries:
                if country.CountryCode.lower() == country_code.lower():
                    return COVID19Embeds.CountryInfo(country)
        else:
            for country in self.summary_cache.Countries:
                if country.Country.lower().startswith(country_code.lower()):
                    return COVID19Embeds.CountryInfo(country)

        return None

    async def covid19_summary_cache_loop(self):
        print("COVID-19 data caching loop launched!")
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(10)

            summary = await self.api.summary()
            if summary:
                self.summary_cache = summary
                
            print(time.strftime("%X %x %Z"))
            print("finished caching covid-19 summary")
            await asyncio.sleep(12000)


class COVID19Embeds:
    @staticmethod
    def CountryInfo(country):
        if country:
            death_percentage = round(float(country.TotalDeaths * 100 / country.TotalConfirmed), 3)
            recovery_percentage = round(float(country.TotalRecovered * 100 / country.TotalConfirmed), 3)

            description = f":thermometer_face: **Confirmed:** " \
                          f"{country.TotalConfirmed} ({country.NewConfirmed} recent)\n"
            description += f":coffin: **Dead:** " \
                           f"{country.TotalDeaths} ({death_percentage}% of total) " \
                           f"({country.NewDeaths} recent)\n"
            description += f":ok_hand: **Recovered:** " \
                           f"{country.TotalRecovered} ({recovery_percentage}% of total) " \
                           f"({country.NewRecovered} recent)\n"

            embed = discord.Embed(
                description=description,
                title=f":flag_{country.CountryCode.lower()}: {country.Country}",
                color=0xAD6F49,
            )
            embed.set_author(name="COVID-19 statistics")
            embed.set_footer(text=f"Last update: {str(country.Date.isoformat(' '))}")
            return embed
        else:
            return None


async def setup(bot):
    await bot.add_cog(COVID19(bot))
