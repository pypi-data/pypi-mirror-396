"""
NGTube Core Module

This module provides the core functionality for interacting with YouTube.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import demjson3 as demjson

class YouTubeCore:
    """
    Core class for YouTube data extraction.

    Attributes:
        url (str): The YouTube URL.
        headers (dict): HTTP headers for requests.
    """

    def __init__(self, url: str):
        """
        Initialize the YouTubeCore with a URL.

        Args:
            url (str): The YouTube URL.
        """
        self.url = url
        self._cached_html = None
        self._client_version = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        # Cookies to bypass EU consent screen
        self.cookies = {
            'CONSENT': 'PENDING+987',
            'SOCS': 'CAISHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmRlIAEaBgiAo_CmBg'
        }
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        """Create a requests session with basic retry and shared headers/cookies."""
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
        session.cookies.update(self.cookies)
        return session

    def fetch_html(self) -> str:
        """
        Fetch the HTML content from the YouTube URL.

        Returns:
            str: The HTML content.
        """
        if self._cached_html:
            return self._cached_html

        response = self.session.get(self.url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch HTML: {response.status_code}")

        self._cached_html = response.text
        return self._cached_html

    def extract_ytinitialdata(self, html: str) -> dict:
        """
        Extract ytInitialData from HTML.

        Args:
            html (str): The HTML content.

        Returns:
            dict: The ytInitialData JSON.
        """
        start_pattern = r'var ytInitialData\s*=\s*\{'
        start_match = re.search(start_pattern, html)

        if start_match:
            start_index = start_match.end() - 1
            brace_count = 0
            in_string = False
            escape_next = False
            end_index = start_index

            for i in range(start_index, len(html)):
                char = html[i]
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not in_string:
                    in_string = True
                elif char == '"' and in_string:
                    in_string = False
                elif not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_index = i
                            break

            json_str = html[start_index:end_index + 1]
            try:
                result = demjson.decode(json_str)
                if isinstance(result, dict):
                    return result
                else:
                    raise Exception("Parsed data is not a dictionary")
            except Exception as e:
                raise Exception(f"Failed to parse ytInitialData: {e}")
        else:
            raise Exception("ytInitialData not found in HTML")

    def extract_ytinitialplayerresponse(self, html: str) -> dict:
        """
        Extract ytInitialPlayerResponse from HTML.

        Args:
            html (str): The HTML content.

        Returns:
            dict: The ytInitialPlayerResponse JSON.
        """
        start_pattern = r'var ytInitialPlayerResponse\s*=\s*\{'
        start_match = re.search(start_pattern, html)

        if start_match:
            start_index = start_match.end() - 1
            brace_count = 0
            in_string = False
            escape_next = False
            end_index = start_index

            for i in range(start_index, len(html)):
                char = html[i]
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not in_string:
                    in_string = True
                elif char == '"' and in_string:
                    in_string = False
                elif not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_index = i
                            break

            json_str = html[start_index:end_index + 1]
            try:
                result = demjson.decode(json_str)
                if isinstance(result, dict):
                    return result
                else:
                    raise Exception("Parsed data is not a dictionary")
            except Exception as e:
                raise Exception(f"Failed to parse ytInitialPlayerResponse: {e}")
        else:
            raise Exception("ytInitialPlayerResponse not found in HTML")

    def extract_visitor_data(self, html: str) -> str:
        """
        Extract visitorData from HTML.

        Args:
            html (str): The HTML content.

        Returns:
            str: The visitorData string.
        """
        try:
            yt_initial_data = self.extract_ytinitialdata(html)
            def find_visitor_data(obj):
                if isinstance(obj, dict):
                    if 'responseContext' in obj and 'visitorData' in obj['responseContext']:
                        return obj['responseContext']['visitorData']
                    for v in obj.values():
                        result = find_visitor_data(v)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_visitor_data(item)
                        if result:
                            return result
                return None
            visitor_data = find_visitor_data(yt_initial_data)
            return visitor_data or ""
        except:
            return ""

    def make_api_request(self, endpoint: str, payload: dict) -> dict:
        """
        Make a POST request to YouTube's internal API.

        Args:
            endpoint (str): The API endpoint.
            payload (dict): The request payload.

        Returns:
            dict: The API response JSON.
        """
        response = self.session.post(endpoint, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code}")

    def get_client_version(self, fallback: str = "2.20251208.06.00") -> str:
        """
        Extract clientVersion from the page HTML, with optional fallback.
        """
        if self._client_version:
            return self._client_version
        try:
            html = self.fetch_html()
            match = re.search(r'"clientVersion"\s*:\s*"([^"]+)"', html)
            if match:
                self._client_version = match.group(1)
                return self._client_version
        except Exception:
            pass
        return fallback
