"""Core application module for the `waft` Textual interface.

This module defines the top-level :class:`Application` class, which manages
The Elm Architecture model and coordinates user interface updates in
response to Textual events.
"""

from dataclasses import replace
from pathlib import Path
from typing import List, Optional, Tuple

from textual.app import App
from textual.css.query import NoMatches

from waft.authentication import get_spotify_access_token
from waft.datatypes import DisplayedTrack
from waft.keyring import retrieve_credentials
from waft.messages import (Authenticating, SearchRequest, StartDownload,
                      TrackSelected, UpdateStatus, UrlSelected)
from waft.model import ApplicationModel, update
from waft.screens import (AudioSource, IntitialAuthenticationScreen,
                     SpotifySearchScreen)
from waft.spotify import get_metadata, spotify_search
from waft.utils import create_options_from_results, create_options_from_suggestions
from waft.widgets import DownloadOption, StatusBar
from waft.youtube import search_youtube
from waft.ytdlp import download_track


class Application(App):
    """Manages/Updates the application state based on Textual events.

    All ::Messages:: have corresponding handlers as member functions of this
    class, as it loops.
    """

    ALLOW_SELECT = False
    CSS_PATH = "../../styles/main.tcss"

    def __init__(self) -> None:
        """Initialize the model state with default values on startup."""

        super().__init__()

        self.model: ApplicationModel = ApplicationModel(
            active_token="",
            api_key="",
            authenticating=False,
            downloads_folder=Path.home() / "Music/waft/",
            developer_key="",
            search_query=("", ""),
            search_results=[],
            selection=DisplayedTrack("", "", "", "", ""),
            suggestion_results=[],
            status_message="...",
            valid_credentials=False,
        )

    async def on_mount(self) -> None:
        """Initialize application state and load the initial screen.

        This method is called once when the Textual application finishes
        mounting. It initializes the T.E.A. model.
        """

        credential_result: Optional[Tuple[str, str, str]] = retrieve_credentials()

        authentication_result: Optional[str] = None
        token: str = ""

        if credential_result is not None:
            authentication_result = self.run_worker(
                get_spotify_access_token(credential_result[0], credential_result[1]),
                exclusive=True,
            ).result

            token = authentication_result if authentication_result else token

            self.model = replace(
                self.model,
                api_key=credential_result[2],
            )

        self.model = replace(
            self.model,
            active_token=token,
            valid_credentials=(authentication_result is not None),
        )

        if self.model.valid_credentials:
            self.push_screen(SpotifySearchScreen())
        else:
            self.push_screen(IntitialAuthenticationScreen())

        self.app.post_message(UpdateStatus("Welcome."))

    async def on_update_status(self, message: UpdateStatus) -> None:
        """Handle a status-message update event.

        Used to re-render the ``StatusBar`` widget.

        Parameters
        ----------
        message : UpdateStatus
            The TEA message containing the new status text.

        Notes
        -----
        - Make sure that screen contains ``StatusBar``, otherwise this function will
          do nothing.
        """

        self.model = update(self.model, message)

        try:
            status_widget: StatusBar = self.screen.query_one(StatusBar)
            status_widget.render_from_model(self.model)
        except NoMatches:
            pass

    async def on_authenticating(self, message: Authenticating) -> None:
        """Handle authentication-state updates.

        Updates state model to reflect whether a authentication request
        has been submitted, disabling parts of the user interface and
        rebuffing duplicate requests if so.
        """

        self.model = update(self.model, message)

        if isinstance(self.screen, IntitialAuthenticationScreen):
            self.screen.render_from_model(self.model)

    async def on_valid_credentials(self) -> None:
        """Transition to Spotify A.P.I. search screen after successful validation."""

        self.pop_screen()
        self.push_screen(SpotifySearchScreen())

    async def on_search_request(self, message: SearchRequest) -> None:
        """Handle a request to perform a Spotify search.

        Parameters
        ----------
        message : SearchRequest
            Contains the user query string and search mode (search by track, album,
            etc.)

        Notes
        -----
        - If the new query is identical to the one cached in
          ``self.model.search_query``, no search is issued.
        """

        if self.model.search_query == (message.query, message.mode):
            return

        self.model = update(self.model, message)

        self.app.post_message(UpdateStatus("Searching..."))
        search_results: List[DisplayedTrack] = spotify_search(
            message.query, self.model.active_token, 50
        )
        self.app.post_message(UpdateStatus("Done."))

        if isinstance(self.screen, SpotifySearchScreen):
            self.screen.display_results(create_options_from_results(search_results))

        self.model = replace(self.model, search_results=search_results)

    async def on_track_selected(self, message: TrackSelected) -> None:
        """Handle track selection and fetch YouTube audio source suggestions.

        Parameters
        ----------
        message : TrackSelected
            Contains the index of the selected track from search results.

        Notes
        -----
        - Updates the model with the selected track.
        - Pushes the AudioSource screen onto the stack.
        - Fetches YouTube suggestions for the selected track and populates the screen.
        """

        self.model = replace(
            self.model, selection=self.model.search_results[message.index]
        )
        self.push_screen(AudioSource())

        if isinstance(self.screen, AudioSource):

            suggestion_results = search_youtube(
                self.model.selection, self.model.api_key
            )
            self.model = replace(self.model, suggestion_results=suggestion_results)
            self.screen.populate_suggestions(
                create_options_from_suggestions(suggestion_results)
            )

    async def on_url_selected(self, message: UrlSelected) -> None:
        """Handle YouTube U.R.L. selection and initiate download.

        Parameters
        ----------
        message : UrlSelected
            Contains the index of the selected YouTube URL from suggestions.

        Notes
        -----
        - Posts a StartDownload message with the selected URL.
        """

        self.app.post_message(
            StartDownload(self.model.suggestion_results[message.index].url)
        )

    async def on_start_download(self, message: StartDownload) -> None:
        """Begin downloading the selected track with metadata and album art.

        Parameters
        ----------
        message : StartDownload
            Contains the YouTube U.R.L. to download from.

        Notes
        -----
        - Fetches album artwork from Spotify metadata.
        - Displays download progress in the U.I. via DownloadOption widget.
        - Runs the download in a worker thread to avoid blocking the U.I.
        """

        # Get image.
        image_url = get_metadata(
            self.model.selection.track_id, self.model.active_token
        ).album.image_url

        # Add option to view.
        title = self.model.selection.title
        option = DownloadOption(self.model.selection)

        if isinstance(self.screen, SpotifySearchScreen):
            self.screen.display_download(
                # create_option_from_download(self.model.selection)
                option
            )
        # Download song.
        self.run_worker(
            download_track(
                message.url,
                Path(self.model.downloads_folder, f"{title}"),
                self.model.selection,
                image_url,
            ),
            thread=True,
        )

        # Call to Database

    async def action_submit_authentication(self) -> None:
        """Trigger authentication submission workflow.

        Invoked either by key bindings or by footer button that
        map to the ``submit_authentication`` action.
        """

        # Calls the same internal function as the footer binding defined
        # in the screen.
        if isinstance(self.screen, IntitialAuthenticationScreen):
            await self.screen.on_input_submitted()
