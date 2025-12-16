"""
NGTube Video Module

This module provides functionality to extract video metadata from YouTube.
"""

from ..core import YouTubeCore
from ..utils import extract_number

class Video:
    """
    Class to represent a YouTube video and extract its metadata.

    Attributes:
        url (str): The YouTube video URL.
        data (dict): The extracted video data.
    """

    def __init__(self, url: str):
        """
        Initialize the Video with a URL.

        Args:
            url (str): The YouTube video URL.
        """
        self.url = url
        self.core = YouTubeCore(url)
        self.data = {}

    def extract_metadata(self) -> dict:
        """
        Extract video metadata from ytInitialData and ytInitialPlayerResponse.

        Returns:
            dict: A dictionary containing video metadata.
        """
        html = self.core.fetch_html()
        data = self.core.extract_ytinitialdata(html)
        player_data = self.core.extract_ytinitialplayerresponse(html)

        # Extract from videoDetails in player_data
        if 'videoDetails' in player_data:
            vd = player_data['videoDetails']
            self.data['title'] = vd.get('title', '')
            self.data['view_count'] = int(vd.get('viewCount', '0'))
            duration_seconds = vd.get('lengthSeconds', '0')
            self.data['duration_in_seconds'] = int(duration_seconds) if duration_seconds.isdigit() else 0
            self.data['description'] = vd.get('shortDescription', '')
            self.data['tags'] = vd.get('keywords', [])
            self.data['video_id'] = vd.get('videoId', '')
            self.data['channel_id'] = vd.get('channelId', '')
            self.data['is_owner_viewing'] = vd.get('isOwnerViewing', False)
            self.data['is_crawlable'] = vd.get('isCrawlable', True)
            self.data['thumbnail'] = vd.get('thumbnail', {}).get('thumbnails', [])
            self.data['allow_ratings'] = vd.get('allowRatings', True)
            self.data['author'] = vd.get('author', '')
            self.data['is_private'] = vd.get('isPrivate', False)
            self.data['is_unplugged_corpus'] = vd.get('isUnpluggedCorpus', False)
            self.data['is_live_content'] = vd.get('isLiveContent', False)

        # Extract from microformat in player_data
        def find_microformat(obj):
            if isinstance(obj, dict):
                if 'playerMicroformatRenderer' in obj:
                    pmr = obj['playerMicroformatRenderer']
                    if 'likeCount' in pmr and not self.data.get('like_count'):
                        self.data['like_count'] = extract_number(pmr['likeCount'])
                    if 'ownerChannelName' in pmr:
                        self.data['channel_name'] = pmr['ownerChannelName']
                    if 'category' in pmr:
                        self.data['category'] = pmr['category']
                    if 'publishDate' in pmr:
                        self.data['publish_date'] = pmr['publishDate']
                    if 'uploadDate' in pmr:
                        self.data['upload_date'] = pmr['uploadDate']
                    if 'isFamilySafe' in pmr:
                        self.data['family_safe'] = pmr['isFamilySafe']
                    if 'ownerProfileUrl' in pmr:
                        self.data['channel_url'] = pmr['ownerProfileUrl']
                    return True
                for v in obj.values():
                    if find_microformat(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_microformat(item):
                        return True
            return False
        find_microformat(player_data)

        # Fallback to ytInitialData if not found
        if not self.data.get('title'):
            def find_title(obj):
                if isinstance(obj, dict):
                    if 'videoPrimaryInfoRenderer' in obj and 'title' in obj['videoPrimaryInfoRenderer'] and 'runs' in obj['videoPrimaryInfoRenderer']['title']:
                        title_parts = obj['videoPrimaryInfoRenderer']['title']['runs']
                        title = ''.join([part['text'] for part in title_parts])
                        self.data['title'] = title
                        return True
                    for v in obj.values():
                        if find_title(v):
                            return True
                elif isinstance(obj, list):
                    for item in obj:
                        if find_title(item):
                            return True
                return False
            find_title(data)

        # Extract views if not from videoDetails
        if not self.data.get('view_count'):
            def find_views(obj):
                if isinstance(obj, dict):
                    if 'videoPrimaryInfoRenderer' in obj and 'viewCount' in obj['videoPrimaryInfoRenderer'] and 'videoViewCountRenderer' in obj['videoPrimaryInfoRenderer']['viewCount'] and 'viewCount' in obj['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer'] and 'simpleText' in obj['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['viewCount']:
                        views_text = obj['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
                        self.data['view_count'] = extract_number(views_text)
                        return True
                    for v in obj.values():
                        if find_views(v):
                            return True
                elif isinstance(obj, list):
                    for item in obj:
                        if find_views(item):
                            return True
                return False
            find_views(data)

        # Extract likes
        def find_likes(obj):
            if isinstance(obj, dict):
                if 'likeCountIfLikedNumber' in obj:
                    self.data['like_count'] = int(obj['likeCountIfLikedNumber'])
                    return True
                for v in obj.values():
                    if find_likes(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_likes(item):
                        return True
            return False
        find_likes(data)

        # Extract subscriber count
        subscriber_text = None
        def find_subscriber(obj):
            nonlocal subscriber_text
            if isinstance(obj, dict):
                if 'subscriberCountText' in obj and 'simpleText' in obj['subscriberCountText']:
                    subscriber_text = obj['subscriberCountText']['simpleText']
                    return True
                for v in obj.values():
                    if find_subscriber(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_subscriber(item):
                        return True
            return False
        find_subscriber(data)
        if subscriber_text:
            self.data['subscriber_count'] = extract_number(subscriber_text)

        return self.data