import copy

import httpx
import orjson

from innertubei.core.constants import (
    contentPath,
    continuationContentPath,
    continuationItemKey,
    continuationKeyPath,
    fallbackContentPath,
    itemSectionKey,
    requestPayload,
    searchKey,
    userAgent,
)
from innertubei.handlers.componenthandler import ComponentHandler


class RequestHandler(ComponentHandler):
    def _makeRequest(self) -> None:
        requestBody = copy.deepcopy(requestPayload)
        requestBody["query"] = self.query
        requestBody["client"] = {
            "hl": self.language,
            "gl": self.region,
        }
        if self.searchPreferences:
            requestBody["params"] = self.searchPreferences
        if self.continuationKey:
            requestBody["continuation"] = self.continuationKey
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
            self.response = response.text
        except Exception:
            raise Exception("ERROR: Could not make request.")

    def _parseSource(self) -> None:
        try:
            if not self.continuationKey:
                responseContent = self._getValue(
                    orjson.loads(self.response), contentPath
                )
            else:
                responseContent = self._getValue(
                    orjson.loads(self.response), continuationContentPath
                )
            if responseContent:
                for element in responseContent:
                    if itemSectionKey in element.keys():
                        self.responseSource = self._getValue(
                            element, [itemSectionKey, "contents"]
                        )
                    if continuationItemKey in element.keys():
                        self.continuationKey = self._getValue(
                            element, continuationKeyPath
                        )
            else:
                self.responseSource = self._getValue(
                    orjson.loads(self.response), fallbackContentPath
                )
                self.continuationKey = self._getValue(
                    self.responseSource[-1], continuationKeyPath
                )
        except:
            raise Exception("ERROR: Could not parse YouTube response.")
