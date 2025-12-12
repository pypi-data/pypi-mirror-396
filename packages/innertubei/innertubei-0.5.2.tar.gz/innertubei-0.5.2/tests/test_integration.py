import pytest

from innertubei import (
    Channel,
    ChannelsSearch,
    Hashtag,
    Playlist,
    Search,
    Suggestions,
    Transcript,
    Video,
    VideosSearch,
)


class TestSearchToVideoWorkflow:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_search_then_get_video_details(self):
        search = VideosSearch("NCS House", limit=3)
        search_result = await search.next()

        assert search_result is not None
        assert len(search_result["result"]) > 0

        first_video = search_result["result"][0]
        video_id = first_video.get("id")

        if video_id:
            video_details = await Video.get(video_id)

            if video_details:
                assert video_details["id"] == video_id
                assert "title" in video_details


class TestPlaylistToVideoWorkflow:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_playlist_to_video_details(self):
        playlist_url = (
            "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
        )
        playlist = await Playlist.get(playlist_url)

        if playlist and playlist.get("videos"):
            first_video = playlist["videos"][0]
            video_id = first_video.get("id")

            if video_id:
                video_details = await Video.get(video_id)

                if video_details:
                    assert video_details["id"] == video_id


class TestChannelToPlaylistWorkflow:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_channel_to_playlist_details(self):
        channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"
        channel = await Channel.get(channel_id)

        if channel and channel.get("playlists"):
            first_playlist = channel["playlists"][0]
            playlist_id = first_playlist.get("id")

            if playlist_id:
                playlist_details = await Playlist.get(playlist_id)

                if playlist_details:
                    assert playlist_details["id"] == playlist_id


class TestSearchVariationsWorkflow:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_different_search_types_same_query(self):
        query = "NoCopyrightSounds"

        general_search = Search(query, limit=2)
        videos_search = VideosSearch(query, limit=2)
        channels_search = ChannelsSearch(query, limit=2)

        general_result = await general_search.next()
        videos_result = await videos_search.next()
        channels_result = await channels_search.next()

        assert general_result is not None
        assert videos_result is not None
        assert channels_result is not None

        assert "result" in general_result
        assert "result" in videos_result
        assert "result" in channels_result


class TestSuggestionsToSearchWorkflow:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_suggestions_to_search_workflow(self):
        suggestions = await Suggestions.get("python")

        if suggestions and suggestions["result"]:
            first_suggestion = suggestions["result"][0]

            search = VideosSearch(first_suggestion, limit=2)
            search_result = await search.next()

            assert search_result is not None
            assert "result" in search_result


class TestTranscriptWithVideoWorkflow:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_search_video_then_transcript(self):
        search = VideosSearch("Harry Styles Watermelon Sugar", limit=1)
        search_result = await search.next()

        if search_result and search_result["result"]:
            first_video = search_result["result"][0]
            video_id = first_video.get("id")

            if video_id:
                transcript = await Transcript.get(video_id)

                assert transcript is not None
                assert "segments" in transcript
                assert "languages" in transcript


class TestHashtagToVideoWorkflow:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_hashtag_to_video_details(self):
        hashtag = Hashtag("music", limit=2)
        hashtag_result = await hashtag.next()

        if hashtag_result and hashtag_result["result"]:
            first_video = hashtag_result["result"][0]
            video_id = first_video.get("id")

            if video_id:
                video_details = await Video.get(video_id)

                if video_details:
                    assert video_details["id"] == video_id


class TestErrorHandlingIntegration:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_invalid_ids_across_components(self):
        invalid_id = "InvalidId123"

        video_result = await Video.get(invalid_id)
        assert video_result is None

        playlist_result = await Playlist.get(invalid_id)
        assert playlist_result is None

        channel_result = await Channel.get(invalid_id)
        assert channel_result is None

        transcript_result = await Transcript.get(invalid_id)
        assert transcript_result is None or (
            isinstance(transcript_result, dict)
            and len(transcript_result.get("segments", [])) == 0
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_empty_results_handling(self):
        unlikely_query = "xyzabc123nonexistentquery789"

        search = VideosSearch(unlikely_query, limit=1)
        result = await search.next()

        assert result is not None
        assert "result" in result
        assert isinstance(result["result"], list)

        suggestions = await Suggestions.get(unlikely_query)
        assert suggestions is not None
        assert "result" in suggestions


class TestPaginationIntegration:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_search_pagination_consistency(self):
        search = VideosSearch("music", limit=5)

        first_page = await search.next()
        second_page = await search.next()

        assert first_page is not None

        if second_page and second_page["result"]:
            first_ids = {
                item.get("id") for item in first_page["result"] if item.get("id")
            }
            second_ids = {
                item.get("id") for item in second_page["result"] if item.get("id")
            }

            overlap = first_ids.intersection(second_ids)
            assert len(overlap) <= 2, f"Too many duplicates between pages: {overlap}"
