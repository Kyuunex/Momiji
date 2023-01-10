import aiohttp


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

    def __init__(self, token=""):
        self._base_url = "https://api.trace.moe/"
        self._session_headers = {
            "Accept": "application/json"
        }
        if token:
            self._session_headers["x-trace-key"] = token
        self._session = aiohttp.ClientSession(headers=self._session_headers)

    async def close(self):
        await self._session.close()

    async def search(self, **kwargs):
        async with self._session.get(self._base_url + "search", params=kwargs) as response:
            response_json = await response.json()
            return SearchResponse(response_json)
