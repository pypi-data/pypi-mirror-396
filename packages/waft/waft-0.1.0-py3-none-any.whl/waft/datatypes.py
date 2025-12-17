"""
Spotify metadata domain models.

This module defines a collection of lightweight dataclass-based containers
representing structured Spotify metadata returned from the Web API. These
classes are used throughout the application to encapsulate album details,
artist information, track metadata, and combined representations for display
or downstream processing.

Classes
-------
Album
    Basic album information including album name and cover image URL.
Artist
    Represents a single contributing artist with a display name.
Track
    Detailed track-level metadata such as duration, explicit flag,
    release date, and track ordering.
FullMetadata
    Bundled container holding the complete metadata set: album, artists,
    and track details.
DisplayedTrack
    Simplified, user-facing version of track metadata intended for
    UI display and search result presentation.

Notes
-----
Although these classes are marked with ``@dataclass``, explicit ``__init__``
methods are provided to maintain control over initialization behavior
and future extensibility. Instances of these models should be considered
immutable once created and used purely as data containers.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Album:
    """
    Album container.

    Represents basic album information returned from Spotify.

    Attributes
    ----------
    album_name : str
        The name of the album.
    image_url : str
        URL linking to the Spotify album cover image.
    """

    album_name: str
    image_url: str

    def __init__(self, album_name, image_url):
        self.album_name = album_name
        self.image_url = image_url


@dataclass
class Artist:
    """
    Artist container.

    Represents a single contributing artist.

    Attributes
    ----------
    artist_name : str
        The artist's display name.
    """

    artist_name: str

    def __init__(self, artist_name):
        self.artist_name = artist_name


@dataclass
class Track:
    """
    Track metadata.

    Stores detailed track-level fields such as duration, explicit flag,
    release date, and ordering within the album.

    Attributes
    ----------
    duration_ms : int
        Duration of the track in milliseconds.
    explicit : bool
        Whether the track is marked explicit.
    name : str
        Track title.
    release_date : str
        The track's release date (ISO string).
    track_number : int
        Track's position within the album.
    """

    duration_ms: int
    explicit: bool
    name: str
    release_date: str
    track_number: int

    def __init__(self, duration_ms, explicit, name, release_date, track_number):
        self.duration_ms = duration_ms
        self.explicit = explicit
        self.name = name
        self.release_date = release_date
        self.track_number = track_number


@dataclass
class FullMetadata:
    """
    Full track metadata wrapper.

    Bundles album info, artist list, and detailed track fields into
    a unified container.

    Attributes
    ----------
    album : Album
        Album metadata object.
    artists : List[Artist]
        List of contributing artists.
    track : Track
        Track-level metadata object.
    """

    album: Album
    artists: List[Artist]
    track: Track

    def __init__(self, album, artists, track):
        self.album = album
        self.artists = artists
        self.track = track


@dataclass
class DisplayedTrack:
    """
    Container for displaying simplified Spotify track metadata.

    This dataclass stores a compact, user-facing representation of a Spotify
    track, including its title, primary artist, album name, duration, and
    track ID. It is primarily used after parsing search results or metadata
    responses to prepare structured data for UI display when a user
    selects their desired track.

    Attributes
    ----------
    title : str
        The track title as shown on Spotify.
    artist : str
        The primary artist's name. May include "and Others" if
        multiple artists contributed to the track.
    album : str
        The album name from which the track originates.
    duration : str
        The track's duration, typically expressed in milliseconds.
    track_id : str
        The unique Spotify track identifier.
    """

    title: str
    artist: str
    album: str
    duration: str
    track_id: str

    def __init__(self, title, artist, album, duration, track_id):
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.track_id = track_id


@dataclass
class YoutubeResult:
    """Represents a single YouTube video search result.

    Stores metadata for a YouTube video that may serve as an audio
    source for downloading.

    Attributes
    ----------
    video_title : str
        The title of the YouTube video.
    channel : str
        The name of the YouTube channel that uploaded the video.
    url : str
        The full URL to the YouTube video.
    """

    video_title: str
    channel: str
    url: str

    def __init__(self, video_title: str, channel: str, url: str):
        self.video_title = video_title
        self.channel = channel
        self.url = url
