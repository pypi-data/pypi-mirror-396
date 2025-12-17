"""
Spotify Web API data models and request helpers.

This module provides typed container classes and helper functions for
interactingwith the Spotify Web API. It includes  higher-level
utilities for searching tracks and retrieving detailed metadata. Parsing
helpers convert raw Spotify API JSON into strongly typed Python objects
suitable for UI display or downstream processing.

Functions in this module perform network requests with appropriate
validation, raising informative exceptions for invalid parameters, network
issues, or non-successful HTTP responses. Actual error handling is left to
caller.

Notes
-----
All functions require a valid Spotify OAuth Bearer token. The user is
responsible for managing token expiration and refresh.
"""

from typing import Any, Dict, List

import requests
from requests.models import Response

from waft.datatypes import Album, Artist, DisplayedTrack, FullMetadata, Track


def parse_tracks_from_json(json_object: Dict[str, Any]) -> List[DisplayedTrack]:
    """
    Parse Spotify search JSON results into a list of `DisplayedTrack` objects.

    This function extracts relevant track metadata from a Spotify `/v1/search`
    API response and converts each track entry into a `DisplayedTrack`
    instance. It pulls the track name, primary artist (appending "and Others"
    when multiple artists are present), album name, duration in milliseconds,
    and track ID.

    Parameters
    ----------
    json_object : Dict[str, Any]
        Raw JSON returned from Spotify's Search API, expected to contain
        `json_object["tracks"]["items"]`, where each item is a track object.

    Returns
    -------
    List[DisplayedTrack]
        A list of parsed `DisplayedTrack` objects in the order they appear
        in the search results.

    Raises
    ------
    KeyError
        If the expected fields (`tracks`, `items`, or nested metadata fields)
        are missing from the input JSON.
    TypeError
        If the structure of the JSON object is not as expected or `json_object`
        is not a dictionary.
    """
    tracks_list: List[Dict[str, Any]] = json_object["tracks"]["items"]
    ordered_data_list: List[DisplayedTrack] = []
    for track_object in tracks_list:
        album: Dict[str, Any] = track_object["album"]
        album_name: str = album["name"]
        duration_ms: int = track_object["duration_ms"]
        track_name: str = track_object["name"]
        artists_list: List[Dict[str, Any]] = track_object["artists"]
        main_artist = artists_list[0]
        artist_name = main_artist["name"]
        track_id: str = track_object["id"]
        if len(artists_list) > 1:
            artist_name = artist_name + " and Others"
        ordered_data_tuple: DisplayedTrack = DisplayedTrack(
            track_name, artist_name, album_name, duration_ms, track_id
        )
        ordered_data_list.append(ordered_data_tuple)
    return ordered_data_list


def spotify_search(query: str, bearer: str, limit: int) -> List[DisplayedTrack]:
    """
    Perform a robust Spotify Search API request for tracks using a query.

    This function queries the Spotify Web API's `/v1/search` endpoint with
    a user-provided search query and returns raw JSON search results. It
    includes defensive input validation, HTTP error handling, and network
    exception handling to improve reliability.

    Parameters
    ----------
    query : str
        The track name (e.g., "Let it Be").
    bearer : str
        A valid OAuth Bearer token for the Spotify Web API.

    Returns
    -------
    Dict[str, Any]
        Raw JSON search results returned by the Spotify API.

    Raises
    ------
    ValueError
        If `query` or `bearer` is empty.
    requests.HTTPError
        If the Spotify API returns a non-200 response code.
    requests.RequestException
        For network-related exceptions such as timeouts or connection errors.

    Examples
    --------
    >>> token = "1POdFZRZbvb...qqillRxMr2z"
    >>> results = spotify_search("Doxy", token)
    >>> for item in results["tracks"]["items"]:
    ...     print(item["name"])
    Doxy
    """
    base_url: str = "https://api.spotify.com/v1/search"
    params: Dict[str, str] = {
        "q": f"track:{query}",  # NOTE: For not, this only searches tracks
        "type": "track",
        "limit": str(limit),
    }
    headers: Dict[str, str] = {"Authorization": f"Bearer {bearer}"}

    response: Response = requests.get(
        base_url, headers=headers, params=params, timeout=60
    )
    response.raise_for_status()  # raises error for non-200 responses

    tracks_list: List[DisplayedTrack] = parse_tracks_from_json(response.json())
    return tracks_list


def parse_album_data(response_json: Dict[str, Any]) -> Album:
    """
    Parse album metadata from a Spotify track JSON response.

    Extracts album-level fields—including album name and the URL of the first
    available album image—from the raw JSON returned by the Spotify track
    endpoint. This helper isolates album parsing logic for reuse within
    higher-level metadata construction.

    Parameters
    ----------
    response_json : Dict[str, Any]
        Full JSON response from the Spotify `/v1/tracks/{id}` endpoint.

    Returns
    -------
    Album
        A populated `Album` dataclass containing the album name and image URL.

    Raises
    ------
    KeyError
        If expected album fields are missing (e.g., `"album"`, `"images"`).
    """
    album: Dict[str, Any] = response_json["album"]
    album_name: str = album["name"]
    images = album["images"]
    first_image: Dict[str, Any] = images[0]
    image_url: str = first_image["url"]
    album_data: Album = Album(album_name, image_url)
    return album_data


def parse_artists_data(response_json: Dict[str, Any]) -> List[Artist]:
    """
    Parse contributing artist metadata from a Spotify track JSON response.

    Converts each artist entry in the raw Spotify track JSON into an `Artist`
    dataclass. This isolates artist parsing for clarity and reuse in structured
    metadata assembly.

    Parameters
    ----------
    response_json : Dict[str, Any]
        Full JSON response from the Spotify `/v1/tracks/{id}` endpoint.

    Returns
    -------
    List[Artist]
        A list of `Artist` objects representing all contributing artists.

    Raises
    ------
    KeyError
        If the `"artists"` field is missing from the response JSON.
    """
    artists = response_json["artists"]
    artists_data: List[Artist] = []
    for artist in artists:
        artist_data: Artist = Artist(artist["name"])
        artists_data.append(artist_data)
    return artists_data


def parse_track_data(response_json: Dict[str, Any]) -> Track:
    """
    Parse track-level metadata from a Spotify track JSON response.

    Extracts core fields describing the track itself—duration, explicit flag,
    title, release date, and track number—from the raw Spotify metadata.
    The release date is taken from the album object, as the track-level payload
    consolidates this data there.

    Parameters
    ----------
    response_json : Dict[str, Any]
        Full JSON response from the Spotify `/v1/tracks/{id}` endpoint.

    Returns
    -------
    Track
        A populated `Track` dataclass with detailed track metadata.

    Raises
    ------
    KeyError
        If required fields such as `"duration_ms"`, `"explicit"`, `"name"`,
        or `"album"` are missing.
    """
    duration_ms: int = response_json["duration_ms"]
    explicit: bool = response_json["explicit"]
    name: str = response_json["name"]
    album: Dict[str, Any] = response_json["album"]
    release_date: str = album["release_date"]  # NOTE: This is from Album.
    track_number: int = response_json["track_number"]
    track_data: Track = Track(duration_ms, explicit, name, release_date, track_number)
    return track_data


def get_metadata(track_id: str, bearer: str) -> FullMetadata:
    """
    Fetch metadata for a specific Spotify track using its track ID.

    This function sends a GET request to the Spotify Web API's track
    endpoint and returns the raw JSON metadata for the given track.
    It creates and sends the HTTP request and raises an exception if
    the HTTP status is invalid.

    Parameters
    ----------
    track_id : str
        The Spotify track ID to query (e.g., "11dFghCHEESElKmJXsNCbNl").
    bearer : str
        A valid OAuth Bearer token for the Spotify Web API.

    Returns
    -------
    FullMetadata
        Custom data type containing album, artist(s), and track data

    Raises
    ------
    ValueError
        If `track_id` or `bearer` is empty.
    requests.HTTPError
        If the Spotify API returns a non-200 status code.
    requests.RequestException
        For network-related errors.

    Examples
    --------
    >>> token = "1POdFZRZbvb...qqillRxMr2z"
    >>> data = get_metadata("random_id12345", token)
    >>> print(data["name"])
    "Pink Pony Club"
    """

    # Verify arguments are not empty
    if not track_id:
        raise ValueError("track_id cannot be empty.")
    if not bearer:
        raise ValueError("bearer token cannot be empty.")
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers: Dict[str, str] = {"Authorization": f"Bearer {bearer}"}

    # Send request and validate HTTP status of response
    response: Response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    response_json: Dict[str, Any] = response.json()

    # Parse data to extract relevant entities
    album_data: Album = parse_album_data(response_json)
    artists_data: List[Artist] = parse_artists_data(response_json)
    track_data: Track = parse_track_data(response_json)

    # Combine Data Types
    full_meta_data: FullMetadata = FullMetadata(album_data, artists_data, track_data)

    return full_meta_data
