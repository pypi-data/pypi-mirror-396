import copy
from typing import Union

import httpx
import orjson

from innertubei.core.constants import (
    ResultMode,
    contentPath,
    continuationKeyPath,
    hashtagBrowseKey,
    hashtagContinuationVideosPath,
    hashtagElementKey,
    hashtagVideosPath,
    requestPayload,
    richItemKey,
    searchKey,
    userAgent,
    videoElementKey,
)
from innertubei.handlers.componenthandler import ComponentHandler


class HashtagCore(ComponentHandler):
    response = None
    resultComponents = []

    def __init__(
        self, hashtag: str, limit: int, language: str, region: str, timeout: int
    ):
        self.hashtag = hashtag
        self.limit = limit
        self.language = language
        self.region = region
        self.timeout = timeout
        self.continuationKey = None
        self.params = None

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        """Returns the hashtag videos.
        Args:
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
        Returns:
            Union[str, dict]: Returns JSON or dictionary.
        """
        if mode == ResultMode.json:
            return orjson.dumps(
                {"result": self.resultComponents}, option=orjson.OPT_INDENT_2
            ).decode("utf-8")
        elif mode == ResultMode.dict:
            return {"result": self.resultComponents}

    def next(self) -> bool:
        """Gets the videos from the next page. Call result
        Returns:
            bool: Returns True if getting more results was successful.
        """
        self.response = None
        self.resultComponents = []
        if self.continuationKey:
            self._makeRequest()
            self._getComponents()
        if self.resultComponents:
            return True
        return False

    def _getParams(self) -> None:
        requestBody = copy.deepcopy(requestPayload)
        requestBody["query"] = "#" + self.hashtag
        requestBody["client"] = {
            "hl": self.language,
            "gl": self.region,
        }
        try:
            response = httpx.post(
                "https://www.youtube.com/youtubei/v1/search",
                params={
                    "key": searchKey,
                },
                headers={
                    "User-Agent": userAgent,
                },
                json=requestBody,
                timeout=self.timeout,
            )
            response.raise_for_status()
            response_json = orjson.loads(response.content)
        except Exception:
            raise Exception("ERROR: Could not make request.")
        content = self._getValue(response_json, contentPath)
        for item in self._getValue(content, [0, "itemSectionRenderer", "contents"]):
            if hashtagElementKey in item.keys():
                self.params = self._getValue(
                    item[hashtagElementKey],
                    ["onTapCommand", "browseEndpoint", "params"],
                )
                return

    async def _asyncGetParams(self) -> None:
        requestBody = copy.deepcopy(requestPayload)
        requestBody["query"] = "#" + self.hashtag
        requestBody["client"] = {
            "hl": self.language,
            "gl": self.region,
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.youtube.com/youtubei/v1/search",
                    params={
                        "key": searchKey,
                    },
                    headers={
                        "User-Agent": userAgent,
                    },
                    json=requestBody,
                    timeout=self.timeout,
                )
                response = orjson.loads(response.content)
        except:
            raise Exception("ERROR: Could not make request.")
        content = self._getValue(response, contentPath)
        for item in self._getValue(content, [0, "itemSectionRenderer", "contents"]):
            if hashtagElementKey in item.keys():
                self.params = self._getValue(
                    item[hashtagElementKey],
                    ["onTapCommand", "browseEndpoint", "params"],
                )
                return

    def _makeRequest(self) -> None:
        if self.params is None:
            return
        requestBody = copy.deepcopy(requestPayload)
        requestBody["browseId"] = hashtagBrowseKey
        requestBody["params"] = self.params
        requestBody["client"] = {
            "hl": self.language,
            "gl": self.region,
        }
        if self.continuationKey:
            requestBody["continuation"] = self.continuationKey
        try:
            response = httpx.post(
                "https://www.youtube.com/youtubei/v1/browse",
                params={
                    "key": searchKey,
                },
                headers={
                    "User-Agent": userAgent,
                },
                json=requestBody,
                timeout=self.timeout,
            )
            response.raise_for_status()
            self.response = response.text
        except Exception:
            raise Exception("ERROR: Could not make request.")

    async def _asyncMakeRequest(self) -> None:
        if self.params == None:
            return
        requestBody = copy.deepcopy(requestPayload)
        requestBody["browseId"] = hashtagBrowseKey
        requestBody["params"] = self.params
        requestBody["client"] = {
            "hl": self.language,
            "gl": self.region,
        }
        if self.continuationKey:
            requestBody["continuation"] = self.continuationKey
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.youtube.com/youtubei/v1/browse",
                    params={
                        "key": searchKey,
                    },
                    headers={
                        "User-Agent": userAgent,
                    },
                    json=requestBody,
                    timeout=self.timeout,
                )
                self.response = response.content
        except:
            raise Exception("ERROR: Could not make request.")

    def _getComponents(self) -> None:
        if self.response == None:
            return
        self.resultComponents = []
        try:
            if not self.continuationKey:
                responseSource = self._getValue(
                    orjson.loads(self.response), hashtagVideosPath
                )
            else:
                responseSource = self._getValue(
                    orjson.loads(self.response), hashtagContinuationVideosPath
                )
            if responseSource:
                for element in responseSource:
                    if richItemKey in element.keys():
                        richItemElement = self._getValue(
                            element, [richItemKey, "content"]
                        )
                        if videoElementKey in richItemElement.keys():
                            videoComponent = self._getVideoComponent(richItemElement)
                            self.resultComponents.append(videoComponent)
                    if len(self.resultComponents) >= self.limit:
                        break
                self.continuationKey = self._getValue(
                    responseSource[-1], continuationKeyPath
                )
        except:
            raise Exception("ERROR: Could not parse YouTube response.")
