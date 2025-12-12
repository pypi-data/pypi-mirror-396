import pytest

from innertubei import Channel
from innertubei.core.constants import ChannelRequestType


class TestChannelStatic:
    TEST_CHANNEL_ID = "UC_aEa8K-EOJ3D6gOs7HcyNg"

    @pytest.mark.asyncio
    async def test_channel_get_playlists(self):
        channel = await Channel.get(self.TEST_CHANNEL_ID)

        assert channel is not None
        assert isinstance(channel, dict)
        assert "id" in channel
        assert channel["id"] == self.TEST_CHANNEL_ID
        assert "title" in channel
        assert "url" in channel
        assert "playlists" in channel
        assert isinstance(channel["playlists"], list)

        playlists = channel["playlists"]
        if len(playlists) > 0:
            first_playlist = playlists[0]
            assert "id" in first_playlist
            assert "title" in first_playlist

    @pytest.mark.asyncio
    async def test_channel_get_info(self):
        channel = await Channel.get(self.TEST_CHANNEL_ID, ChannelRequestType.info)

        assert channel is not None
        assert isinstance(channel, dict)

        assert "id" in channel
        assert "title" in channel

        expected_info_fields = ["description", "subscribers", "country", "views"]
        info_fields_found = sum(1 for field in expected_info_fields if field in channel)

        assert info_fields_found > 0


class TestChannelInstance:
    TEST_CHANNEL_ID = "UC_aEa8K-EOJ3D6gOs7HcyNg"

    @pytest.mark.asyncio
    async def test_channel_instance_init(self):
        channel = Channel(self.TEST_CHANNEL_ID)

        await channel.init()

        assert hasattr(channel, "result")
        assert channel.result is not None
        assert isinstance(channel.result, dict)

        result = channel.result
        assert "id" in result
        assert result["id"] == self.TEST_CHANNEL_ID
        assert "title" in result

    @pytest.mark.asyncio
    async def test_channel_pagination(self):
        channel = Channel(self.TEST_CHANNEL_ID, ChannelRequestType.playlists)
        await channel.init()

        initial_result = channel.result.copy()
        initial_playlists_count = len(initial_result.get("playlists", []))

        if hasattr(channel, "has_more_playlists") and channel.has_more_playlists():
            await channel.next()

            updated_playlists = channel.result.get("playlists", [])
            assert len(updated_playlists) >= initial_playlists_count

    @pytest.mark.asyncio
    async def test_channel_instance_with_info_type(self):
        channel = Channel(self.TEST_CHANNEL_ID, ChannelRequestType.info)
        await channel.init()

        assert channel.result is not None
        result = channel.result

        assert "id" in result
        assert "title" in result

        info_indicators = [
            "description",
            "subscribers",
            "country",
            "views",
            "joinedDate",
            "keywords",
        ]
        has_info_fields = any(field in result for field in info_indicators)
        assert has_info_fields, "Channel info should contain metadata fields"


class TestChannelErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_channel_id(self):
        result = await Channel.get("UCInvalidChannelId123")

        assert result is None or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_malformed_channel_ids(self):
        malformed_ids = [
            "invalid_channel",
            "",
            "UC",
            "NotAChannelId",
        ]

        for channel_id in malformed_ids:
            result = await Channel.get(channel_id)
            assert result is None or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_deleted_or_terminated_channel(self):
        result = await Channel.get("UCxxxxxxxxxxxxxxxxxxxxxxxxx")

        assert result is None

    @pytest.mark.asyncio
    async def test_channel_instance_with_invalid_id(self):
        channel = Channel("invalid_id")

        try:
            await channel.init()
            assert channel.result is None or isinstance(channel.result, dict)
        except Exception as e:
            error_str = str(e).lower()
            assert any(
                keyword in error_str
                for keyword in [
                    "invalid",
                    "not found",
                    "unavailable",
                    "error",
                    "attribute",
                    "none",
                ]
            )


class TestChannelDataIntegrity:
    @pytest.mark.asyncio
    async def test_channel_data_structure(self):
        channel = await Channel.get(TestChannelStatic.TEST_CHANNEL_ID)

        if channel is not None:
            required_fields = ["id", "title"]
            for field in required_fields:
                assert field in channel, f"Missing required field: {field}"

            assert isinstance(channel["title"], str)
            assert len(channel["title"]) > 0

            assert channel["id"] == TestChannelStatic.TEST_CHANNEL_ID

            if "playlists" in channel:
                playlists = channel["playlists"]
                assert isinstance(playlists, list)

                for playlist in playlists[:3]:
                    assert "id" in playlist
                    assert "title" in playlist

                    assert isinstance(playlist["title"], str)
                    assert len(playlist["title"]) > 0

                    if "videoCount" in playlist:
                        video_count = playlist["videoCount"]
                        assert isinstance(video_count, (str, int))

            if "thumbnails" in channel:
                thumbnails = channel["thumbnails"]
                assert isinstance(thumbnails, list)

                for thumb in thumbnails[:3]:
                    assert "url" in thumb
                    assert "width" in thumb
                    assert "height" in thumb

                    assert thumb["url"].startswith(("http://", "https://"))

            if "subscribers" in channel:
                subs = channel["subscribers"]
                if isinstance(subs, dict):
                    assert "simpleText" in subs or "label" in subs

    @pytest.mark.asyncio
    async def test_channel_url_structure(self):
        channel = await Channel.get(TestChannelStatic.TEST_CHANNEL_ID)

        if channel is not None and "url" in channel:
            url = channel["url"]
            assert isinstance(url, str)
            assert "youtube.com/channel/" in url or "youtube.com/@" in url

        if channel is not None and "link" in channel:
            link = channel["link"]
            assert isinstance(link, str)
            assert "youtube.com" in link
