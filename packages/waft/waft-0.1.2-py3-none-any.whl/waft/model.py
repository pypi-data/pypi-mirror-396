"""T.E.A. model and the corresponding update logic for `waft` application.

Notes
-----
- All state transitions must be pure and must return a new model instance
  rather than mutating an existing one.
"""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Tuple

from textual.message import Message

from waft.datatypes import DisplayedTrack, YoutubeResult
from waft.messages import Authenticating, SearchRequest, UpdateStatus


@dataclass(frozen=True)
class ApplicationModel:  # pylint: disable=too-many-instance-attributes
    """An immutable struct-like representation of the state of the application.

    Attributes
    ----------
    active_token: str
        The currently active Spotify access token obtained during
        authentication. An empty string indicates that no token has been
        acquired or verified yet.
    authenticating : bool
        Whether the application is currently performing an authentication
        workflow. Used to disable inputs, show spinners, and block
        additional submissions.
    search_query : (str, str)
        TODO
    status_message : str
        Text to display in the global status bar.
    valid_credentials: bool
        Whether the application has confirmed that stored or newly provided
        credentials are valid for making Spotify API requests.
    """

    active_token: str
    api_key: str
    authenticating: bool
    developer_key: str
    downloads_folder: Path
    search_query: Tuple[str, str]
    search_results: List[DisplayedTrack]
    selection: DisplayedTrack
    suggestion_results: List[YoutubeResult]
    status_message: str
    valid_credentials: bool


def update(model: ApplicationModel, message: Message) -> ApplicationModel:
    """Apply a TEA state transition to the application model.

    This pure function receives the current model and a Textual message,
    and returns a new model reflecting the appropriate state changes.

    Parameters
    ----------
    model : ApplicationModel
        The current immutable state of the application.
    message : Message
        A Textual message indicating the type of state transition to
        perform.

    Returns
    -------
    ApplicationModel
        A new model instance with the applied state modifications.
    """

    match message:
        case UpdateStatus(text=text):
            return replace(model, status_message=text)
        case Authenticating(state=state):
            return replace(model, authenticating=state)
        case SearchRequest(query=query, mode=mode):
            return replace(model, search_query=(query, mode))
        case _:
            return model
