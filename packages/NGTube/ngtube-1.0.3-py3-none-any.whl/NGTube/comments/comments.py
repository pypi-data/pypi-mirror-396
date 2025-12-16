"""
NGTube Comments Module

This module provides functionality to extract comments from YouTube videos.
"""

import time
from typing import Optional
from ..core import YouTubeCore
from .. import utils

class Comments:
    """
    Class to extract comments from a YouTube video.

    Attributes:
        url (str): The YouTube video URL.
        comments (list): List of extracted comments.
        top_comments (list): List of top/pinned comments.
    """

    def __init__(self, url: str, country: Optional[dict] = None):
        """
        Initialize the Comments with a URL.

        Args:
            url (str): The YouTube video URL.
            country (dict): Country filter with 'hl' and 'gl' keys, use CountryFilters constants.
        """
        if country is None:
            from ..core import CountryFilters
            country = CountryFilters.US
        self.country = country
        self.url = url
        self.core = YouTubeCore(url)
        self.comments = []
        self.top_comments = []
        self.visitor_data = self.core.extract_visitor_data(self.core.fetch_html())

    def extract_initial_comments(self, data: dict):
        """
        Extract initial comments from ytInitialData.

        Args:
            data (dict): The ytInitialData JSON.
        """
        # Extract microformat comments as top comments
        def find_microformat_comments(obj):
            if isinstance(obj, dict):
                if 'microformat' in obj and 'microformatDataRenderer' in obj['microformat'] and 'videoDetails' in obj['microformat']['microformatDataRenderer'] and 'comments' in obj['microformat']['microformatDataRenderer']['videoDetails']:
                    comments_list = obj['microformat']['microformatDataRenderer']['videoDetails']['comments']
                    for comment in comments_list:
                        if comment.get('type') == 'https://schema.org/Comment':
                            micro_comment = {
                                'author': comment.get('author', {}).get('name', ''),
                                'text': comment.get('text', ''),
                                'dateCreated': comment.get('dateCreated', ''),
                                'url': comment.get('author', {}).get('url', ''),
                                'alternateName': comment.get('author', {}).get('alternateName', ''),
                                'upvoteCount': comment.get('upvoteCount', 0)
                            }
                            self.top_comments.append(micro_comment)
                for v in obj.values():
                    find_microformat_comments(v)
            elif isinstance(obj, list):
                for item in obj:
                    find_microformat_comments(item)
        find_microformat_comments(data)

        # Extract top comments from engagement panel
        def find_top_comments(obj):
            if isinstance(obj, dict):
                if 'engagementPanelSectionListRenderer' in obj and obj['engagementPanelSectionListRenderer'].get('panelIdentifier') == 'engagement-panel-comments-section':
                    content = obj['engagementPanelSectionListRenderer'].get('content', {})
                    section_list = content.get('sectionListRenderer', {})
                    contents = section_list.get('contents', [])
                    for item in contents:
                        if 'itemSectionRenderer' in item:
                            sub_contents = item['itemSectionRenderer'].get('contents', [])
                            for sub_item in sub_contents:
                                if 'commentThreadRenderer' in sub_item:
                                    thread = sub_item['commentThreadRenderer']
                                    if thread.get('isTopLevelThread') and thread.get('isPinned', False):
                                        # This is a top/pinned comment
                                        comment_renderer = thread.get('comment', {}).get('commentRenderer', {})
                                        author = comment_renderer.get('authorText', {}).get('simpleText', '')
                                        text_runs = comment_renderer.get('contentText', {}).get('runs', [])
                                        text = ''.join([run.get('text', '') for run in text_runs])
                                        like_count = comment_renderer.get('likeCount', 0)
                                        published_time = comment_renderer.get('publishedTimeText', {}).get('runs', [{}])[0].get('text', '')
                                        author_thumb = comment_renderer.get('authorThumbnail', {}).get('thumbnails', [{}])[0].get('url', '')
                                        comment_id = comment_renderer.get('commentId', '')
                                        reply_count = comment_renderer.get('replyCount', 0)
                                        top_comment = {
                                            'author': author,
                                            'text': text,
                                            'likeCount': like_count,
                                            'publishedTimeText': published_time,
                                            'authorThumbnail': author_thumb,
                                            'commentId': comment_id,
                                            'replyCount': reply_count
                                        }
                                        self.top_comments.append(top_comment)
                                    elif thread.get('isTopLevelThread'):
                                        # Regular top-level comment
                                        comment_renderer = thread.get('comment', {}).get('commentRenderer', {})
                                        author = comment_renderer.get('authorText', {}).get('simpleText', '')
                                        text_runs = comment_renderer.get('contentText', {}).get('runs', [])
                                        text = ''.join([run.get('text', '') for run in text_runs])
                                        like_count = comment_renderer.get('likeCount', 0)
                                        published_time = comment_renderer.get('publishedTimeText', {}).get('runs', [{}])[0].get('text', '')
                                        author_thumb = comment_renderer.get('authorThumbnail', {}).get('thumbnails', [{}])[0].get('url', '')
                                        comment_id = comment_renderer.get('commentId', '')
                                        reply_count = comment_renderer.get('replyCount', 0)
                                        comment = {
                                            'author': author,
                                            'text': text,
                                            'likeCount': like_count,
                                            'publishedTimeText': published_time,
                                            'authorThumbnail': author_thumb,
                                            'commentId': comment_id,
                                            'replyCount': reply_count
                                        }
                                        self.comments.append(comment)
                for v in obj.values():
                    find_top_comments(v)
            elif isinstance(obj, list):
                for item in obj:
                    find_top_comments(item)
        find_top_comments(data)

    def load_more_comments(self, data: dict, max_comments: Optional[int] = None):
        """
        Load additional comments via YouTube's API.

        Args:
            data (dict): The ytInitialData JSON.
            max_comments (int, optional): Maximum number of comments to load. If None, loads all available.
        """
        # Find continuation token and load more comments
        continuation_token = None
        def find_continuation(obj):
            nonlocal continuation_token
            if isinstance(obj, dict):
                if 'engagementPanelSectionListRenderer' in obj and obj['engagementPanelSectionListRenderer'].get('panelIdentifier') == 'engagement-panel-comments-section':
                    content = obj['engagementPanelSectionListRenderer'].get('content', {})
                    section_list = content.get('sectionListRenderer', {})
                    contents = section_list.get('contents', [])
                    for item in contents:
                        if 'itemSectionRenderer' in item:
                            sub_contents = item['itemSectionRenderer'].get('contents', [])
                            for sub_item in sub_contents:
                                if 'continuationItemRenderer' in sub_item:
                                    endpoint = sub_item['continuationItemRenderer'].get('continuationEndpoint', {})
                                    command = endpoint.get('continuationCommand', {})
                                    continuation_token = command.get('token')
                                    return True
                for v in obj.values():
                    if find_continuation(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_continuation(item):
                        return True
            return False
        find_continuation(data)

        if continuation_token:
            # Build payload and make API requests
            current_continuation = continuation_token
            max_calls = 50  # Increased from 10 to allow loading more comments
            call_count = 0
            while current_continuation and call_count < max_calls and (max_comments is None or len(self.comments) < max_comments):
                payload = {
                    "context": {
                        "client": {
                            "hl": self.country["hl"],
                            "gl": self.country["gl"],
                            "clientName": "WEB",
                            "clientVersion": "2.20251208.06.00",
                            "visitorData": self.visitor_data
                        }
                    },
                    "continuation": current_continuation
                }

                api_data = self.core.make_api_request("https://www.youtube.com/youtubei/v1/next", payload)
                comments_before = len(self.comments)

                # Extract comments from API response
                def extract_api_comments(obj):
                    if isinstance(obj, dict):
                        if 'commentEntityPayload' in obj:
                            payload = obj['commentEntityPayload']
                            properties = payload.get('properties', {})
                            author = payload.get('author', {})
                            toolbar = payload.get('toolbar', {})
                            comment = {
                                'author': author.get('displayName', properties.get('authorButtonA11y', '')),
                                'text': properties.get('content', {}).get('content', ''),
                                'likeCount': utils.extract_number(toolbar.get('likeCountNotliked', '0')),
                                'publishedTimeText': properties.get('publishedTime', ''),
                                'authorThumbnail': author.get('avatarThumbnailUrl', ''),
                                'commentId': properties.get('commentId', ''),
                                'replyCount': int(toolbar.get('replyCount', 0) or 0)
                            }
                            self.comments.append(comment)
                        for v in obj.values():
                            extract_api_comments(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_api_comments(item)
                extract_api_comments(api_data)

                comments_after = len(self.comments)
                if comments_after == comments_before:
                    break  # No new comments

                time.sleep(0.5)

                # Find next continuation - direct path approach
                next_continuation = None

                # Check onResponseReceivedEndpoints directly
                endpoints = api_data.get('onResponseReceivedEndpoints', [])
                for endpoint in endpoints:
                    if isinstance(endpoint, dict):
                        # Check for appendContinuationItemsAction
                        if 'appendContinuationItemsAction' in endpoint:
                            continuation_items = endpoint['appendContinuationItemsAction'].get('continuationItems', [])
                            if continuation_items and isinstance(continuation_items[-1], dict) and 'continuationItemRenderer' in continuation_items[-1]:
                                endpoint_obj = continuation_items[-1]['continuationItemRenderer'].get('continuationEndpoint', {})
                                command = endpoint_obj.get('continuationCommand', {})
                                token = command.get('token')
                                if token:
                                    next_continuation = token
                                    break
                        # Check for reloadContinuationItemsCommand
                        elif 'reloadContinuationItemsCommand' in endpoint:
                            cmd = endpoint['reloadContinuationItemsCommand']
                            if cmd.get('targetId') == 'engagement-panel-comments-section':
                                continuation_items = cmd.get('continuationItems', [])
                                for item in reversed(continuation_items):
                                    if isinstance(item, dict) and 'continuationItemRenderer' in item:
                                        endpoint_obj = item['continuationItemRenderer'].get('continuationEndpoint', {})
                                        command = endpoint_obj.get('continuationCommand', {})
                                        token = command.get('token')
                                        if token:
                                            next_continuation = token
                                            break
                current_continuation = next_continuation
                call_count += 1

    def get_comments(self, max_comments: Optional[int] = None) -> dict:
        """
        Get all available comments for the video, separated into top comments and regular comments.

        Args:
            max_comments (int, optional): Maximum number of comments to load. If None, loads all available.

        Returns:
            dict: Dictionary with 'top_comment' and 'comments' lists.
        """
        html = self.core.fetch_html()
        data = self.core.extract_ytinitialdata(html)
        self.extract_initial_comments(data)
        self.load_more_comments(data, max_comments)
        return {
            'top_comment': self.top_comments,
            'comments': self.comments
        }