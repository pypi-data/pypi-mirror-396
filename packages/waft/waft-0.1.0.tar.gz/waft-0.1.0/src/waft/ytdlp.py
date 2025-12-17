"""YouTube download functionality using ``yt-dlp``.

This module provides asynchronous track downloading from YouTube URLs,
including audio extraction and metadata embedding.
"""

from os import makedirs
from pathlib import Path

from yt_dlp import YoutubeDL

from waft.datatypes import DisplayedTrack
from waft.metadata import write_metadata


async def download_track(
    url: str, destination: Path, data: DisplayedTrack, image_url: str
) -> None:
    """Download and process a track from YouTube with metadata embedding.

    Downloads audio from the specified YouTube URL, converts it to MP3 format,
    and embeds track metadata and album artwork.

    Parameters
    ----------
    url : str
        The YouTube URL to download audio from.
    destination : Path
        The file path where the MP3 should be saved (without extension).
    data : DisplayedTrack
        Track metadata to embed in the MP3 file.
    image_url : str
        URL to the album artwork to embed in the MP3 file.
    """

    # Set up ouput folder if it does not exist already.
    if not destination.parent.exists():
        makedirs(destination.parent)

    options = {
        "outtmpl": str(destination),
        "noprogress": True,
        "quiet": True,
        "format": "bestaudio/best",
        "concurrent_fragment_downloads": 32,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with YoutubeDL(options) as youtube_downloader:  # type: ignore
        youtube_downloader.download(url)

    write_metadata(destination, data, image_url)
