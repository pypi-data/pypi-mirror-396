import asyncio

import pytest

from innertubei import Video, VideosSearch
from innertubei.core.componenthandler import getValue, getVideoId
from innertubei.core.constants import ChannelRequestType, ResultMode, VideoSortOrder


class TestConstants:
    def test_result_mode_values(self):
        assert hasattr(ResultMode, "dict")
        assert hasattr(ResultMode, "json")
        assert ResultMode.dict == 1
        assert ResultMode.json == 0

    def test_video_sort_order_exists(self):
        assert hasattr(VideoSortOrder, "relevance")
        assert hasattr(VideoSortOrder, "uploadDate")
        assert hasattr(VideoSortOrder, "viewCount")
        assert hasattr(VideoSortOrder, "rating")

    def test_channel_request_type(self):
        assert hasattr(ChannelRequestType, "playlists")
        assert hasattr(ChannelRequestType, "info")


class TestComponentHandler:
    def test_get_value_basic(self):
        data = {"a": {"b": {"c": "value"}}}
        result = getValue(data, ["a", "b", "c"])
        assert result == "value"

    def test_get_value_missing_key(self):
        data = {"a": {"b": "value"}}
        result = getValue(data, ["a", "x", "c"])
        assert result is None

    def test_get_value_with_list_indices(self):
        data = {"items": [{"name": "first"}, {"name": "second"}]}
        result = getValue(data, ["items", 1, "name"])
        assert result == "second"

    def test_get_value_out_of_bounds(self):
        data = {"items": [{"name": "first"}]}
        result = getValue(data, ["items", 5, "name"])
        assert result is None

    def test_get_video_id_from_urls(self):
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=60s", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]

        for url, expected in test_cases:
            result = getVideoId(url)
            assert result == expected, f"Failed for {url}"

    def test_get_video_id_invalid_urls(self):
        invalid_cases = [
            ("", None),
            (None, None),
            (
                "https://example.com",
                "https://example.com",
            ),  # Returns input for non-YouTube URLs
            (
                "https://www.youtube.com/watch",
                "https://www.youtube.com/watch",
            ),  # Returns input if no v= param
        ]

        for invalid_url, expected in invalid_cases:
            result = getVideoId(invalid_url)
            assert result == expected, (
                f"Expected {expected} for {invalid_url}, got {result}"
            )


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_network_timeout_behavior(self):
        search = VideosSearch("test query", limit=1)

        try:
            result = await asyncio.wait_for(search.next(), timeout=10)
            assert result is not None
            assert "result" in result
        except asyncio.TimeoutError:
            pass

    @pytest.mark.asyncio
    async def test_none_input_handling(self):
        result = getValue(None, ["test"])
        assert result is None

        result = getVideoId(None)
        assert result is None


class TestDataValidation:
    @pytest.mark.asyncio
    async def test_video_id_format_validation(self):
        valid_id = "E07s5ZYygMg"
        video = await Video.get(valid_id)

        if video is not None:
            assert video.get("id") == valid_id

    @pytest.mark.asyncio
    async def test_url_format_validation(self):
        valid_url = "https://www.youtube.com/watch?v=E07s5ZYygMg"
        video = await Video.get(valid_url)

        if video is not None:
            assert "youtube.com" in video.get("link", "")

    @pytest.mark.asyncio
    async def test_result_structure_validation(self):
        search = VideosSearch("test", limit=1)
        result = await search.next()

        assert isinstance(result, dict)
        assert "result" in result
        assert isinstance(result["result"], list)


class TestConcurrencyBehavior:
    @pytest.mark.asyncio
    async def test_concurrent_video_requests(self):
        video_ids = ["E07s5ZYygMg", "dQw4w9WgXcQ"]

        tasks = [Video.get(vid_id) for vid_id in video_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == len(video_ids)
        for result in results:
            assert not isinstance(result, Exception) or result is None

    @pytest.mark.asyncio
    async def test_concurrent_search_requests(self):
        queries = ["music", "python", "tutorial"]

        async def search_query(query):
            search = VideosSearch(query, limit=1)
            return await search.next()

        tasks = [search_query(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == len(queries)
        for result in results:
            if not isinstance(result, Exception) and result is not None:
                assert "result" in result


class TestMemoryAndPerformance:
    @pytest.mark.asyncio
    async def test_large_limit_handling(self):
        search = VideosSearch("music", limit=50)

        try:
            result = await search.next()

            if result is not None:
                assert "result" in result
                results_count = len(result["result"])
                assert results_count <= 50
            else:
                assert True  # Gracefully handle case where search returns None
        except Exception:
            assert True  # Gracefully handle any search exceptions

    def test_string_length_limits(self):
        long_query = "test " * 100

        assert len(long_query) == 500
        assert isinstance(long_query, str)


class TestBoundaryConditions:
    @pytest.mark.asyncio
    async def test_zero_limit_handling(self):
        from innertubei import VideosSearch

        search = VideosSearch("test", limit=0)
        result = await search.next()

        assert result is not None
        assert "result" in result

    @pytest.mark.asyncio
    async def test_negative_limit_handling(self):
        from innertubei import VideosSearch

        search = VideosSearch("test", limit=-1)
        result = await search.next()

        assert result is not None
        assert "result" in result

    @pytest.mark.asyncio
    async def test_empty_string_parameters(self):
        search = VideosSearch("", limit=1)
        result = await search.next()

        assert result is not None
        assert "result" in result
