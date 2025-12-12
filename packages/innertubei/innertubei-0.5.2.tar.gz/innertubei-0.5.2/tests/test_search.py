import pytest

from innertubei import (
    ChannelSearch,
    ChannelsSearch,
    CustomSearch,
    PlaylistsSearch,
    Search,
    VideosSearch,
)
from innertubei.core.constants import VideoSortOrder


class TestSearch:
    @pytest.mark.asyncio
    async def test_general_search(self):
        search = Search("NoCopyrightSounds", limit=5)
        result = await search.next()

        assert result is not None
        assert "result" in result
        assert len(result["result"]) > 0

        types_found = set()
        for item in result["result"]:
            if "type" in item:
                types_found.add(item["type"])

        assert len(types_found) > 0

    @pytest.mark.asyncio
    async def test_search_pagination(self):
        search = Search("music", limit=3)

        first_result = await search.next()
        assert first_result is not None
        first_items = first_result["result"]

        second_result = await search.next()
        if second_result and second_result["result"]:
            second_items = second_result["result"]

            first_ids = {item.get("id") for item in first_items if item.get("id")}
            second_ids = {item.get("id") for item in second_items if item.get("id")}

            overlap = first_ids.intersection(second_ids)
            assert len(overlap) == 0, "Pagination should not return duplicate items"


class TestVideosSearch:
    @pytest.mark.asyncio
    async def test_videos_search(self):
        search = VideosSearch("NCS House", limit=5)
        result = await search.next()

        assert result is not None
        assert "result" in result
        assert len(result["result"]) > 0

        for item in result["result"]:
            assert item.get("type") == "video" or "duration" in item
            assert "title" in item
            if "link" in item:
                assert "watch?v=" in item["link"]


class TestChannelsSearch:
    @pytest.mark.asyncio
    async def test_channels_search(self):
        search = ChannelsSearch("NoCopyrightSounds", limit=3)
        result = await search.next()

        assert result is not None
        assert "result" in result
        assert len(result["result"]) >= 0

        for item in result["result"]:
            assert item.get("type") == "channel" or "subscribers" in item
            assert "title" in item
            if "link" in item:
                assert "channel/" in item["link"] or "@" in item["link"]


class TestPlaylistsSearch:
    @pytest.mark.asyncio
    async def test_playlists_search(self):
        search = PlaylistsSearch("NCS House", limit=3)
        result = await search.next()

        assert result is not None
        assert "result" in result
        assert len(result["result"]) >= 0

        for item in result["result"]:
            assert item.get("type") == "playlist" or "videoCount" in item
            assert "title" in item
            if "link" in item:
                assert "playlist?list=" in item["link"]


class TestCustomSearch:
    @pytest.mark.asyncio
    async def test_custom_search_with_upload_date_filter(self):
        search = CustomSearch(
            "Python", search_preferences=VideoSortOrder.uploadDate, limit=5
        )
        result = await search.next()

        assert result is not None
        assert "result" in result
        assert len(result["result"]) >= 0


class TestChannelSearch:
    @pytest.mark.asyncio
    async def test_channel_search(self):
        channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"

        search = ChannelSearch("house", channel_id)
        result = await search.next()

        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 0

        for item in result:
            assert "title" in item or "id" in item
            assert item.get("type") in ["video", "playlist"] or "id" in item


class TestSearchErrorHandling:
    @pytest.mark.asyncio
    async def test_empty_query_search(self):
        search = VideosSearch("", limit=1)
        result = await search.next()

        assert result is not None
        assert "result" in result

    @pytest.mark.asyncio
    async def test_very_specific_search(self):
        unlikely_query = "xyzabc123veryrarequery789"
        search = VideosSearch(unlikely_query, limit=1)
        result = await search.next()

        assert result is not None
        assert "result" in result
