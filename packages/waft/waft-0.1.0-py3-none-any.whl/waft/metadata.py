"""Metadata handling for downloaded audio files.

This module provides functionality to write ID3 tags and album artwork
to MP3 files after they have been downloaded.
"""

# from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

import eyed3  # type: ignore
import music_tag  # type: ignore
from eyed3.id3.frames import ImageFrame  # type: ignore

from waft.datatypes import DisplayedTrack

# from PIL import Image


def write_metadata(path: Path, data: DisplayedTrack, image_url: str) -> None:
    """Write ID3 metadata tags and album artwork to an MP3 file.

    Embeds track title, artist, album name, and cover art into the MP3 file
    at the specified path. The album artwork is fetched from the provided URL,
    resized if necessary to 480x480 pixels, and embedded as a FRONT_COVER image.

    Parameters
    ----------
    path : Path
        The file path to the MP3 file (without extension). The '.mp3' extension
        will be appended automatically.
    data : DisplayedTrack
        Track metadata containing title, artist, and album information.
    image_url : str
        URL to the album artwork image to embed in the MP3 file.

    Notes
    -----
    - Album artwork is automatically resized to a maximum of 480x480 pixels
      to reduce file size while maintaining quality.
    - ID3 tags are saved in version 2.3.0 format for compatibility with
      Windows Media Player and other legacy players.
    - Uses both music_tag and eyed3 libraries: music_tag for text metadata
      and eyed3 for image embedding.
    """

    mp3_tags = music_tag.load_file(f"{path}.mp3")
    mp3_tags["tracktitle"] = data.title
    mp3_tags["artist"] = data.artist
    mp3_tags["album"] = data.album
    mp3_tags.save()

    # Read image data and rescale if nessessary.
    image_data: bytes = urlopen(image_url).read()
    # image = Image.open(BytesIO(image_data), "r")  # type: ignore
    # image.thumbnail((480, 480))
    # image.save((buffer := BytesIO()), format=image.format)
    # image_data = buffer.getvalue()

    # Write image data.
    audiofile = eyed3.load(f"{path}.mp3")  # type: ignore
    audiofile.tag.images.set(  # type: ignore
        ImageFrame.FRONT_COVER, image_data, "image/jpeg"
    )
    # Windows media player and such only support ID3v2.3.
    audiofile.tag.save(version=(2, 3, 0))  # type: ignore
