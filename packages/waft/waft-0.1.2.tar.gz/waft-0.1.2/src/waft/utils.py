"""Utility functions for formatting and U.I. conversion.

This module provides helper functions for converting data structures into
Textual U.I. components and formatting time values for display.
"""

from datetime import timedelta
from typing import List

from rich.table import Table
from textual.widgets.option_list import Option

from waft.datatypes import YoutubeResult
from waft.spotify import DisplayedTrack


def format_milliseconds(milliseconds: int) -> str:
    """Convert milliseconds to a human-readable time string.

    Formats the duration in HH:MM:SS format if the duration is an hour or longer,
    otherwise formats as MM:SS.

    Parameters
    ----------
    milliseconds : int
        The duration in milliseconds to format.

    Returns
    -------
    str
        Formatted time string in either "H:MM:SS" or "M:SS" format.
    """

    total_seconds: int = int(timedelta(milliseconds=milliseconds).total_seconds())
    hours: int = total_seconds // 3600
    minutes: int = (total_seconds % 3600) // 60
    seconds: int = total_seconds % 60

    return (
        f"{hours:d}:{minutes:02d}:{seconds:02d}"
        if total_seconds >= 3600
        else f"{minutes:d}:{seconds:02d}"
    )


def create_options_from_results(results_list: List[DisplayedTrack]) -> List[Option]:
    """Convert Spotify search results into Textual Option widgets.

    Creates formatted table layouts for each track result, displaying title,
    artist, album, and duration in a structured grid format.

    Parameters
    ----------
    results_list : List[DisplayedTrack]
        List of track metadata objects from Spotify search results.

    Returns
    -------
    List[Option]
        List of Textual Option objects ready to be added to an OptionList widget.
    """

    options: List[Option] = []

    result: DisplayedTrack
    for result in results_list:
        table: Table = Table.grid(expand=True)

        # NOTE: Changing the ratios is a guess and check, so have fun changing it...
        table.add_column(
            "Title", justify="left", ratio=90, no_wrap=True, overflow="ellipsis"
        )
        table.add_column(
            "Album", justify="left", ratio=160, no_wrap=True, overflow="ellipsis"
        )
        table.add_column(
            "Duration", justify="right", ratio=50, no_wrap=True, overflow="ellipsis"
        )
        table.add_row(
            f"[b]{result.title}[/b]",
            f"{result.album}",
            f"{format_milliseconds(int(result.duration))}",
        )
        table.add_row(f"{result.artist}")

        options.append(Option(table))

    return options


def create_options_from_suggestions(suggestions: List[YoutubeResult]) -> List[Option]:
    """Convert YouTube search results into Textual Option widgets.

    Creates formatted table layouts for each YouTube suggestion, displaying
    video title, channel name, and URL in a structured grid format.

    Parameters
    ----------
    suggestions : List[YoutubeResult]
        List of YouTube video metadata objects from search results.

    Returns
    -------
    List[Option]
        List of Textual Option objects ready to be added to an OptionList widget.
    """

    options: List[Option] = []
    suggestion: YoutubeResult
    for suggestion in suggestions:
        table: Table = Table.grid(expand=True)

        table.add_column(
            "Title", justify="left", ratio=30, no_wrap=True, overflow="ellipsis"
        )
        table.add_column(
            "Channel", justify="left", ratio=20, no_wrap=True, overflow="ellipsis"
        )
        table.add_column(
            "Url", justify="right", ratio=50, no_wrap=True, overflow="ellipsis"
        )
        table.add_row(
            f"{suggestion.video_title}",
            f"{suggestion.channel}",
            f"{suggestion.url}",
        )

        options.append(Option(table))

    return options
