"""
NGTube Search Module

This module provides functionality to search YouTube and extract search results.
"""

from ..core import YouTubeCore
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from typing import Optional

class SearchFilters:
    """
    Predefined search filters for YouTube search.
    """
    MOVIES = "EgIQBA%3D%3D"
    CHANNELS = "EgIQAg%3D%3D"
    PLAYLISTS = "EgIQAw%3D%3D"
    VIDEOS_TODAY = "EgIIAg%3D%3D"
    LAST_HOUR = "EgIIAQ%3D%3D"
    SORT_BY_DATE = "CAI%3D"

class Search:
    """
    Class to perform YouTube searches and extract results.

    Attributes:
        query (str): The search query.
        max_results (int): Maximum number of results to load.
        results (list): List of video results.
        estimated_results (int): Estimated total results.
    """

    def __init__(self, query: str, max_results: int = 50, filter: str = "", country: Optional[dict] = None):
        """
        Initialize the Search with a query.

        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to load.
            filter (str): Search filter, use SearchFilters constants or custom params string.
            country (dict): Country filter with 'hl' and 'gl' keys, use CountryFilters constants.
        """
        if country is None:
            from ..core import CountryFilters
            country = CountryFilters.US
        self.country = country
        self.query = query
        self.max_results = max_results
        self.filter = filter
        self.params = filter if isinstance(filter, str) else (filter.value if hasattr(filter, 'value') else str(filter))
        self.results = []
        self.estimated_results = 0
        self.core = YouTubeCore("https://www.youtube.com")
        self.visitor_data = self.core.extract_visitor_data(self.core.fetch_html())
        self.client_version = self.core.get_client_version("2.20251208.06.00")
        self.url = "https://www.youtube.com/youtubei/v1/search?prettyPrint=false"
        self.payload = {
            "context": {
                "client": {
                    "hl": self.country["hl"],
                    "gl": self.country["gl"],
                    "clientName": "WEB",
                    "clientVersion": self.client_version,
                    "visitorData": self.visitor_data
                }
            },
            "query": query
        }
        if self.params:
            self.payload["params"] = self.params
        if self.params:
            self.payload["params"] = self.params
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 OPR/124.0.0.0"
        }
        self.timeout = 10
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        """Create a session with retries to reduce transient failures."""
        session = requests.Session()
        session.headers.update(self.headers)
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def perform_search(self):
        """
        Perform the search and load results.
        """
        continuation = None
        while len(self.results) < self.max_results:
            if continuation:
                self.payload["continuation"] = continuation
            response = self.session.post(self.url, json=self.payload, timeout=self.timeout)
            if response.status_code != 200:
                break
            data = response.json()
            items, estimated, cont = self._parse_results(data)
            if not self.estimated_results:
                self.estimated_results = estimated
            self.results.extend(items)
            continuation = cont
            if not continuation:
                break
            time.sleep(0.3)

    def _parse_results(self, data):
        if not data:
            return [], 0, None
        estimated_results = int(data.get("estimatedResults", "0"))
        contents = data.get("contents", {}).get("twoColumnSearchResultsRenderer", {}).get("primaryContents", {}).get("sectionListRenderer", {}).get("contents", [])
        continuation = None
        items = []
        for item in contents:
            if "itemSectionRenderer" in item:
                for content in item["itemSectionRenderer"]["contents"]:
                    if "videoRenderer" in content:
                        video = content["videoRenderer"]
                        video_info = {
                            "type": "video",
                            "videoId": video.get("videoId"),
                            "title": video.get("title", {}).get("runs", [{}])[0].get("text"),
                            "channel": video.get("longBylineText", {}).get("runs", [{}])[0].get("text"),
                            "publishedTime": video.get("publishedTimeText", {}).get("simpleText"),
                            "length": video.get("lengthText", {}).get("simpleText"),
                            "viewCount": video.get("viewCountText", {}).get("simpleText"),
                            "thumbnail": video.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url")
                        }
                        items.append(video_info)
                    elif "channelRenderer" in content:
                        channel = content["channelRenderer"]
                        channel_info = {
                            "type": "channel",
                            "channelId": channel.get("channelId"),
                            "title": channel.get("title", {}).get("simpleText"),
                            "description": " ".join([run.get("text", "") for run in channel.get("descriptionSnippet", {}).get("runs", [])]),
                            "subscriberCount": channel.get("videoCountText", {}).get("simpleText"),  # Note: This seems to be videoCount in the data
                            "thumbnail": channel.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url")
                        }
                        items.append(channel_info)
                    elif "movieRenderer" in content:
                        movie = content["movieRenderer"]
                        movie_info = {
                            "type": "movie",
                            "videoId": movie.get("videoId"),
                            "title": movie.get("title", {}).get("runs", [{}])[0].get("text"),
                            "description": " ".join([run.get("text", "") for run in movie.get("descriptionSnippet", {}).get("runs", [])]),
                            "channel": movie.get("longBylineText", {}).get("runs", [{}])[0].get("text"),
                            "length": movie.get("lengthText", {}).get("simpleText"),
                            "thumbnail": movie.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url")
                        }
                        items.append(movie_info)
                    elif "lockupViewModel" in content:
                        lockup = content["lockupViewModel"]
                        metadata = lockup.get("metadata", {}).get("lockupMetadataViewModel", {})
                        title = metadata.get("title", {}).get("content", "")
                        content_metadata = metadata.get("metadata", {}).get("contentMetadataViewModel", {})
                        metadata_rows = content_metadata.get("metadataRows", [])
                        channel = ""
                        video_count = ""
                        if metadata_rows:
                            parts = metadata_rows[0].get("metadataParts", [])
                            if parts:
                                channel = parts[0].get("text", {}).get("content", "")
                            if len(parts) > 1:
                                video_count = parts[1].get("text", {}).get("content", "")
                        playlist_info = {
                            "type": "playlist",
                            "title": title,
                            "channel": channel,
                            "videoCount": video_count,
                            "thumbnail": lockup.get("contentImage", {}).get("collectionThumbnailViewModel", {}).get("primaryThumbnail", {}).get("thumbnailViewModel", {}).get("image", {}).get("sources", [{}])[0].get("url", "")
                        }
                        items.append(playlist_info)
            elif "continuationItemRenderer" in item:
                continuation = item["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
        # Check for continuation in onResponseReceivedCommands
        if "onResponseReceivedCommands" in data:
            for command in data["onResponseReceivedCommands"]:
                if "appendContinuationItemsAction" in command:
                    for item in command["appendContinuationItemsAction"]["continuationItems"]:
                        if "itemSectionRenderer" in item:
                            for content in item["itemSectionRenderer"]["contents"]:
                                if "videoRenderer" in content:
                                    video = content["videoRenderer"]
                                    video_info = {
                                        "type": "video",
                                        "videoId": video.get("videoId"),
                                        "title": video.get("title", {}).get("runs", [{}])[0].get("text"),
                                        "channel": video.get("longBylineText", {}).get("runs", [{}])[0].get("text"),
                                        "publishedTime": video.get("publishedTimeText", {}).get("simpleText"),
                                        "length": video.get("lengthText", {}).get("simpleText"),
                                        "viewCount": video.get("viewCountText", {}).get("simpleText"),
                                        "thumbnail": video.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url")
                                    }
                                    items.append(video_info)
                                elif "channelRenderer" in content:
                                    channel = content["channelRenderer"]
                                    channel_info = {
                                        "type": "channel",
                                        "channelId": channel.get("channelId"),
                                        "title": channel.get("title", {}).get("simpleText"),
                                        "description": " ".join([run.get("text", "") for run in channel.get("descriptionSnippet", {}).get("runs", [])]),
                                        "subscriberCount": channel.get("videoCountText", {}).get("simpleText"),
                                        "thumbnail": channel.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url")
                                    }
                                    items.append(channel_info)
                                elif "movieRenderer" in content:
                                    movie = content["movieRenderer"]
                                    movie_info = {
                                        "type": "movie",
                                        "videoId": movie.get("videoId"),
                                        "title": movie.get("title", {}).get("runs", [{}])[0].get("text"),
                                        "description": " ".join([run.get("text", "") for run in movie.get("descriptionSnippet", {}).get("runs", [])]),
                                        "channel": movie.get("longBylineText", {}).get("runs", [{}])[0].get("text"),
                                        "length": movie.get("lengthText", {}).get("simpleText"),
                                        "thumbnail": movie.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url")
                                    }
                                    items.append(movie_info)
                                elif "lockupViewModel" in content:
                                    lockup = content["lockupViewModel"]
                                    metadata = lockup.get("metadata", {}).get("lockupMetadataViewModel", {})
                                    title = metadata.get("title", {}).get("content", "")
                                    content_metadata = metadata.get("metadata", {}).get("contentMetadataViewModel", {})
                                    metadata_rows = content_metadata.get("metadataRows", [])
                                    channel = ""
                                    video_count = ""
                                    if metadata_rows:
                                        parts = metadata_rows[0].get("metadataParts", [])
                                        if parts:
                                            channel = parts[0].get("text", {}).get("content", "")
                                        if len(parts) > 1:
                                            video_count = parts[1].get("text", {}).get("content", "")
                                    playlist_info = {
                                        "type": "playlist",
                                        "title": title,
                                        "channel": channel,
                                        "videoCount": video_count,
                                        "thumbnail": lockup.get("contentImage", {}).get("collectionThumbnailViewModel", {}).get("primaryThumbnail", {}).get("thumbnailViewModel", {}).get("image", {}).get("sources", [{}])[0].get("url", "")
                                    }
                                    items.append(playlist_info)
                        elif "continuationItemRenderer" in item:
                            continuation = item["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
        return items, estimated_results, continuation

    def get_results(self):
        """
        Get the search results.

        Returns:
            dict: Dictionary with query, filter, params, estimated_results, loaded_items, and items list.
        """
        return {
            "query": self.query,
            "filter": self.filter,
            "params": self.params,
            "estimated_results": self.estimated_results,
            "loaded_items": len(self.results),
            "items": self.results
        }
