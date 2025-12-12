import pytest

from innertubei import Transcript


class TestTranscript:
    TEST_VIDEO_ID = "E07s5ZYygMg"
    TEST_VIDEO_URL = "https://www.youtube.com/watch?v=E07s5ZYygMg"

    @pytest.mark.asyncio
    async def test_transcript_basic(self):
        transcript = await Transcript.get(self.TEST_VIDEO_URL)

        assert transcript is not None
        assert isinstance(transcript, dict)
        assert "segments" in transcript
        assert "languages" in transcript

        segments = transcript["segments"]
        languages = transcript["languages"]

        assert isinstance(segments, list)
        assert isinstance(languages, list)

    @pytest.mark.asyncio
    async def test_transcript_with_video_id(self):
        transcript = await Transcript.get(self.TEST_VIDEO_ID)

        if transcript is None:
            pytest.skip("Transcript API returned None - possibly rate limited")

        assert "segments" in transcript
        assert "languages" in transcript

    @pytest.mark.asyncio
    async def test_transcript_segments_structure(self):
        transcript = await Transcript.get(self.TEST_VIDEO_URL)

        if transcript and transcript["segments"]:
            segments = transcript["segments"]

            for segment in segments[:5]:
                assert "text" in segment
                assert isinstance(segment["text"], str)

                if "startMs" in segment:
                    assert isinstance(segment["startMs"], (int, str))
                if "endMs" in segment:
                    assert isinstance(segment["endMs"], (int, str))

    @pytest.mark.asyncio
    async def test_transcript_languages_structure(self):
        transcript = await Transcript.get(self.TEST_VIDEO_URL)

        if transcript and transcript["languages"]:
            languages = transcript["languages"]

            for lang in languages:
                assert isinstance(lang, dict)

                if "params" in lang:
                    assert isinstance(lang["params"], str)
                if "title" in lang:
                    assert isinstance(lang["title"], str)

    @pytest.mark.asyncio
    async def test_transcript_with_params(self):
        transcript = await Transcript.get(self.TEST_VIDEO_URL)

        if transcript and transcript["languages"] and len(transcript["languages"]) > 1:
            first_lang_params = transcript["languages"][0].get("params")

            if first_lang_params:
                specific_transcript = await Transcript.get(
                    self.TEST_VIDEO_URL, first_lang_params
                )

                assert specific_transcript is not None
                assert "segments" in specific_transcript


class TestTranscriptErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_video_id(self):
        transcript = await Transcript.get("invalid_video_id")

        assert transcript is None or (
            isinstance(transcript, dict) and len(transcript.get("segments", [])) == 0
        )

    @pytest.mark.asyncio
    async def test_video_without_transcript(self):
        fake_video_id = "aaaaaaaaaaa"
        transcript = await Transcript.get(fake_video_id)

        assert transcript is None or (
            isinstance(transcript, dict) and len(transcript.get("segments", [])) == 0
        )

    @pytest.mark.asyncio
    async def test_malformed_video_urls(self):
        malformed_urls = [
            "not_a_url",
            "https://example.com",
            "",
            "youtube.com/watch",
        ]

        for url in malformed_urls:
            transcript = await Transcript.get(url)
            assert transcript is None or isinstance(transcript, dict)

    @pytest.mark.asyncio
    async def test_invalid_params(self):
        transcript = await Transcript.get(
            TestTranscript.TEST_VIDEO_URL, "invalid_params"
        )

        assert transcript is None or isinstance(transcript, dict)


class TestTranscriptDataIntegrity:
    @pytest.mark.asyncio
    async def test_transcript_content_consistency(self):
        transcript = await Transcript.get(TestTranscript.TEST_VIDEO_URL)

        if transcript and transcript["segments"]:
            segments = transcript["segments"]

            prev_end_time = -1
            for segment in segments[:10]:
                if "startMs" in segment and "endMs" in segment:
                    try:
                        start_ms = (
                            int(segment["startMs"])
                            if isinstance(segment["startMs"], str)
                            else segment["startMs"]
                        )
                        end_ms = (
                            int(segment["endMs"])
                            if isinstance(segment["endMs"], str)
                            else segment["endMs"]
                        )

                        assert start_ms <= end_ms, (
                            "Start time should be before end time"
                        )

                        if prev_end_time > 0:
                            assert start_ms >= prev_end_time - 1000, (
                                "Segments should be roughly chronological"
                            )

                        prev_end_time = end_ms
                    except (ValueError, TypeError):
                        pass

    @pytest.mark.asyncio
    async def test_transcript_text_quality(self):
        transcript = await Transcript.get(TestTranscript.TEST_VIDEO_URL)

        if transcript and transcript["segments"]:
            segments = transcript["segments"]

            text_segments = [seg["text"] for seg in segments if seg.get("text")]

            if text_segments:
                total_text = " ".join(text_segments[:20])
                assert len(total_text.strip()) > 0

                non_empty_segments = [text for text in text_segments if text.strip()]
                assert len(non_empty_segments) > 0
