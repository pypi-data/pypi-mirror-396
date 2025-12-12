from __future__ import annotations

from typing import Union


def getValue(source: dict, path: list[str]) -> Union[str, int, dict, None]:
    if source is None:
        return None

    value = source
    for key in path:
        if value is None:
            return None

        if type(key) is str:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        elif type(key) is int:
            if isinstance(value, list) and 0 <= key < len(value):
                value = value[key]
            else:
                return None
    return value


def getVideoId(video_link: str) -> str:
    if not video_link or not isinstance(video_link, str):
        return None

    try:
        if "youtu.be" in video_link:
            if video_link.endswith("/"):
                return video_link.split("/")[-2]
            return video_link.split("/")[-1]
        elif "youtube.com" in video_link and "v=" in video_link:
            if "&" not in video_link:
                return video_link[video_link.index("v=") + 2 :]
            return video_link[video_link.index("v=") + 2 : video_link.index("&")]
        else:
            return video_link if video_link else None
    except (ValueError, IndexError):
        return None
