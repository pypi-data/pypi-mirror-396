# innertubei

**Fast, async-first Python library for YouTube's internal API (Innertube)**

## Installation

### Using uv (recommended)
```bash
uv add innertubei
```

### Using pip
```bash
pip install innertubei
```

## Quick Start

```python
import asyncio
from innertubei import Search, Video, Playlist, Transcript, Suggestions

async def main():
    # Search videos, channels, playlists
    search = Search('NoCopyrightSounds', limit=5)
    results = await search.next()

    # Get video details + formats
    video = await Video.get('E07s5ZYygMg')

    # Get playlist info + videos
    playlist = await Playlist.get('PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')

    # Get video transcript
    transcript = await Transcript.get('https://www.youtube.com/watch?v=E07s5ZYygMg')

    # Get search suggestions
    suggestions = await Suggestions.get('python tutorial')

asyncio.run(main())
```

For detailed examples, see [`example.py`](example.py).

## Development

### Using uv (recommended)
```bash
# Clone and setup
git clone https://github.com/ohmyarthur/innertubei
cd innertubei
uv sync

# Run examples
uv run example.py

# Run tests
uv run uv run python -m pytest
```

### Using traditional tools
```bash
pip install -e .
python example.py
```

## License
MIT License. See [LICENSE](/LICENSE) for details.

## Credits
- **Based on**: [py-yt-search](https://github.com/AshokShau/py-yt-search) by [AshokShau](https://github.com/AshokShau) - the original foundation
- **Maintained by**: [ohmyarthur](https://github.com/ohmyarthur)
- **Inspiration**: [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) by Alex Mercer
