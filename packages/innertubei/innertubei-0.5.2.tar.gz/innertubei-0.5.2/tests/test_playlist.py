import pytest

from innertubei import Playlist


class TestPlaylistStatic:
    TEST_PLAYLIST_URL = (
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )
    TEST_PLAYLIST_ID = "PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"

    @pytest.mark.asyncio
    async def test_playlist_get_full(self):
        playlist = await Playlist.get(self.TEST_PLAYLIST_URL)

        assert playlist is not None
        assert isinstance(playlist, dict)

        assert "id" in playlist
        assert "title" in playlist
        assert "videos" in playlist

        videos = playlist["videos"]
        assert isinstance(videos, list)

        if len(videos) > 0:
            first_video = videos[0]
            assert "id" in first_video
            assert "title" in first_video

    @pytest.mark.asyncio
    async def test_playlist_get_with_id_only(self):
        playlist = await Playlist.get(self.TEST_PLAYLIST_ID)

        assert playlist is not None
        assert playlist["id"] == self.TEST_PLAYLIST_ID
        assert "title" in playlist
        assert "videos" in playlist

    @pytest.mark.asyncio
    async def test_playlist_get_info_only(self):
        playlist = await Playlist.getInfo(self.TEST_PLAYLIST_URL)

        assert playlist is not None
        assert isinstance(playlist, dict)

        assert "id" in playlist
        assert "title" in playlist

        if "channel" in playlist:
            channel = playlist["channel"]
            assert isinstance(channel, dict)
            assert "name" in channel or "id" in channel

    @pytest.mark.asyncio
    async def test_playlist_get_videos_only(self):
        videos = await Playlist.getVideos(self.TEST_PLAYLIST_URL)

        assert videos is not None
        assert isinstance(videos, list)

        if len(videos) > 0:
            first_video = videos[0]
            assert "id" in first_video
            assert "title" in first_video


class TestPlaylistInstance:
    TEST_PLAYLIST_URL = (
        "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    )

    @pytest.mark.asyncio
    async def test_playlist_instance_basic(self):
        playlist = Playlist(self.TEST_PLAYLIST_URL)

        await playlist.getNextVideos()

        info = playlist.info
        assert info is not None
        assert isinstance(info, dict)
        assert "id" in info
        assert "title" in info

        videos = playlist.videos
        assert isinstance(videos, list)

        if len(videos) > 0:
            first_video = videos[0]
            assert "id" in first_video
            assert "title" in first_video

    @pytest.mark.asyncio
    async def test_playlist_pagination(self):
        playlist = Playlist(self.TEST_PLAYLIST_URL)

        await playlist.getNextVideos()
        initial_count = len(playlist.videos)

        if playlist.hasMoreVideos:
            await playlist.getNextVideos()
            new_count = len(playlist.videos)
            assert new_count >= initial_count

    @pytest.mark.asyncio
    async def test_playlist_instance_isolated(self):
        playlist1 = Playlist(self.TEST_PLAYLIST_URL)
        playlist2 = Playlist(self.TEST_PLAYLIST_URL)

        await playlist1.getNextVideos()

        assert playlist2.info is None
        assert len(playlist2.videos) == 0

        await playlist2.getNextVideos()

        assert playlist1.info is not None
        assert playlist2.info is not None
        assert playlist1.info["id"] == playlist2.info["id"]


class TestPlaylistErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_playlist_url(self):
        result = await Playlist.get(
            "https://www.youtube.com/playlist?list=InvalidPlaylistId"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_malformed_playlist_urls(self):
        malformed_urls = [
            "not_a_url",
            "https://example.com",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "",
        ]

        for url in malformed_urls:
            result = await Playlist.get(url)
            assert result is None

    @pytest.mark.asyncio
    async def test_private_or_deleted_playlist(self):
        result = await Playlist.get(
            "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxx"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_playlist_instance_with_invalid_url(self):
        playlist = Playlist("invalid_url")

        try:
            await playlist.getNextVideos()
            assert playlist.info is None or len(playlist.videos) == 0
        except Exception as e:
            error_str = str(e).lower()
            assert any(
                keyword in error_str
                for keyword in [
                    "invalid",
                    "error",
                    "parse",
                    "attribute",
                    "group",
                    "none",
                    "unavailable",
                ]
            ), "Unexpected error type"


class TestPlaylistDataIntegrity:
    @pytest.mark.asyncio
    async def test_playlist_data_structure(self):
        playlist = await Playlist.get(TestPlaylistStatic.TEST_PLAYLIST_URL)

        if playlist is not None:
            required_fields = ["id", "title"]
            for field in required_fields:
                assert field in playlist, f"Missing required field: {field}"

            assert isinstance(playlist["title"], str)
            assert len(playlist["title"]) > 0

            assert playlist["id"] == TestPlaylistStatic.TEST_PLAYLIST_ID

            if "videos" in playlist:
                videos = playlist["videos"]
                assert isinstance(videos, list)

                for video in videos[:3]:
                    assert "id" in video
                    assert "title" in video

                    assert isinstance(video["title"], str)
                    assert len(video["title"]) > 0

                    if "duration" in video:
                        duration = video["duration"]
                        assert isinstance(duration, str)

                    if "thumbnails" in video:
                        thumbnails = video["thumbnails"]
                        assert isinstance(thumbnails, list)

                        for thumb in thumbnails[:2]:
                            assert "url" in thumb
                            assert "width" in thumb
                            assert "height" in thumb

                            assert thumb["url"].startswith(("http://", "https://"))

            if "channel" in playlist:
                channel = playlist["channel"]
                assert isinstance(channel, dict)

                if "name" in channel:
                    assert isinstance(channel["name"], str)
                if "id" in channel:
                    assert isinstance(channel["id"], str)
