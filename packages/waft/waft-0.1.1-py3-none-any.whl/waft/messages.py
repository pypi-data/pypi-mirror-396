"""Message definitions for the `waft` application's T.E.A. event flow.

This module defines custom Textual message subclasses used to communicate
state changes to the application's update loop.

Messages
--------
Authenticating
    Indicates that an authentication workflow has started or ended.
UpdateStatus
    Carries text for updating the application's status display.
"""

from textual.message import Message


class Authenticating(Message):
    """Message indicating a change to the authentication workflow state.

    This message is emitted when the application begins or ends an
    authentication sequence. Used to disable ::Input:: fields and thwart
    duplicate successive authentication requests.
    """

    def __init__(self, state: bool) -> None:
        """
        Construct an authentication message.

        Parameters
        ----------
        state : bool
            Whether authentication is currently active.
        """

        super().__init__()
        self.state = state


class UpdateStatus(Message):
    """Message containing updated status text for the application.

    This message is dispatched when a screen or widget needs to update the
    text displayed in the global status bar. It carries the new message
    content, leaving rendering and model updates to the application controller.
    """

    def __init__(self, text: str) -> None:
        """Construct a status update message.

        Parameters
        ----------
        text : str
            The status text to present to the user.
        """

        super().__init__()
        self.text = text


class ValidCredentials(Message):
    """Message indicating that provided credentials have passed validation.

    This message is dispatched when the user's submitted credentials are determined to
    be valid, allowing the program to proceed to the Spotify A.P.I. search menu.

    Notes
    -----
    - Calling ``super().__init__()`` is required so that Textual correctly
      handles this as a message.
    """

    def __init__(self) -> None:  # pylint: disable=useless-parent-delegation
        """Construct a credential validation message.

        Notes
        -----
        Calling ``super().__init__()`` is required so that Textual correctly
        handles this as a message.
        """
        super().__init__()


class SearchRequest(Message):
    """Message requesting a Spotify search operation.

    This message is dispatched when the user submits a search query. It contains
    both the search string and the search mode (e.g., track, album, artist) to
    determine how the Spotify A.P.I. should interpret the query.
    """

    def __init__(self, query: str, mode: str) -> None:
        """Construct a search request message.

        Parameters
        ----------
        query : str
            The user's search query string to send to the Spotify A.P.I.
        mode : str
            The search mode specifying what to search for (e.g., 'track', 'album',
            'artist').
        """

        super().__init__()
        self.query = query
        self.mode = mode


class TrackSelected(Message):
    """Message indicating a track has been selected from search results.

    This message is dispatched when the user selects a track from the Spotify
    search results. It contains the index of the selected track, which is used
    to retrieve the full track details from the cached search results.
    """

    def __init__(self, index: int) -> None:
        """Construct a U.R.L. selection message.

        Parameters
        ----------
        index : int
            The zero-based index of the selected YouTube result in the suggestions list.
        """

        super().__init__()
        self.index = index


class UrlSelected(Message):
    """Message indicating a YouTube U.R.L. has been selected from suggestions.

    This message is dispatched when the user selects a YouTube video from the
    list of audio source suggestions. It contains the index of the selected U.R.L.,
    which is used to initiate the download process.
    """

    def __init__(self, index: int) -> None:
        """Construct a URL selection message.

        Parameters
        ----------
        index : int
            The zero-based index of the selected YouTube result in the suggestions list.
        """

        super().__init__()
        self.index = index


class StartDownload(Message):
    """Message triggering the download process for a selected track.

    This message is dispatched when the user confirms their audio source selection
    and wants to begin downloading. It contains the YouTube U.R.L. to download from,
    along with track metadata for tagging.
    """

    def __init__(self, url: str) -> None:
        """Construct a status update message.

        Parameters
        ----------
        url : str
            The YouTube URL to download audio from.
        """

        super().__init__()
        self.url = url
