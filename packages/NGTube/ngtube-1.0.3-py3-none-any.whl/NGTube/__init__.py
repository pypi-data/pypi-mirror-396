"""
NGTube - A Python library for YouTube data extraction

This package provides modules for extracting data from YouTube videos, channels, comments, and searches.
"""

from .core import YouTubeCore, CountryFilters
from .video.video import Video
from .comments.comments import Comments
from .channel.channel import Channel
from .search.search import Search, SearchFilters
from .shorts.shorts import Shorts

__version__ = "1.0.3"
__author__ = "NGxD TV"