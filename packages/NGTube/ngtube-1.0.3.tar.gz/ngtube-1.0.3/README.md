# NGTube - YouTube Scraper

A comprehensive Python library for scraping YouTube data, including videos, comments, and channel profiles.

## ⚠️ Disclaimer

**This library is provided for educational and research purposes only.** Scraping YouTube data may violate YouTube's Terms of Service. Use at your own risk. The authors are not responsible for any misuse or legal consequences. Always respect robots.txt and implement appropriate rate limiting.

## Features

- **Video Extraction**: Extract detailed metadata from YouTube videos (title, views, likes, duration, tags, description, etc.)
- **Comment Extraction**: Extract comments from videos, including loading additional comments via YouTube's internal API
- **Channel Extraction**: Extract complete channel profile data (subscribers, description, featured video, video list with continuation support)
- **Shorts Extraction**: Fetch random shorts from YouTube's homepage with metadata and comments, and load unlimited shorts from the Shorts feed
- **Search Functionality**: Search YouTube with various filters (videos, channels, playlists, etc.) and country localization
- **Country Localization**: Support for different countries/regions (US, DE, UK, FR, etc.) for all API requests
- **Flexible Video Loading**: Load specific number of videos or all available videos from a channel
- **Clean Data Output**: Structured JSON-compatible data output
- **Modular Design**: Separate classes for different extraction tasks

## Installation

### 🚀 Quick Install (Recommended)

```bash
pip install NGTube
```

That's it! NGTube is now available on PyPI and ready to use.

### Option 1: Install from PyPI (Stable)

```bash
pip install NGTube
```

### Option 2: Install from Source

1. Clone or download the repository.
2. Navigate to the project directory.
3. Install the package using pip:

```bash
pip install .
```

### Option 3: Manual Installation

1. Clone or download the repository.
2. Ensure you have Python 3.6+ installed.
3. Install required dependencies:

```bash
pip install requests demjson3
```

4. Copy the `NGTube` folder to your project directory or add it to your Python path.

### Using setup.py

The `setup.py` file is used for packaging and installation. You can also install manually:

```bash
python setup.py install
```

However, using `pip install .` is recommended as it handles modern Python packaging better.

## Quick Start

### Extract Video Metadata

```python
from NGTube import Video

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video = Video(url)
metadata = video.extract_metadata()

print("Title:", metadata['title'])
print("Views:", metadata['view_count'])
print("Likes:", metadata['like_count'])
print("Duration:", metadata['duration_seconds'], "seconds")
```

### Extract Comments

```python
from NGTube import Comments

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
comments = Comments(url)

# Load all comments
comment_data = comments.get_comments()
print(f"Total comments: {len(comment_data['comments'])}")

# Load limited number of comments (faster)
comment_data_limited = comments.get_comments(max_comments=50)
print(f"Limited comments: {len(comment_data_limited['comments'])}")

for comment in comment_data['comments'][:3]:
    print(f"{comment['author']}: {comment['text'][:50]}...")
```

### Extract Channel Profile

```python
from NGTube import Channel

url = "https://www.youtube.com/@HandOfUncut"
channel = Channel(url)

# Load first 10 videos
profile = channel.extract_profile(max_videos=10)

print("Channel Title:", profile['title'])
print("Subscribers:", profile['stats']['subscribers'])
print("Videos loaded:", profile['stats']['loaded_videos_count'])

# Load all videos
profile_all = channel.extract_profile(max_videos='all')
print("Total videos:", profile_all['stats']['loaded_videos_count'])
```

### Fetch Random Shorts

```python
from NGTube import Shorts, Comments

shorts = Shorts()

# Fetch a single random short
short_data = shorts.fetch_short()
print("Title:", short_data['title'])
print("Video ID:", short_data['video_id'])
print("Channel:", short_data['channel_name'])
print("Thumbnail:", short_data['thumbnail'][0]['url'])

# Fetch comments for the short (same as regular videos)
comments = Comments(f"https://www.youtube.com/watch?v={short_data['video_id']}")
comment_data = comments.get_comments(max_comments=20)  # Limit comments
print(f"Comments: {len(comment_data['comments'])}")

# Fetch multiple shorts from the feed
shorts_feed = shorts.fetch_shorts_feed(max_shorts=20)
print(f"Loaded {len(shorts_feed)} shorts from feed")
for short in shorts_feed[:3]:
    print(f"Short: {short['video_id']} - Views: {short.get('view_count', 'N/A')}")
```

## Detailed Usage

### Video Class

```python
from NGTube import Video

video = Video("https://www.youtube.com/watch?v=VIDEO_ID")
metadata = video.extract_metadata()

# Available metadata keys:
# - title, view_count, like_count, duration_seconds
# - channel_name, channel_id, subscriber_count
# - description, tags, category, is_private
# - upload_date, published_time_text
```

### Comments Class

```python
from NGTube import Comments

comments = Comments("https://www.youtube.com/watch?v=VIDEO_ID")

# Load all comments
data = comments.get_comments()

# Load limited number of comments (recommended for performance)
data_limited = comments.get_comments(max_comments=100)

# Returns dictionary with:
# - 'top_comment': list of top comments
# - 'comments': list of regular comments

# Each comment contains:
# - author, text, likeCount, publishedTimeText
# - authorThumbnail, commentId, replyCount
```

### Channel Class

```python
from NGTube import Channel

channel = Channel("https://www.youtube.com/@ChannelHandle")

# Extract profile with specific number of videos
profile = channel.extract_profile(max_videos=50)

# Extract profile with all videos (may take time)
profile = channel.extract_profile(max_videos='all')

# Available profile data:
# - title, description, channel_id, channel_url
# - keywords, is_family_safe, links
# - subscriber_count_text, view_count_text, video_count_text
# - avatar (list of thumbnail dictionaries with url, width, height)
# - banner (list of banner image dictionaries with url, width, height)
# - featured_video (dict with videoId, title, description)
# - videos (list of video dictionaries)
# - shorts (list of short dictionaries)
# - playlists (list of playlist dictionaries)
# - stats (dict containing: subscribers, total_views, video_count, loaded_videos_count, loaded_shorts_count, loaded_playlists_count)
```

### Shorts Class

```python
from NGTube import Shorts, Comments

shorts = Shorts()

# Fetch a random short from YouTube's homepage
short_data = shorts.fetch_short()

# Fetch comments for the short (same as regular videos)
comments_obj = Comments(f"https://www.youtube.com/watch?v={short_data['video_id']}")
comment_data = comments_obj.get_comments(max_comments=50)

# Fetch multiple shorts from the Shorts feed (unlimited)
shorts_feed = shorts.fetch_shorts_feed(max_shorts=50)

# Available short data:
# - title: The title of the short
# - video_id: The YouTube video ID
# - channel_name: The channel name (with @)
# - channel_handle: The channel handle (without @)
# - channel_id: The channel ID
# - channel_url: The channel URL
# - sound_metadata: Music/sound information if available
# - thumbnail: List of thumbnail dictionaries with url, width, height
# - like_count: Number of likes
# - view_count: Number of views
# - comment_count: Number of comments
# - publish_date: Publication date
# - sequence_continuation: Token for fetching next short in sequence

# Comments for shorts work exactly like regular videos:
# Use Comments(f"https://www.youtube.com/watch?v={short_data['video_id']}").get_comments(max_comments=N)
# - title: The title of the short (may be empty for some)
# - thumbnail: Thumbnail URL
# - view_count: Number of views (text format)
# - published_time: Relative time (e.g., "2 hours ago")

# Comments data structure:
# - comment_id: Unique comment identifier
# - content: The comment text
# - published_time: When the comment was posted
# - reply_level: Nesting level (0 for top-level)
# - author: Dict with channel_id, display_name, avatar_thumbnail_url, is_verified, is_creator
# - toolbar: Dict with like_count and reply_count
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py`: Extract video metadata and comments
- `batch_processing.py`: Process multiple videos
- `channel_usage.py`: Extract channel profile data
- `shorts_usage.py`: Fetch random shorts from YouTube
- `WEB/`: Web-based demo application showcasing all features

Run any example:

```bash
python examples/basic_usage.py
```

### Web Demo

For an interactive web interface:

```bash
cd examples/WEB
pip install flask
python app.py
```

Then open http://127.0.0.1:5000 in your browser to try all NGTube features through a user-friendly interface.

#### Screenshots

![Web Panel Home](images/web_panel_home.png)
*Figure: Home page of the web panel with all tabs*

![Video Tab](images/video_tab.png)
*Figure: Video tab for metadata extraction*

![Comments Tab](images/comments_tab.png)
*Figure: Comments tab for comment extraction*

![Channel Tab](images/channel_tab.png)
*Figure: Channel tab for channel profile extraction*

![Search Tab](images/search_tab.png)
*Figure: Search tab for YouTube search*

## API Reference

### Core Classes

#### YouTubeCore
Base class for YouTube interactions.

- `__init__(url: str)`: Initialize with YouTube URL
- `fetch_html() -> str`: Fetch HTML content
- `extract_ytinitialdata(html: str) -> dict`: Extract ytInitialData
- `make_api_request(endpoint: str, payload: dict) -> dict`: Make API requests

#### CountryFilters
Predefined country filters for localization.

- `US`: United States (hl: "en", gl: "US")
- `DE`: Germany (hl: "de", gl: "DE")
- `UK`: United Kingdom (hl: "en", gl: "GB")
- `FR`: France (hl: "fr", gl: "FR")
- `ES`: Spain (hl: "es", gl: "ES")
- `IT`: Italy (hl: "it", gl: "IT")
- `JP`: Japan (hl: "ja", gl: "JP")

#### SearchFilters
Predefined search filters.

- `MOVIES`: Search for movies
- `CHANNELS`: Search for channels
- `PLAYLISTS`: Search for playlists
- `VIDEOS_TODAY`: Videos uploaded today
- `LAST_HOUR`: Videos uploaded in the last hour
- `SORT_BY_DATE`: Sort results by upload date

#### Video
Extract video metadata.

- `__init__(url: str)`: Initialize with video URL
- `extract_metadata() -> dict`: Extract and return video metadata

#### Comments
Extract video comments.

- `__init__(url: str)`: Initialize with video URL
- `get_comments(max_comments: int = None) -> dict`: Extract and return comments data
  - `max_comments`: Optional limit for number of comments to load (None = all available)

#### Channel
Extract channel profile and videos.

- `__init__(url: str, country: dict = None)`: Initialize with channel URL and optional country filter
- `extract_profile(max_videos: int | str = 200) -> dict`: Extract profile data
  - `max_videos`: Number of videos to load, or 'all' for all videos

#### Search
Perform YouTube searches with filters.

- `__init__(query: str, max_results: int = 50, filter: str = "", country: dict = None)`: Initialize search
  - `query`: Search query string
  - `max_results`: Maximum results to load
  - `filter`: Search filter (use SearchFilters constants)
  - `country`: Country filter (use CountryFilters constants)
- `perform_search()`: Execute the search
- `get_results() -> dict`: Get search results

#### Shorts
Fetch random shorts from YouTube.

- `__init__(country: dict = None)`: Initialize with optional country filter
- `fetch_short() -> dict`: Fetch a random short
- `fetch_shorts_feed(max_shorts: int = 50) -> list`: Fetch multiple shorts from feed

*Note: Comments for shorts work exactly like regular videos using the Comments class:
`Comments(f"https://www.youtube.com/watch?v={short_data['video_id']}").get_comments(max_comments=N)`*

### Utils Module

- `extract_number(text: str) -> int`: Extract numbers from text (handles German formatting)
- `extract_links(text: str) -> list`: Extract URLs from text

## Data Structures

### Video Metadata
```json
{
  "title": "Video Title",
  "view_count": 299955,
  "duration_in_seconds": 6994,
  "description": "Video description...",
  "tags": ["tag1", "tag2"],
  "video_id": "VIDEO_ID",
  "channel_id": "UC...",
  "is_owner_viewing": false,
  "is_crawlable": true,
  "thumbnail": {...},
  "allow_ratings": true,
  "author": "Channel Name",
  "is_private": false,
  "is_unplugged_corpus": false,
  "is_live_content": false,
  "like_count": 8547,
  "channel_name": "Channel Name",
  "category": "Gaming",
  "publish_date": "2023-12-01",
  "upload_date": "2023-12-01",
  "family_safe": true,
  "channel_url": "https://...",
  "subscriber_count": 1400000
}
```

### Comment Data
```json
{
  "top_comment": [...],
  "comments": [
    {
      "author": "Username",
      "text": "Comment text",
      "likeCount": 196,
      "publishedTimeText": "vor 1 Tag",
      "authorThumbnail": "https://...",
      "commentId": "...",
      "replyCount": 1
    }
  ]
}
```

### Channel Profile
```json
{
  "title": "Channel Title",
  "description": "Channel description...",
  "channelId": "UC...",
  "channelUrl": "https://...",
  "keywords": "keyword1 keyword2",
  "isFamilySafe": true,
  "links": ["https://..."],
  "subscriberCountText": "159.000 Abonnenten",
  "viewCountText": "84.770 Aufrufe",
  "videoCountText": "2583 Videos",
  "subscribers": 159000,
  "total_views": 84770,
  "video_count": 2583,
  "featured_video": {
    "videoId": "...",
    "title": "Featured Video Title",
    "description": "Featured video description..."
  },
  "videos": [
    {
      "videoId": "...",
      "title": "Video Title",
      "publishedTimeText": "vor 1 Tag",
      "viewCountText": "40.773 Aufrufe",
      "lengthText": "1:02:58",
      "thumbnails": [...]
    }
  ],
  "loaded_videos_count": 1
}
```

## Limitations

- **Rate Limiting**: YouTube may rate-limit requests. Add delays between requests for bulk operations.
- **Comment Limits**: Comments can be limited using the `max_comments` parameter in `get_comments(max_comments=N)`. Without limits, YouTube may restrict the number of comments loaded.
- **Video Limits**: Channel video extraction may be limited by YouTube's pagination.
- **Shorts Comments**: Shorts use the same comment system as regular videos, so unlimited comments are supported.
- **Terms of Service**: This library is for educational purposes. Respect YouTube's Terms of Service and robots.txt.

## Troubleshooting

- **Import Errors**: Ensure NGTube folder is in your Python path
- **API Errors**: YouTube changes their internal APIs frequently. The library uses current endpoints as of December 2025.
- **Missing Data**: Some videos/channels may have restricted data access

## Contributing

This library is maintained for educational purposes. Feel free to submit issues or improvements.

## License

This project can be used by anyone with attribution.