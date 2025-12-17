"""YouTube search functionality for finding audio sources.

This module provides functions to search YouTube for videos matching
Spotify track metadata and parse the results into usable data structures.
"""

from typing import Any, Dict, List

import googleapiclient.discovery  # type: ignore

from waft.datatypes import DisplayedTrack, YoutubeResult


def parse_results_from_json(json_object: Dict[str, Any]) -> List[YoutubeResult]:
    """Parse YouTube API response JSON into YoutubeResult objects.

    Extracts video title, channel name, and URL from the YouTube API
    search response, filtering out non-video results.

    Parameters
    ----------
    json_object : Dict[str, Any]
        The JSON response dictionary from the YouTube Data API search endpoint.

    Returns
    -------
    List[YoutubeResult]
        List of parsed YouTube video results containing title, channel, and URL.
    """

    results = []

    for item in json_object["items"]:
        if item["id"]["kind"] != "youtube#video":
            continue

        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        url = "https://www.youtube.com/watch?v=" + item["id"]["videoId"]
        results.append(YoutubeResult(title, channel, url))

    return results


def search_youtube(search_info: DisplayedTrack, api_key: str) -> List[YoutubeResult]:
    """Search YouTube for videos matching the given track metadata.

    Constructs a search query from track title, artist, and album information,
    then queries the YouTube Data API to find matching videos.

    Parameters
    ----------
    search_info : DisplayedTrack
        Track metadata to use for constructing the search query.
    api_key : str
        YouTube Data API key for authentication.

    Returns
    -------
    List[YoutubeResult]
        List of YouTube video results matching the search criteria.
    """

    developer_key: str = api_key
    title = search_info.title
    artist = search_info.artist
    album = search_info.album
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=developer_key
    )
    request = youtube.search().list(  # pylint: disable=no-member
        part="snippet", maxResults=25, q=f"{title} {artist} {album}"
    )
    response = request.execute()
    return parse_results_from_json(response)
