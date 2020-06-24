import aiohttp
import time
import asyncio
import discord
from discord.ext import commands
import urllib.parse

from modules import permissions
import dateutil.parser


class Covid19Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = Covid19Api()
        self.summary_cache = None
        self.bot.background_tasks.append(
            self.bot.loop.create_task(self.covid19_summary_cache_loop())
        )

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
            await ctx.send("I don't have data yet")
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
        try:
            if len(country_code) == 2:
                for country in self.summary_cache.Countries:
                    if country.CountryCode.lower() == country_code.lower():
                        return Covid19Embeds.CountryInfo(country)
            else:
                for country in self.summary_cache.Countries:
                    if country.Country.lower().startswith(country_code.lower()):
                        return Covid19Embeds.CountryInfo(country)
        except:
            return None

        return None

    async def covid19_summary_cache_loop(self):
        print("COVID-19 data caching loop launched!")
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await asyncio.sleep(10)
                summary = await self.api.summary()
                if summary:
                    self.summary_cache = summary
                print(time.strftime("%X %x %Z"))
                print("finished caching covid-19 summary")
                await asyncio.sleep(12000)
            except Exception as e:
                print(time.strftime("%X %x %Z"))
                print("in covid19_summary_cache_loop")
                print(e)
                await asyncio.sleep(12000)


class Covid19Embeds:
    @staticmethod
    def CountryInfo(country):
        if country:
            description = f":thermometer_face: **Confirmed:** {country.TotalConfirmed} ({country.NewConfirmed} recent)\n"
            description += f":coffin: **Dead:** {country.TotalDeaths} ({country.NewDeaths} recent)\n"
            description += f":ok_hand: **Recovered:** {country.TotalRecovered} ({country.NewRecovered} recent)\n"

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


class Summary:
    def __init__(self, response):
        self.Date = dateutil.parser.parse(response["Date"])
        self.Global = Global(response["Global"])
        self.Countries = []
        for country in response["Countries"]:
            self.Countries.append(SummaryCountry(country))


class Global:
    def __init__(self, response):
        self.NewConfirmed = response["NewConfirmed"]
        self.TotalConfirmed = response["TotalConfirmed"]
        self.NewDeaths = response["NewDeaths"]
        self.TotalDeaths = response["TotalDeaths"]
        self.NewRecovered = response["NewRecovered"]
        self.TotalRecovered = response["TotalRecovered"]


class SummaryCountry:
    def __init__(self, response):
        self.Country = response["Country"]
        self.CountryCode = response["CountryCode"]
        self.Slug = response["Slug"]
        self.NewConfirmed = response["NewConfirmed"]
        self.TotalConfirmed = response["TotalConfirmed"]
        self.NewDeaths = response["NewDeaths"]
        self.TotalDeaths = response["TotalDeaths"]
        self.NewRecovered = response["NewRecovered"]
        self.TotalRecovered = response["TotalRecovered"]
        self.Date = dateutil.parser.parse(response["Date"])


class Covid19Api:
    def __init__(self):
        self._base_url = "https://api.covid19api.com/"

    async def _raw_request(self, endpoint, parameters=[]):
        url = self._base_url + endpoint
        if parameters:
            url = url + "?" + urllib.parse.urlencode(parameters)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_json = await response.json()
                return response_json

    async def summary(self):
        result = await self._raw_request("summary")
        if result:
            return Summary(result)
        else:
            return None


def setup(bot):
    bot.add_cog(Covid19Statistics(bot))
