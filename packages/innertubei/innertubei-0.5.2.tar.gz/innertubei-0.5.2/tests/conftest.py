from typing import Any, Dict

import pytest


@pytest.fixture(scope="session")
def stable_test_data():
    return {
        "video_ids": {
            "popular_music": "E07s5ZYygMg",
            "rick_roll": "dQw4w9WgXcQ",
            "old_stable": "9bZkp7q19f0",
        },
        "channel_ids": {
            "ncs": "UC_aEa8K-EOJ3D6gOs7HcyNg",
            "youtube": "UCBR8-60-B28hp2BmDPdntcQ",
            "ted": "UCAuUUnT6oDeKwE6v1NGQxug",
        },
        "playlist_ids": {
            "ncs_house": "PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK",
            "youtube_rewind": "PL590L5WQmH8fJ54F369BLDSqIwcs-TCfs",
        },
        "search_queries": {
            "popular": ["music", "tutorial", "news", "gaming", "cooking"],
            "technical": ["python", "javascript", "programming", "coding"],
            "safe": ["nature", "animals", "science", "education"],
        },
        "hashtags": {
            "popular": ["music", "gaming", "shorts", "viral", "trending"],
            "safe": ["nature", "art", "education", "travel", "food"],
        },
    }


@pytest.fixture
def mock_response_data():
    return {
        "empty_search": {"result": []},
        "single_video": {
            "result": [
                {
                    "id": "test123",
                    "title": "Test Video",
                    "link": "https://www.youtube.com/watch?v=test123",
                    "channel": {"name": "Test Channel", "id": "UCtest123"},
                }
            ]
        },
        "playlist_basic": {
            "id": "PLtest123",
            "title": "Test Playlist",
            "videos": [
                {
                    "id": "video1",
                    "title": "Video 1",
                    "link": "https://www.youtube.com/watch?v=video1",
                }
            ],
            "channel": {"name": "Test Channel", "id": "UCtest123"},
        },
    }


class TestHelpers:
    @staticmethod
    def validate_video_structure(video: Dict[str, Any]) -> bool:
        required_fields = ["id", "title"]
        return all(field in video for field in required_fields)

    @staticmethod
    def validate_playlist_structure(playlist: Dict[str, Any]) -> bool:
        required_fields = ["id", "title", "videos"]
        return all(field in playlist for field in required_fields)

    @staticmethod
    def validate_channel_structure(channel: Dict[str, Any]) -> bool:
        required_fields = ["id", "title"]
        return all(field in channel for field in required_fields)

    @staticmethod
    def count_valid_items(items: list, validator) -> int:
        return sum(1 for item in items if validator(item))


@pytest.fixture
def test_helpers():
    return TestHelpers


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )


def pytest_collection_modifyitems(config, items):
    network_marker = pytest.mark.network
    for item in items:
        item.add_marker(network_marker)

    slow_marker = pytest.mark.slow
    slow_test_patterns = ["pagination", "multiple", "integration"]

    for item in items:
        if any(pattern in item.name.lower() for pattern in slow_test_patterns):
            item.add_marker(slow_marker)


def assert_youtube_url(url: str, video_id: str = None):
    assert isinstance(url, str)
    assert "youtube.com" in url
    if video_id:
        assert video_id in url


def assert_non_empty_string(value: str, field_name: str = "field"):
    assert isinstance(value, str), f"{field_name} should be a string"
    assert len(value.strip()) > 0, f"{field_name} should not be empty"


def assert_valid_video_id(video_id: str):
    assert isinstance(video_id, str)
    assert len(video_id) >= 10
    assert video_id.replace("-", "").replace("_", "").isalnum()


pytest.assert_youtube_url = assert_youtube_url
pytest.assert_non_empty_string = assert_non_empty_string
pytest.assert_valid_video_id = assert_valid_video_id
