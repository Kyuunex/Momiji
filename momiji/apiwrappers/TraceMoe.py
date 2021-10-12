import aiohttp
import urllib.request
import urllib.parse
import urllib


class SearchResult:
    def __init__(self, result):
        self.anilist = result["anilist"]
        self.filename = result["filename"]
        self.episode = result["episode"]  # nullable
        self.from_ = result["from"]
        self.to = result["to"]
        self.similarity = result["similarity"]
        self.video = result["video"]
        self.image = result["image"]

    def __str__(self):
        return self.filename


class SearchResponse:
    def __init__(self, search_response):
        self.frameCount = search_response["frameCount"]
        self.error = search_response["error"]
        self.result = []
        for result_dict in search_response["result"]:
            self.result.append(SearchResult(result_dict))


class TraceMoeApi:
    # TODO: https://soruly.github.io/trace.moe-api/#/docs
    # TODO: don't create a new session on every request, just init one and reuse it

    def __init__(self, token=""):
        self._base_url = "https://api.trace.moe/"
        self.session_headers = {
            "Accept": "application/json"
        }
        if token:
            self.session_headers["x-trace-key"] = token

    async def _raw_request(self, endpoint, parameters):
        url = self._base_url + endpoint + "?" + urllib.parse.urlencode(parameters)
        async with aiohttp.ClientSession(headers=self.session_headers) as session:
            async with session.get(url) as response:
                response_json = await response.json()
                return response_json

    async def search(self, **kwargs):
        result = await self._raw_request("search", kwargs)
        if result:
            return SearchResponse(result)
        else:
            return None
