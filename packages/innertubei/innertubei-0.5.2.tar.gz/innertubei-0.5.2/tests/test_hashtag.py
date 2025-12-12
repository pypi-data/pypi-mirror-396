import pytest

from innertubei import Hashtag


class TestHashtag:
    @pytest.mark.asyncio
    async def test_hashtag_basic(self):
        hashtag = Hashtag("ncs", limit=10)
        result = await hashtag.next()

        assert result is not None
        assert isinstance(result, dict)
        assert "result" in result

        videos = result["result"]
        assert isinstance(videos, list)

        if len(videos) > 0:
            first_video = videos[0]
            assert "id" in first_video
            assert "title" in first_video

    @pytest.mark.asyncio
    async def test_hashtag_with_different_tags(self):
        tags = ["music", "gaming", "tutorial"]

        for tag in tags:
            hashtag = Hashtag(tag, limit=5)
            result = await hashtag.next()

            assert result is not None
            assert "result" in result

    @pytest.mark.asyncio
    async def test_hashtag_pagination(self):
        hashtag = Hashtag("music", limit=5)

        first_result = await hashtag.next()
        assert first_result is not None
        first_videos = first_result["result"]

        if len(first_videos) > 0:
            second_result = await hashtag.next()

            if second_result and second_result["result"]:
                second_videos = second_result["result"]

                first_ids = {video.get("id") for video in first_videos}
                second_ids = {video.get("id") for video in second_videos}

                overlap = first_ids.intersection(second_ids)
                assert len(overlap) == 0

    @pytest.mark.asyncio
    async def test_hashtag_with_language_region(self):
        hashtag = Hashtag("music", limit=5, language="en", region="US")
        result = await hashtag.next()

        assert result is not None
        assert "result" in result

    @pytest.mark.asyncio
    async def test_hashtag_limit_parameter(self):
        limits = [1, 5, 20]

        for limit in limits:
            hashtag = Hashtag("test", limit=limit)
            result = await hashtag.next()

            if result and result["result"]:
                actual_count = len(result["result"])
                assert actual_count <= limit


class TestHashtagErrorHandling:
    @pytest.mark.asyncio
    async def test_empty_hashtag(self):
        hashtag = Hashtag("", limit=5)
        result = await hashtag.next()

        assert result is not None
        assert "result" in result

    @pytest.mark.asyncio
    async def test_nonexistent_hashtag(self):
        hashtag = Hashtag("veryrarenonexistenthashtagxyz123", limit=5)
        result = await hashtag.next()

        assert result is not None
        assert "result" in result

    @pytest.mark.asyncio
    async def test_special_characters_hashtag(self):
        special_tags = [
            "test@#$",
            "test hashtag",
            "test+tag",
        ]

        for tag in special_tags:
            hashtag = Hashtag(tag, limit=3)
            result = await hashtag.next()

            assert result is not None
            assert "result" in result

    @pytest.mark.asyncio
    async def test_large_limit(self):
        hashtag = Hashtag("music", limit=100)
        result = await hashtag.next()

        assert result is not None
        assert "result" in result

        videos = result["result"]
        assert len(videos) <= 100

    @pytest.mark.asyncio
    async def test_zero_limit(self):
        hashtag = Hashtag("music", limit=0)
        result = await hashtag.next()

        assert result is not None
        assert "result" in result


class TestHashtagDataIntegrity:
    @pytest.mark.asyncio
    async def test_hashtag_video_structure(self):
        hashtag = Hashtag("music", limit=5)
        result = await hashtag.next()

        if result and result["result"]:
            videos = result["result"]

            for video in videos[:3]:
                assert "id" in video
                assert isinstance(video["id"], str)
                assert len(video["id"]) > 0

                assert "title" in video
                assert isinstance(video["title"], str)
                assert len(video["title"]) > 0

                if "thumbnails" in video:
                    thumbnails = video["thumbnails"]
                    assert isinstance(thumbnails, list)

                    for thumb in thumbnails[:2]:
                        assert "url" in thumb
                        assert "width" in thumb
                        assert "height" in thumb

                        assert thumb["url"].startswith(("http://", "https://"))
                        assert isinstance(thumb["width"], int)
                        assert isinstance(thumb["height"], int)

                if "channel" in video:
                    channel = video["channel"]
                    assert isinstance(channel, dict)

                    if "name" in channel:
                        assert isinstance(channel["name"], str)
                    if "id" in channel:
                        assert isinstance(channel["id"], str)

    @pytest.mark.asyncio
    async def test_hashtag_results_uniqueness(self):
        hashtag = Hashtag("popular", limit=20)
        result = await hashtag.next()

        if result and result["result"]:
            videos = result["result"]
            video_ids = [video.get("id") for video in videos if video.get("id")]

            unique_ids = set(video_ids)
            assert len(unique_ids) == len(video_ids)

    @pytest.mark.asyncio
    async def test_hashtag_video_links(self):
        hashtag = Hashtag("music", limit=5)
        result = await hashtag.next()

        if result and result["result"]:
            videos = result["result"]

            for video in videos[:3]:
                if "link" in video:
                    link = video["link"]
                    assert isinstance(link, str)
                    assert "youtube.com/watch?v=" in link

                if "channel" in video and "link" in video["channel"]:
                    channel_link = video["channel"]["link"]
                    assert isinstance(channel_link, str)
                    assert "youtube.com" in channel_link
