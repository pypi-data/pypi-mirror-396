"""
NGTube Channel Module

This module provides functionality to extract channel metadata and videos from YouTube channels.
"""

import re
from typing import Union
from ..core import YouTubeCore
from .. import utils

class Channel:
    """
    Class to extract channel metadata and videos from a YouTube channel.

    Attributes:
        url (str): The YouTube channel URL.
        data (dict): The extracted channel data.
    """

    def __init__(self, url: str):
        """
        Initialize the Channel with a URL.

        Args:
            url (str): The YouTube channel URL.
        """
        self.url = url
        self.core = YouTubeCore(url)
        self.data = {}
        self.visitor_data = self.core.extract_visitor_data(self.core.fetch_html())

    def extract_profile(self, max_videos: Union[int, str] = 200) -> dict:
        """
        Extract channel profile data including metadata and videos.

        Args:
            max_videos (int | str): Maximum number of videos to load. Use 'all' to load all videos.
        """
        # API URL
        api_url = "https://www.youtube.com/youtubei/v1/browse"

        # Extract channel ID from URL
        channel_id = self._extract_channel_id()

        # Payload for Home Tab (to get profile data)
        payload_home = self._get_payload_home(channel_id)

        # Make API request for home tab
        try:
            data_home = self.core.make_api_request(api_url, payload_home)
            # Extract profile data from home response
            self._extract_profile_data(data_home)
        except Exception:
            # If home fails, try videos response for profile data
            pass

        # Payload for Videos Tab
        payload_videos = self._get_payload_videos(channel_id)

        # Make API request for videos
        try:
            data_videos = self.core.make_api_request(api_url, payload_videos)
        except Exception as e:
            raise Exception(f"Failed to fetch videos data: {e}")

        # Extract videos
        self._extract_videos(data_videos, max_videos)

        # If profile data not extracted from home, try from videos
        if not self.data.get('title'):
            self._extract_profile_data(data_videos)

        # Extract numbers
        self._extract_numbers()

        return self.data

    def extract_reels(self, max_reels: Union[int, str] = 200) -> list:
        """
        Extract channel reels/shorts.

        Args:
            max_reels (int | str): Maximum number of reels to load. Use 'all' to load all reels.
        """
        # API URL
        api_url = "https://www.youtube.com/youtubei/v1/browse"

        # Extract channel ID from URL
        channel_id = self._extract_channel_id()

        # Payload for Reels Tab
        payload_reels = self._get_payload_reels(channel_id)

        # Make API request for reels tab
        try:
            data_reels = self.core.make_api_request(api_url, payload_reels)
        except Exception as e:
            raise ValueError(f"Failed to fetch reels data: {e}")

        # Extract reels
        reels = self._extract_reels_data(data_reels, max_reels)
        return reels

    def extract_playlists(self, max_playlists: Union[int, str] = 200) -> list:
        """
        Extract channel playlists.

        Args:
            max_playlists (int | str): Maximum number of playlists to load. Use 'all' to load all playlists.
        """
        # API URL
        api_url = "https://www.youtube.com/youtubei/v1/browse"

        # Extract channel ID from URL
        channel_id = self._extract_channel_id()

        # Payload for Playlists Tab
        payload_playlists = self._get_payload_playlists(channel_id)

        # Make API request for playlists tab
        try:
            data_playlists = self.core.make_api_request(api_url, payload_playlists)
        except Exception as e:
            raise ValueError(f"Failed to fetch playlists data: {e}")

        # Extract playlists
        playlists = self._extract_playlists_data(data_playlists, max_playlists)
        return playlists

    def _extract_reels_data(self, data: dict, max_reels: Union[int, str]) -> list:
        """Extract reels data from API response."""
        reels = self._find_reels(data)
        if max_reels != 'all' and isinstance(max_reels, int):
            reels = reels[:max_reels]
        return reels

    def _extract_playlists_data(self, data: dict, max_playlists: Union[int, str]) -> list:
        """Extract playlists data from API response."""
        playlists = self._find_playlists(data)
        if max_playlists != 'all' and isinstance(max_playlists, int):
            playlists = playlists[:max_playlists]
        return playlists

    def _find_reels(self, obj):
        """Find reels in the data structure."""
        reels = []
        if isinstance(obj, dict):
            if 'richGridRenderer' in obj and 'contents' in obj['richGridRenderer']:
                for item in obj['richGridRenderer']['contents']:
                    if 'richItemRenderer' in item and 'content' in item['richItemRenderer']:
                        content = item['richItemRenderer']['content']
                        if 'shortsLockupViewModel' in content:
                            slvm = content['shortsLockupViewModel']
                            # Extract videoId from onTap.reelWatchEndpoint.videoId
                            video_id = None
                            if 'onTap' in slvm and 'innertubeCommand' in slvm['onTap'] and 'reelWatchEndpoint' in slvm['onTap']['innertubeCommand']:
                                video_id = slvm['onTap']['innertubeCommand']['reelWatchEndpoint'].get('videoId')
                            # Extract title from overlayMetadata.primaryText
                            overlay = slvm.get('overlayMetadata', {})
                            title = overlay.get('primaryText', {}).get('content', '')
                            # Extract viewCountText from overlayMetadata.secondaryText
                            view_count_text = overlay.get('secondaryText', {}).get('content', '')
                            # Extract viewCount as int
                            view_count = utils.extract_number(view_count_text) if view_count_text else 0
                            # Extract thumbnails from thumbnailViewModel
                            thumbnail_view = slvm.get('thumbnailViewModel', {}).get('thumbnailViewModel', {}).get('image', {}).get('sources', [])
                            reel = {
                                'videoId': video_id,
                                'title': title,
                                'viewCountText': view_count_text,
                                'viewCount': view_count,
                                'thumbnails': thumbnail_view
                            }
                            reels.append(reel)
            # Recurse
            for v in obj.values():
                reels.extend(self._find_reels(v))
        elif isinstance(obj, list):
            for item in obj:
                reels.extend(self._find_reels(item))
        return reels

    def _find_playlists(self, obj):
        """Find playlists in the data structure."""
        playlists = []
        if isinstance(obj, dict):
            if 'gridRenderer' in obj and 'items' in obj['gridRenderer']:
                for item in obj['gridRenderer']['items']:
                    if 'lockupViewModel' in item:
                        lvm = item['lockupViewModel']
                        # Extract playlistId from contentId
                        playlist_id = lvm.get('contentId', '')
                        # Extract title from metadata.lockupMetadataViewModel.title
                        title = lvm.get('metadata', {}).get('lockupMetadataViewModel', {}).get('title', {}).get('content', '')
                        # Extract thumbnails from contentImage.collectionThumbnailViewModel.primaryThumbnail.thumbnailViewModel.image.sources
                        thumbnails = lvm.get('contentImage', {}).get('collectionThumbnailViewModel', {}).get('primaryThumbnail', {}).get('thumbnailViewModel', {}).get('image', {}).get('sources', [])
                        # Extract videoCount from thumbnailOverlayBadgeViewModel.thumbnailBadges[0].text
                        video_count_text = ''
                        overlays = lvm.get('contentImage', {}).get('collectionThumbnailViewModel', {}).get('primaryThumbnail', {}).get('thumbnailViewModel', {}).get('overlays', [])
                        for overlay in overlays:
                            if 'thumbnailOverlayBadgeViewModel' in overlay:
                                badges = overlay['thumbnailOverlayBadgeViewModel'].get('thumbnailBadges', [])
                                if badges:
                                    video_count_text = badges[0].get('thumbnailBadgeViewModel', {}).get('text', '')
                                    break
                        # Extract videoCount as int
                        video_count = utils.extract_number(video_count_text) if video_count_text else 0
                        playlist = {
                            'playlistId': playlist_id,
                            'title': title,
                            'videoCountText': video_count_text,
                            'videoCount': video_count,
                            'thumbnails': thumbnails
                        }
                        playlists.append(playlist)
            # Recurse
            for v in obj.values():
                playlists.extend(self._find_playlists(v))
        elif isinstance(obj, list):
            for item in obj:
                playlists.extend(self._find_playlists(item))
        return playlists

    def _extract_channel_id(self) -> str:
        """Extract channel ID from URL by fetching the channel page."""
        if '/channel/' in self.url:
            # Direct channel ID in URL
            return self.url.split('/channel/')[1].split('/')[0].split('?')[0]
        
        if '@' in self.url:
            # For @handles, fetch the page to get the UC-ID
            try:
                html = self.core.fetch_html()
                # Try to find channel ID in the HTML
                # Pattern 1: browseId in ytInitialData (most reliable)
                match = re.search(r'"browseId"\s*:\s*"(UC[a-zA-Z0-9_-]+)"', html)
                if match:
                    return match.group(1)
                
                # Pattern 2: "channelId":"UC..."
                match = re.search(r'"channelId"\s*:\s*"(UC[a-zA-Z0-9_-]+)"', html)
                if match:
                    return match.group(1)
                
                # Pattern 3: "externalId":"UC..."
                match = re.search(r'"externalId"\s*:\s*"(UC[a-zA-Z0-9_-]+)"', html)
                if match:
                    return match.group(1)
                
                # Pattern 4: /channel/UC... in canonical URL
                match = re.search(r'/channel/(UC[a-zA-Z0-9_-]+)', html)
                if match:
                    return match.group(1)
                    
                raise ValueError("Could not find channel ID in page")
                
            except Exception as e:
                raise ValueError(f"Failed to extract channel ID: {e}")
        
        # For other formats, fetch the page to get the real channel ID
        try:
            html = self.core.fetch_html()
            
            # Try to find channel ID in the HTML
            # Pattern 1: browseId in ytInitialData (most reliable)
            match = re.search(r'"browseId"\s*:\s*"(UC[a-zA-Z0-9_-]+)"', html)
            if match:
                return match.group(1)
            
            # Pattern 2: "channelId":"UC..."
            match = re.search(r'"channelId"\s*:\s*"(UC[a-zA-Z0-9_-]+)"', html)
            if match:
                return match.group(1)
            
            # Pattern 3: "externalId":"UC..."
            match = re.search(r'"externalId"\s*:\s*"(UC[a-zA-Z0-9_-]+)"', html)
            if match:
                return match.group(1)
            
            # Pattern 4: /channel/UC... in canonical URL
            match = re.search(r'/channel/(UC[a-zA-Z0-9_-]+)', html)
            if match:
                return match.group(1)
                
            raise ValueError("Could not find channel ID in page")
            
        except Exception as e:
            raise ValueError(f"Failed to extract channel ID: {e}")

    def _get_payload_home(self, channel_id: str) -> dict:
        """Get payload for home tab."""
        return {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "WEB",
                    "clientVersion": "2.20251208.06.00",
                    "visitorData": self.visitor_data
                }
            },
            "browseId": channel_id
        }

    def _get_payload_videos(self, channel_id: str) -> dict:
        """Get payload for videos tab."""
        return {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "WEB",
                    "clientVersion": "2.20251208.06.00",
                    "visitorData": self.visitor_data
                }
            },
            "browseId": channel_id,
            "params": "EgZ2aWRlb3PyBgQKAjoA"
        }

    def _get_payload_reels(self, channel_id: str) -> dict:
        """Get payload for reels/shorts tab."""
        return {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "WEB",
                    "clientVersion": "2.20251208.06.00",
                    "visitorData": self.visitor_data
                }
            },
            "browseId": channel_id,
            "params": "EgZzaG9ydHPyBgUKA5oBAA%3D%3D"
        }

    def _get_payload_playlists(self, channel_id: str) -> dict:
        """Get payload for playlists tab."""
        return {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "clientName": "WEB",
                    "clientVersion": "2.20251208.06.00",
                    "visitorData": self.visitor_data
                }
            },
            "browseId": channel_id,
            "params": "EglwbGF5bGlzdHPyBgQKAkIA"
        }

    def _extract_profile_data(self, data: dict):
        """Extract profile data from API response."""
        def find_profile_data(obj):
            if isinstance(obj, dict):
                if 'channelMetadataRenderer' in obj:
                    cmr = obj['channelMetadataRenderer']
                    self.data['title'] = cmr.get('title', '')
                    self.data['description'] = cmr.get('description', '')
                    self.data['channelId'] = cmr.get('externalId', '')
                    self.data['channelUrl'] = cmr.get('channelUrl', '')
                    self.data['keywords'] = cmr.get('keywords', '')
                    self.data['isFamilySafe'] = cmr.get('isFamilySafe', False)
                    self.data['links'] = utils.extract_links(self.data.get('description', ''))
                    if 'avatar' in cmr and 'thumbnails' in cmr['avatar']:
                        self.data['avatar'] = cmr['avatar']['thumbnails']
                    return True
                if 'channelHeaderRenderer' in obj:
                    chr = obj['channelHeaderRenderer']
                    if 'subscriberCountText' in chr and 'simpleText' in chr['subscriberCountText']:
                        self.data['subscriberCountText'] = chr['subscriberCountText']['simpleText']
                    if 'videosCountText' in chr:
                        vct = chr['videosCountText']
                        if 'simpleText' in vct:
                            self.data['videoCountText'] = vct['simpleText']
                        elif 'runs' in vct and vct['runs']:
                            self.data['videoCountText'] = vct['runs'][0].get('text', '')
                    return True
                if 'c4TabbedHeaderRenderer' in obj:
                    c4thr = obj['c4TabbedHeaderRenderer']
                    if 'banner' in c4thr and 'imageBannerViewModel' in c4thr['banner']:
                        banner_vm = c4thr['banner']['imageBannerViewModel']
                        if 'image' in banner_vm and 'sources' in banner_vm['image']:
                            self.data['banner'] = banner_vm['image']['sources']
                    return True
                if 'pageHeaderViewModel' in obj:
                    phvm = obj['pageHeaderViewModel']
                    if 'banner' in phvm and 'imageBannerViewModel' in phvm['banner']:
                        banner_vm = phvm['banner']['imageBannerViewModel']
                        if 'image' in banner_vm and 'sources' in banner_vm['image']:
                            self.data['banner'] = banner_vm['image']['sources']
                    # Extract metadata from contentMetadataViewModel
                    if 'metadata' in phvm and 'contentMetadataViewModel' in phvm['metadata']:
                        cmvm = phvm['metadata']['contentMetadataViewModel']
                        if 'metadataRows' in cmvm and isinstance(cmvm['metadataRows'], list):
                            for row in cmvm['metadataRows']:
                                if 'metadataParts' in row and isinstance(row['metadataParts'], list):
                                    for part in row['metadataParts']:
                                        if 'text' in part and 'content' in part['text']:
                                            content = part['text']['content']
                                            if 'subscribers' in content.lower():
                                                self.data['subscriberCountText'] = content
                                            elif 'videos' in content.lower() or 'video' in content.lower():
                                                self.data['videoCountText'] = content
                    return True
                if 'videoCountText' in obj:
                    vct = obj['videoCountText']
                    if 'simpleText' in vct:
                        self.data['videoCountText'] = vct['simpleText']
                    elif 'runs' in vct and vct['runs']:
                        self.data['videoCountText'] = vct['runs'][0].get('text', '')
                if 'subscriberCountText' in obj and 'simpleText' in obj['subscriberCountText']:
                    self.data['subscriberCountText'] = obj['subscriberCountText']['simpleText']
                if 'viewCountText' in obj and 'simpleText' in obj['viewCountText']:
                    self.data['viewCountText'] = obj['viewCountText']['simpleText']
                if 'channelVideoPlayerRenderer' in obj:
                    cvpr = obj['channelVideoPlayerRenderer']
                    video = {
                        'videoId': cvpr.get('videoId'),
                        'title': cvpr.get('title', {}).get('runs', [{}])[0].get('text', ''),
                        'description': cvpr.get('description', {}).get('runs', [{}])[0].get('text', '')
                    }
                    self.data['featured_video'] = video
                # Also check for metadataRows for video count
                if 'metadataRows' in obj and isinstance(obj['metadataRows'], list):
                    for row in obj['metadataRows']:
                        if 'metadataParts' in row and isinstance(row['metadataParts'], list):
                            for part in row['metadataParts']:
                                if 'text' in part and 'content' in part['text']:
                                    content = part['text']['content']
                                    if 'Videos' in content:
                                        self.data['videoCountText'] = content
                for v in obj.values():
                    find_profile_data(v)
            elif isinstance(obj, list):
                for item in obj:
                    find_profile_data(item)

        find_profile_data(data)

    def _extract_videos(self, data: dict, max_videos: Union[int, str]):
        """Extract videos from API response with continuation."""
        api_url = "https://www.youtube.com/youtubei/v1/browse"
        data_videos_list = [data]
        loaded_videos = 0

        # Initial videos
        initial_videos = self._find_videos(data)
        loaded_videos += len(initial_videos)

        # Find continuation token
        continuation_token = self._find_continuation_token(data)

        # Load more videos
        while continuation_token and (max_videos == 'all' or (isinstance(max_videos, int) and loaded_videos < max_videos)):
            payload_continuation = {
                "context": {
                    "client": {
                        "hl": "en",
                        "gl": "US",
                        "clientName": "WEB",
                        "clientVersion": "2.20251208.06.00",
                        "visitorData": self.visitor_data
                    }
                },
                "continuation": continuation_token
            }

            try:
                data_cont = self.core.make_api_request(api_url, payload_continuation)
                data_videos_list.append(data_cont)
                new_videos = len(self._find_videos(data_cont))
                loaded_videos += new_videos
                if new_videos == 0:
                    break
                continuation_token = self._find_continuation_token(data_cont)
            except Exception:
                break

        # Collect all videos and deduplicate by videoId
        all_videos = []
        seen_video_ids = set()
        for data in data_videos_list:
            for video in self._find_videos(data):
                video_id = video.get('videoId')
                if video_id and video_id not in seen_video_ids:
                    seen_video_ids.add(video_id)
                    all_videos.append(video)
                elif not video_id:
                    all_videos.append(video)  # Keep videos without ID

        # Limit videos if max_videos is not 'all'
        if max_videos != 'all' and isinstance(max_videos, int):
            all_videos = all_videos[:max_videos]

        self.data['videos'] = all_videos
        self.data['loaded_videos_count'] = len(all_videos)

    def _find_videos(self, obj):
        """Find videos in the data structure."""
        videos = []
        if isinstance(obj, dict):
            # Initial videos - richGridRenderer (continuation)
            if 'richGridRenderer' in obj and 'contents' in obj['richGridRenderer']:
                for item in obj['richGridRenderer']['contents']:
                    if 'richItemRenderer' in item and 'content' in item['richItemRenderer']:
                        content = item['richItemRenderer']['content']
                        if 'videoRenderer' in content:
                            vr = content['videoRenderer']
                            video = {
                                'videoId': vr.get('videoId'),
                                'title': vr.get('title', {}).get('runs', [{}])[0].get('text', ''),
                                'publishedTimeText': vr.get('publishedTimeText', {}).get('simpleText', ''),
                                'viewCountText': vr.get('viewCountText', {}).get('simpleText', ''),
                                'lengthText': vr.get('lengthText', {}).get('simpleText', ''),
                                'thumbnails': vr.get('thumbnail', {}).get('thumbnails', [])
                            }
                            videos.append(video)
                        elif 'gridVideoRenderer' in content:
                            gvr = content['gridVideoRenderer']
                            video = {
                                'videoId': gvr.get('videoId'),
                                'title': gvr.get('title', {}).get('simpleText', ''),
                                'publishedTimeText': gvr.get('publishedTimeText', {}).get('simpleText', ''),
                                'viewCountText': gvr.get('viewCountText', {}).get('simpleText', ''),
                                'lengthText': gvr.get('thumbnailOverlays', [{}])[0].get('thumbnailOverlayTimeStatusRenderer', {}).get('text', {}).get('simpleText', ''),
                                'thumbnails': gvr.get('thumbnail', {}).get('thumbnails', [])
                            }
                            videos.append(video)
            # Initial videos - gridRenderer (first load)
            if 'gridRenderer' in obj and 'items' in obj['gridRenderer']:
                for item in obj['gridRenderer']['items']:
                    if 'gridVideoRenderer' in item:
                        gvr = item['gridVideoRenderer']
                        video = {
                            'videoId': gvr.get('videoId'),
                            'title': gvr.get('title', {}).get('simpleText', ''),
                            'publishedTimeText': gvr.get('publishedTimeText', {}).get('simpleText', ''),
                            'viewCountText': gvr.get('viewCountText', {}).get('simpleText', ''),
                            'lengthText': gvr.get('thumbnailOverlays', [{}])[0].get('thumbnailOverlayTimeStatusRenderer', {}).get('text', {}).get('simpleText', ''),
                            'thumbnails': gvr.get('thumbnail', {}).get('thumbnails', [])
                        }
                        videos.append(video)
            # Continuation videos
            if 'onResponseReceivedActions' in obj:
                for action in obj['onResponseReceivedActions']:
                    if 'appendContinuationItemsAction' in action:
                        for item in action['appendContinuationItemsAction']['continuationItems']:
                            if 'richItemRenderer' in item and 'content' in item['richItemRenderer']:
                                content = item['richItemRenderer']['content']
                                if 'videoRenderer' in content:
                                    vr = content['videoRenderer']
                                    video = {
                                        'videoId': vr.get('videoId'),
                                        'title': vr.get('title', {}).get('runs', [{}])[0].get('text', ''),
                                        'publishedTimeText': vr.get('publishedTimeText', {}).get('simpleText', ''),
                                        'viewCountText': vr.get('viewCountText', {}).get('simpleText', ''),
                                        'lengthText': vr.get('lengthText', {}).get('simpleText', ''),
                                        'thumbnails': vr.get('thumbnail', {}).get('thumbnails', [])
                                    }
                                    videos.append(video)
                                elif 'gridVideoRenderer' in content:
                                    gvr = content['gridVideoRenderer']
                                    video = {
                                        'videoId': gvr.get('videoId'),
                                        'title': gvr.get('title', {}).get('simpleText', ''),
                                        'publishedTimeText': gvr.get('publishedTimeText', {}).get('simpleText', ''),
                                        'viewCountText': gvr.get('viewCountText', {}).get('simpleText', ''),
                                        'lengthText': gvr.get('thumbnailOverlays', [{}])[0].get('thumbnailOverlayTimeStatusRenderer', {}).get('text', {}).get('simpleText', ''),
                                        'thumbnails': gvr.get('thumbnail', {}).get('thumbnails', [])
                                    }
                                    videos.append(video)
            for v in obj.values():
                videos.extend(self._find_videos(v))
        elif isinstance(obj, list):
            for item in obj:
                videos.extend(self._find_videos(item))
        return videos

    def _find_reels(self, obj):
        """Find reels in the data structure."""
        reels = []
        if isinstance(obj, dict):
            if 'richGridRenderer' in obj and 'contents' in obj['richGridRenderer']:
                for item in obj['richGridRenderer']['contents']:
                    if 'richItemRenderer' in item and 'content' in item['richItemRenderer']:
                        content = item['richItemRenderer']['content']
                        if 'shortsLockupViewModel' in content:
                            slvm = content['shortsLockupViewModel']
                            # Extract videoId from onTap.reelWatchEndpoint.videoId
                            video_id = None
                            if 'onTap' in slvm and 'innertubeCommand' in slvm['onTap'] and 'reelWatchEndpoint' in slvm['onTap']['innertubeCommand']:
                                video_id = slvm['onTap']['innertubeCommand']['reelWatchEndpoint'].get('videoId')
                            # Extract title from overlayMetadata.primaryText
                            overlay = slvm.get('overlayMetadata', {})
                            title = overlay.get('primaryText', {}).get('content', '')
                            # Extract viewCountText from overlayMetadata.secondaryText
                            view_count_text = overlay.get('secondaryText', {}).get('content', '')
                            reel = {
                                'videoId': video_id,
                                'title': title,
                                'viewCountText': view_count_text,
                                'viewCount': utils.extract_number(view_count_text),
                                'thumbnails': slvm.get('onTap', {}).get('innertubeCommand', {}).get('reelWatchEndpoint', {}).get('thumbnail', {}).get('thumbnails', [])
                            }
                            reels.append(reel)
            # Recurse
            for v in obj.values():
                reels.extend(self._find_reels(v))
        elif isinstance(obj, list):
            for item in obj:
                reels.extend(self._find_reels(item))
        return reels
    def _find_continuation_token(self, obj):
        """Find continuation token in the data structure."""
        if isinstance(obj, dict):
            # Initial structure
            if 'continuationItemRenderer' in obj:
                cir = obj['continuationItemRenderer']
                if 'continuationEndpoint' in cir:
                    endpoint = cir['continuationEndpoint']
                    if isinstance(endpoint, dict) and 'continuationCommand' in endpoint:
                        cmd = endpoint['continuationCommand']
                        if 'token' in cmd:
                            return cmd['token']
            # Continuation structure
            if 'onResponseReceivedActions' in obj:
                for action in obj['onResponseReceivedActions']:
                    if 'appendContinuationItemsAction' in action:
                        for item in action['appendContinuationItemsAction']['continuationItems']:
                            if 'continuationItemRenderer' in item:
                                cir = item['continuationItemRenderer']
                                if 'continuationEndpoint' in cir:
                                    endpoint = cir['continuationEndpoint']
                                    if isinstance(endpoint, dict) and 'continuationCommand' in endpoint:
                                        cmd = endpoint['continuationCommand']
                                        if 'token' in cmd:
                                            return cmd['token']
            for v in obj.values():
                token = self._find_continuation_token(v)
                if token:
                    return token
        elif isinstance(obj, list):
            for item in obj:
                token = self._find_continuation_token(item)
                if token:
                    return token
        return None

    def _extract_numbers(self):
        """Extract numerical values from text fields."""
        if 'subscriberCountText' in self.data:
            self.data['subscribers'] = utils.extract_number(self.data['subscriberCountText'])
        if 'viewCountText' in self.data:
            self.data['total_views'] = utils.extract_number(self.data['viewCountText'])
        if 'videoCountText' in self.data:
            self.data['video_count'] = utils.extract_number(self.data['videoCountText'])
