import pytest

from innertubei import Video
from innertubei.core.constants import ResultMode


class TestVideo:
    TEST_VIDEO_ID = "E07s5ZYygMg"
    TEST_VIDEO_URL = "https://www.youtube.com/watch?v=E07s5ZYygMg"

    @pytest.mark.asyncio
    async def test_video_get_full(self):
        video = await Video.get(self.TEST_VIDEO_URL)

        if video is None:
            pytest.skip("Video API returned None - possibly rate limited")

        assert isinstance(video, dict)
        assert "id" in video
        assert video["id"] == self.TEST_VIDEO_ID
        assert "title" in video
        assert "duration" in video
        assert "viewCount" in video

    @pytest.mark.asyncio
    async def test_video_get_with_url(self):
        video = await Video.get(self.TEST_VIDEO_URL)

        if video is None:
            pytest.skip("Video API returned None - possibly rate limited")

        assert video["id"] == self.TEST_VIDEO_ID

    @pytest.mark.asyncio
    async def test_video_get_with_upload_date(self):
        video = await Video.get(self.TEST_VIDEO_URL, get_upload_date=True)

        if video is None:
            pytest.skip("Video API returned None - possibly rate limited")

        assert "uploadDate" in video or "publishDate" in video

    @pytest.mark.asyncio
    async def test_video_get_info_only(self):
        video = await Video.getInfo(self.TEST_VIDEO_URL)

        assert video is not None
        assert isinstance(video, dict)
        assert "id" in video
        assert "title" in video

        assert "streamingData" not in video or video["streamingData"] is None

    @pytest.mark.asyncio
    async def test_video_get_formats_only(self):
        formats = await Video.getFormats(self.TEST_VIDEO_URL)

        assert formats is not None
        assert isinstance(formats, dict)

        if "streamingData" in formats and formats["streamingData"]:
            streaming_data = formats["streamingData"]
            assert "formats" in streaming_data or "adaptiveFormats" in streaming_data

    @pytest.mark.asyncio
    async def test_video_result_modes(self):
        dict_result = await Video.get(self.TEST_VIDEO_URL, result_mode=ResultMode.dict)
        json_result = await Video.get(self.TEST_VIDEO_URL, result_mode=ResultMode.json)

        if dict_result is None or json_result is None:
            pytest.skip("Video API returned None - possibly rate limited")

        assert isinstance(dict_result, dict)
        assert isinstance(json_result, str)

        import json

        parsed_json = json.loads(json_result)
        assert isinstance(parsed_json, dict)
        assert dict_result["id"] == parsed_json["id"]


class TestVideoErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_video_id(self):
        result = await Video.get("invalid_video_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_deleted_or_private_video(self):
        result = await Video.get("dQw4w9WgXcQ_fake")
        assert result is None

    @pytest.mark.asyncio
    async def test_malformed_urls(self):
        malformed_urls = [
            "not_a_url",
            "https://example.com",
            "youtube.com/watch",
            "",
        ]

        for url in malformed_urls:
            result = await Video.get(url)
            assert result is None

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        result = await Video.get(TestVideo.TEST_VIDEO_URL, timeout=1)

        assert result is None or isinstance(result, dict)


class TestVideoDataIntegrity:
    @pytest.mark.asyncio
    async def test_video_data_structure(self):
        video = await Video.get(TestVideo.TEST_VIDEO_URL)

        if video is not None:
            assert "id" in video
            assert "title" in video
            assert isinstance(video["title"], str)
            assert len(video["title"]) > 0

            if "duration" in video:
                duration = video["duration"]
                if isinstance(duration, dict) and "secondsText" in duration:
                    assert isinstance(duration["secondsText"], (str, int, type(None)))

            if "viewCount" in video:
                view_count = video["viewCount"]
                if isinstance(view_count, dict) and "text" in view_count:
                    assert isinstance(view_count["text"], (str, type(None)))

            if "thumbnails" in video and video["thumbnails"]:
                thumbnails = video["thumbnails"]
                assert isinstance(thumbnails, list)

                for thumb in thumbnails[:3]:
                    assert "url" in thumb
                    assert "width" in thumb
                    assert "height" in thumb

                    assert thumb["url"].startswith(("http://", "https://"))
                    assert isinstance(thumb["width"], int)
                    assert isinstance(thumb["height"], int)

            if "channel" in video and video["channel"]:
                channel = video["channel"]
                assert isinstance(channel, dict)

                if "name" in channel:
                    assert isinstance(channel["name"], (str, type(None)))
                if "id" in channel:
                    assert isinstance(channel["id"], (str, type(None)))

            if "link" in video:
                link = video["link"]
                assert isinstance(link, str)
                assert "youtube.com/watch?v=" in link
