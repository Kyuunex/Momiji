"""
An asynchronous COVID-19 statistics API wrapper
"""

import aiohttp
import dateutil.parser


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

    def __str__(self):
        return self.Country


class Summary:
    def __init__(self, response):
        self.Date = dateutil.parser.parse(response["Date"])
        self.Global = Global(response["Global"])
        self.Countries = []
        for country in response["Countries"]:
            self.Countries.append(SummaryCountry(country))


class COVID19APIClient:
    def __init__(self):
        self._base_url = "https://api.covid19api.com/"
        self._session = aiohttp.ClientSession()

    async def close(self):
        await self._session.close()

    async def summary(self):
        async with self._session.get(self._base_url + "summary") as response:
            response_contents = await response.json()
            return Summary(response_contents)
