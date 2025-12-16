"""
NGTube Shorts Module

This module provides functionality to extract shorts from YouTube.
"""

from ..core import YouTubeCore
from typing import Optional

class Shorts:
    """
    Class to fetch random shorts from YouTube homepage.

    Attributes:
        data (dict): The extracted short data.
    """

    def __init__(self, country: Optional[dict] = None):
        """
        Initialize the Shorts class.

        Args:
            country (dict): Country filter with 'hl' and 'gl' keys, use CountryFilters constants.
        """
        if country is None:
            from ..core import CountryFilters
            country = CountryFilters.US
        self.country = country
        self.core = YouTubeCore("https://www.youtube.com/shorts")
        self.data = {}
        self.endpoint = "https://www.youtube.com/youtubei/v1/reel/reel_item_watch"
        self.client_version = self.core.get_client_version("2.20251212.01.00")
        self.visitor_data = self.core.extract_visitor_data(self.core.fetch_html())

    def fetch_short(self) -> dict:
        """
        Fetch a random short from YouTube.

        Returns:
            dict: A dictionary containing short metadata.
        """
        payload = {
            "context": {
                "client": {
                    "hl": self.country["hl"],
                    "gl": self.country["gl"],
                    "visitorData": self.visitor_data,
                    "clientName": "WEB",
                    "clientVersion": self.client_version
                },
                "request": {
                    "useSsl": True,
                    "internalExperimentFlags": [],
                    "consistencyTokenJars": []
                }
            },
            "params": "CA8%3D",
            "inputType": "REEL_WATCH_INPUT_TYPE_SEEDLESS",
            "disablePlayerResponse": True
        }

        response = self.core.make_api_request(self.endpoint, payload)

        if response.get("status") == "REEL_ITEM_WATCH_STATUS_SUCCEEDED":
            self.data = self._parse_response(response)
        else:
            raise Exception("Failed to fetch short")

        return self.data

    def _parse_response(self, response: dict) -> dict:
        """
        Parse the API response to extract short metadata.

        Args:
            response (dict): The API response JSON.

        Returns:
            dict: Parsed short metadata.
        """
        data = {}

        overlay = response.get("overlay", {})
        short_overlay = overlay.get("reelPlayerOverlayRenderer", {})

        # Parse metadata items
        metapanel = short_overlay.get("metapanel", {})
        short_metapanel = metapanel.get("reelMetapanelViewModel", {})
        metadata_items = short_metapanel.get("metadataItems", [])

        for item in metadata_items:
            if "reelChannelBarViewModel" in item:
                channel_vm = item["reelChannelBarViewModel"]
                data["channel_name"] = channel_vm.get("channelName", {}).get("content", "")
                data["channel_handle"] = channel_vm.get("channelName", {}).get("content", "").replace("@", "")
                browse_endpoint = channel_vm.get("channelName", {}).get("commandRuns", [{}])[0].get("onTap", {}).get("innertubeCommand", {}).get("browseEndpoint", {})
                data["channel_id"] = browse_endpoint.get("browseId", "")
                data["channel_url"] = browse_endpoint.get("canonicalBaseUrl", "")

            elif "shortsVideoTitleViewModel" in item:
                title_vm = item["shortsVideoTitleViewModel"]
                data["title"] = title_vm.get("text", {}).get("content", "")

            elif "reelSoundMetadataViewModel" in item:
                sound_vm = item["reelSoundMetadataViewModel"]
                data["sound_metadata"] = sound_vm.get("soundMetadata", {}).get("content", "")

        # Parse button bar for likes and comments
        button_bar = short_overlay.get("buttonBar", {})
        short_action_bar = button_bar.get("reelActionBarViewModel", {})
        button_view_models = short_action_bar.get("buttonViewModels", [])

        for button_vm in button_view_models:
            if "likeButtonViewModel" in button_vm:
                like_vm = button_vm["likeButtonViewModel"]
                toggle_vm = like_vm.get("toggleButtonViewModel", {}).get("toggleButtonViewModel", {})
                default_vm = toggle_vm.get("defaultButtonViewModel", {}).get("buttonViewModel", {})
                title = default_vm.get("title", "")
                if title and title.replace(".", "").replace(",", "").isdigit():
                    data["like_count"] = self._parse_number(title)
                toggled_vm = toggle_vm.get("toggledButtonViewModel", {}).get("buttonViewModel", {})
                toggled_title = toggled_vm.get("title", "")
                if toggled_title and toggled_title.replace(".", "").replace(",", "").isdigit():
                    data["like_count"] = self._parse_number(toggled_title)

            elif "buttonViewModel" in button_vm:
                bvm = button_vm["buttonViewModel"]
                title = bvm.get("title", "")
                accessibility = bvm.get("accessibilityText", "")
                if "Kommentar" in accessibility or "comment" in accessibility.lower():
                    if title and title.isdigit():
                        data["comment_count"] = int(title)

        # Parse engagement panels for comments and description
        engagement_panels = response.get("engagementPanels", [])
        for panel in engagement_panels:
            if "engagementPanelSectionListRenderer" in panel:
                panel_renderer = panel["engagementPanelSectionListRenderer"]
                header = panel_renderer.get("header", {})
                title_header = header.get("engagementPanelTitleHeaderRenderer", {})
                title = title_header.get("title", {})
                runs = title.get("runs", [])
                if runs and ("Kommentar" in runs[0].get("text", "") or "Comments" in runs[0].get("text", "")):
                    contextual_info = title_header.get("contextualInfo", {})
                    info_runs = contextual_info.get("runs", [])
                    if info_runs:
                        comment_count_text = info_runs[0].get("text", "")
                        if comment_count_text.isdigit():
                            data["comment_count"] = int(comment_count_text)

                    # Extract continuation token for comments
                    content = panel_renderer.get("content", {})
                    section_list = content.get("sectionListRenderer", {})
                    contents = section_list.get("contents", [])
                    for content_item in contents:
                        if "itemSectionRenderer" in content_item:
                            item_section = content_item["itemSectionRenderer"]
                            item_contents = item_section.get("contents", [])
                            for item in item_contents:
                                if "continuationItemRenderer" in item:
                                    continuation_renderer = item["continuationItemRenderer"]
                                    continuation_endpoint = continuation_renderer.get("continuationEndpoint", {})
                                    continuation_command = continuation_endpoint.get("continuationCommand", {})
                                    data["comments_continuation"] = continuation_command.get("token", "")

                if "structuredDescriptionContentRenderer" in panel_renderer.get("content", {}):
                    content = panel_renderer.get("content", {})
                    desc_renderer = content["structuredDescriptionContentRenderer"]
                    items = desc_renderer.get("items", [])
                    for item in items:
                        if "videoDescriptionHeaderRenderer" in item:
                            header_renderer = item["videoDescriptionHeaderRenderer"]
                            title_runs = header_renderer.get("title", {}).get("runs", [])
                            if title_runs:
                                data["title"] = title_runs[0].get("text", "")

                            channel = header_renderer.get("channel", {}).get("simpleText", "")
                            if channel:
                                data["channel_name"] = channel

                            views = header_renderer.get("views", {}).get("simpleText", "")
                            if views:
                                data["view_count"] = self._parse_number(views.split()[0])

                            publish_date = header_renderer.get("publishDate", {}).get("simpleText", "")
                            if publish_date:
                                data["publish_date"] = publish_date

                            factoids = header_renderer.get("factoid", [])
                            for factoid in factoids:
                                if "factoidRenderer" in factoid:
                                    fr = factoid["factoidRenderer"]
                                    label = fr.get("label", {}).get("simpleText", "")
                                    value = fr.get("value", {}).get("simpleText", "")
                                    if "Like" in label:
                                        data["like_count"] = self._parse_number(value)
                                    elif "Aufruf" in label:
                                        data["view_count"] = self._parse_number(value)
                                elif "viewCountFactoidRenderer" in factoid:
                                    vcfr = factoid["viewCountFactoidRenderer"]
                                    fr = vcfr.get("factoid", {}).get("factoidRenderer", {})
                                    value = fr.get("value", {}).get("simpleText", "")
                                    if value:
                                        data["view_count"] = self._parse_number(value)

        # Additional data from replacementEndpoint
        replacement = response.get("replacementEndpoint", {}).get("reelWatchEndpoint", {})
        if replacement:
            data["video_id"] = replacement.get("videoId", data.get("video_id", ""))
            data["thumbnail"] = replacement.get("thumbnail", {}).get("thumbnails", data.get("thumbnail", []))

        data["sequence_continuation"] = response.get("sequenceContinuation", "")

        return data

    def fetch_shorts_feed(self, max_shorts: int = 50) -> list:
        """
        Fetch multiple shorts from the YouTube Shorts feed.

        Args:
            max_shorts (int): Maximum number of shorts to fetch.

        Returns:
            list: A list of dictionaries containing short metadata (basic info only for performance).
        """
        shorts_list = []
        
        # Get initial sequence continuation from Shorts page
        html = self.core.fetch_html()
        yt_initial_data = self.core.extract_ytinitialdata(html)
        sequence_continuation = yt_initial_data.get('sequenceContinuation', '')
        
        if not sequence_continuation:
            raise Exception("Could not find sequence continuation for Shorts feed")
        
        endpoint = "https://www.youtube.com/youtubei/v1/reel/reel_watch_sequence"
        
        while len(shorts_list) < max_shorts and sequence_continuation:
            payload = {
                "context": {
                    "client": {
                        "hl": self.country["hl"],
                        "gl": self.country["gl"],
                        "visitorData": self.visitor_data,
                        "clientName": "WEB",
                        "clientVersion": self.client_version,
                        "osName": "Windows",
                        "osVersion": "10.0",
                        "platform": "DESKTOP"
                    },
                    "request": {
                        "useSsl": True
                    }
                },
                "sequenceParams": sequence_continuation
            }
            
            response = self.core.make_api_request(endpoint, payload)
            
            # Parse entries
            entries = response.get('entries', [])
            for entry in entries:
                if len(shorts_list) >= max_shorts:
                    break
                if 'command' in entry:
                    command = entry['command']
                    if 'reelWatchEndpoint' in command:
                        endpoint_data = command['reelWatchEndpoint']
                        video_id = endpoint_data.get('videoId')
                        if video_id:
                            # Create basic short data
                            short_data = {
                                'video_id': video_id,
                                'title': endpoint_data.get('overlay', {}).get('reelPlayerOverlayRenderer', {}).get('reelPlayerHeaderSupportedRenderers', {}).get('reelPlayerHeaderRenderer', {}).get('reelTitleText', {}).get('simpleText', ''),
                                'channel_name': endpoint_data.get('overlay', {}).get('reelPlayerOverlayRenderer', {}).get('reelPlayerHeaderSupportedRenderers', {}).get('reelPlayerHeaderRenderer', {}).get('channelTitleText', {}).get('simpleText', ''),
                                'thumbnail': endpoint_data.get('thumbnail', {}).get('thumbnails', [])
                            }
                            shorts_list.append(short_data)
            
            # Get next continuation
            continuation_endpoint = response.get('continuationEndpoint', {})
            if continuation_endpoint:
                continuation_command = continuation_endpoint.get('continuationCommand', {})
                sequence_continuation = continuation_command.get('token', '')
            else:
                sequence_continuation = ''
        
        return shorts_list

    def _parse_number(self, text: str) -> int:
        """
        Parse a number string with potential suffixes like 'Mio.', 'K', etc.

        Args:
            text (str): The text to parse.

        Returns:
            int: The parsed number.
        """
        text = text.replace(".", "").replace(",", "").strip()
        if "Mio" in text or "M" in text:
            return int(float(text.replace("Mio", "").replace("M", "")) * 1000000)
        elif "K" in text:
            return int(float(text.replace("K", "")) * 1000)
        else:
            return int(text) if text.isdigit() else 0