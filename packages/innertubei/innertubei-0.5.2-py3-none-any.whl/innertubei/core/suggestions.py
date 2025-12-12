from typing import Union
from urllib.parse import urlencode

import orjson

from innertubei.core.constants import ResultMode
from innertubei.core.requests import RequestCore


class SuggestionsCore(RequestCore):
    """Gets search suggestions for the given query.

    Args:
        language (str, optional): Sets the suggestion language. Defaults to 'en'.
        region (str, optional): Sets the suggestion region. Defaults to 'US'.

    Examples:
        Calling `result` method gives the search result.

        >>> suggestions = Suggestions(language = 'en', region = 'US').get('Harry Styles', mode = ResultMode.json)
        >>> print(suggestions)
        {
            'result': [
                'harry styles',
                'harry styles treat people with kindness',
                'harry styles golden music video',
                'harry styles interview',
                'harry styles adore you',
                'harry styles watermelon sugar',
                'harry styles snl',
                'harry styles falling',
                'harry styles tpwk',
                'harry styles sign of the times',
                'harry styles jingle ball 2020',
                'harry styles christmas',
                'harry styles live',
                'harry styles juice'
            ]
        }
    """

    def __init__(self, language: str = "en", region: str = "US", timeout: int = None):
        super().__init__()
        self.language = language
        self.region = region
        self.timeout = timeout

    def _post_request_processing(self, mode):
        searchSuggestions = []

        self.__parseSource()
        for element in self.responseSource:
            if type(element) is list:
                for searchSuggestionElement in element:
                    searchSuggestions.append(searchSuggestionElement[0])
                break
        if mode == ResultMode.dict:
            return {"result": searchSuggestions}
        elif mode == ResultMode.json:
            return orjson.dumps(
                {"result": searchSuggestions}, option=orjson.OPT_INDENT_2
            ).decode("utf-8")

    async def _getAsync(
        self, query: str, mode: int = ResultMode.dict
    ) -> Union[dict, str]:
        self.url = (
            "https://clients1.google.com/complete/search"
            + "?"
            + urlencode(
                {
                    "hl": self.language,
                    "gl": self.region,
                    "q": query,
                    "client": "youtube",
                    "gs_ri": "youtube",
                    "ds": "yt",
                }
            )
        )

        await self.__makeAsyncRequest()
        if self.response is None:
            return {"result": []}
        return self._post_request_processing(mode)

    def __parseSource(self) -> None:
        try:
            start_index = self.response.index("([") + 1
            end_index = self.response.rindex("])") + 1
            self.responseSource = orjson.loads(self.response[start_index:end_index])
        except (ValueError, orjson.JSONDecodeError) as e:
            import logging

            logging.error(
                "ERROR: Could not parse YouTube response. Raw response: %r",
                self.response,
            )
            raise Exception("ERROR: Could not parse YouTube response.") from e

    async def __makeAsyncRequest(self) -> None:
        request = await self.asyncGetRequest()
        if request:
            self.response = request.text
        else:
            self.response = None
