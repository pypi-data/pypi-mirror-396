"""User interface screens for the `waft` application.

This module defines the interactive screens used throughout the `waft`
application. Each screen is responsible for rendering widgets, collecting
user input, and emitting TEA messages that drive global state updates in
the application.
"""

from asyncio import gather
from typing import List, Optional, Tuple

from rich.columns import Columns
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Input, OptionList, Select, Static
from textual.widgets.option_list import Option

from waft.authentication import get_spotify_access_token
from waft.keyring import store_credentials
from waft.messages import (Authenticating, SearchRequest, StartDownload,
                      TrackSelected, UpdateStatus, UrlSelected,
                      ValidCredentials)
from waft.model import ApplicationModel
from waft.widgets import Logo, StatusBar


class IntitialAuthenticationScreen(Screen):
    """Screen for collecting initial authentication credentials.

    This screen presents three input fields—client ID, client secret,
    and a YouTube API key—along with keyboard bindings and a status bar.
    """

    BINDING_GROUP_TITLE: str | None = "Initial Authentication Screen"
    BINDINGS = [
        Binding(key="<c-q>", action="app.quit", description="Quit the application"),
        Binding(key="<tab>", action="app.focus_next", description="Focus next"),
        Binding(
            key="<enter>",
            action="app.submit_authentication",
            description="Submit authentication requests",
        ),
    ]

    def render_from_model(self, model: ApplicationModel) -> None:
        """Update widget states based on the current TEA model.

        Parameters
        ----------
        model : ApplicationModel
            The global application state used to determine which inputs
            should be enabled or disabled.
        """

        self.query_one("#client_id_box", Input).disabled = model.authenticating
        self.query_one("#client_secret_box", Input).disabled = model.authenticating
        self.query_one("#youtube_key_box", Input).disabled = model.authenticating

    async def on_input_submitted(self) -> None:
        """Fire when a user hits <enter>/<c-m> or clicks the button in the ::Footer::.

        Notes
        -----
        Authentication itself is performed outside this screen; the
        screen only gathers inputs and dispatches messages.
        """

        # I only used the `mypy` ignore because all solutions I could think of
        # created cyclical imports.
        if self.app.model.authenticating:  # type: ignore[attr-defined]
            return

        # Poll input values.
        client_id: str = self.query_one("#client_id_box", Input).value
        client_secret: str = self.query_one("#client_secret_box", Input).value
        api_key: str = self.query_one("#youtube_key_box", Input).value

        # Check that all credentials are provided, prompt user otherwise.
        if not (client_id and client_secret and api_key):
            self.app.post_message(UpdateStatus("Please provide valid credentials."))
            return

        # Disable input fields and block new requests.
        self.app.post_message(Authenticating(True))

        self.app.post_message(UpdateStatus("Submitting authentication requests..."))

        # Authentication logic (do so asynchronously).
        # NOTE: TODO add youtube api key authentication.
        result: Tuple[Optional[str]] = await gather(
            get_spotify_access_token(client_id, client_secret)
        )

        self.app.post_message(Authenticating(False))

        if result[0] is None:
            self.app.post_message(UpdateStatus("Invalid credentials."))
            return

        store_credentials(client_id, client_secret, api_key)
        self.app.post_message(ValidCredentials())
        self.app.post_message(UpdateStatus("Success."))

    def compose(self) -> ComposeResult:
        """Construct and yield the widgets that make up the screen layout.

        Yields
        ------
        ComposeResult
            An iterable container of Textual widgets, including the
            credential input fields, the application logo, the status
            bar, and the footer.
        """

        client_id_box = Input(
            classes="credentials_input", id="client_id_box", placeholder="Client ID"
        )
        client_secret_box = Input(
            classes="credentials_input",
            id="client_secret_box",
            placeholder="Client Secret",
            password=True,
        )
        youtube_key_box = Input(
            classes="credentials_input",
            id="youtube_key_box",
            placeholder="YouTube API Key",
        )

        client_id_box.border_title = "Client ID"
        client_secret_box.border_title = "Client Secret"
        youtube_key_box.border_title = "YouTube API Key"

        status_bar = StatusBar()

        yield Horizontal(
            Vertical(
                Logo(id="logo"),
                client_id_box,
                client_secret_box,
                youtube_key_box,
                classes="initial_screen_alignment",
            ),
            classes="initial_screen_alignment",
        )
        yield status_bar
        yield Footer(show_command_palette=False)


class SpotifySearchScreen(Screen):
    """Screen for the Spotify A.P.I. search view.

    This screen presents a minimal user interface for entering or initiating search
    queries against the Spotify A.P.I.
    """

    BINDING_GROUP_TITLE: str | None = "Spotify A.P.I. Search Screen"
    BINDINGS = [
        Binding(key="<c-q>", action="app.quit", description="Quit the application")
    ]

    def compose(self) -> ComposeResult:
        """Construct and yield the widgets that make up the screen layout.

        Yields
        ------
        ComposeResult
            An iterable container of Textual widgets, including the search input bar,
            mode selector, results list, download progress list, status bar, and
            footer.
        """

        search_bar: Horizontal = Horizontal(
            Input(placeholder="Search", id="search_input"),
            Button("", id="search_button"),
            id="search_bar",
        )
        search_mode: Select = Select(
            [("Track", "track")],  # NOTE: Add Album search in future.
            allow_blank=False,
            compact=True,
            id="search_mode",
        )
        header_text: Columns = Columns(
            [
                Text("Title", justify="left"),
                Text("Album", justify="left"),
                Text("Duration", justify="right"),
            ],
            expand=True,
            equal=False,
        )
        search_results: Vertical = Vertical(
            Static(header_text),
            OptionList(id="search_results"),
            id="search_results_view",
        )
        downloads: OptionList = OptionList(id="downloads_view")

        search_bar.border_title = "[1] ─ Search"
        search_results.border_title = "[2] ─ Search Results"
        downloads.border_title = "[3] ─ Progress"

        status_bar: StatusBar = StatusBar()

        yield Container(
            Horizontal(
                Vertical(
                    Horizontal(search_bar, search_mode, id="search_header"),
                    search_results,
                ),
                downloads,
            )
        )
        yield status_bar
        yield Footer(show_command_palette=False)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission events in the search bar.

        Triggers a Spotify search when the user presses Enter in the search input field,
        then moves focus to the results list for keyboard navigation.

        Parameters
        ----------
        event : Input.Submitted
            The input submission event containing the search query value.
        """

        if event.input.id == "search_input":
            mode: str = str(self.query_one("#search_mode", Select).value)
            self.app.post_message(SearchRequest(event.value, mode))
            self.query_one("#search_results", OptionList).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle search button click events.

        Triggers a Spotify search when the user clicks the search button,
        using the current value in the search input field.

        Parameters
        ----------
        event : Button.Pressed
            The button press event.

        Notes
        -----
        - Only processes events from the search_button widget.
        """

        if event.button.id == "search_button":
            query: str = self.query_one("#search_input", Input).value.strip()
            mode: str = str(self.query_one("#search_mode", Select).value)
            self.app.post_message(SearchRequest(query, mode))

    async def on_select_changed(self, event: Select.Changed) -> None:
        """Handle search mode selection changes.

        Automatically re-runs the current search query when the user changes
        the search mode (e.g., from track to album search).

        Parameters
        ----------
        event : Select.Changed
            The select widget change event containing the new mode value.

        Notes
        -----
        - Only processes events from the search_mode widget.
        - Only triggers a new search if a query is already present.

        """

        if event.select.id == "search_mode":
            query: str = self.query_one("#search_input", Input).value.strip()
            mode: str = str(event.value)
            if query:
                self.app.post_message(SearchRequest(query, mode))

    def display_results(self, results: List[Option]) -> None:
        """Update the search results list with new options.

        Clears the current search results and populates the list with new
        track options returned from a Spotify search.

        Parameters
        ----------
        results : List[Option]
            List of Textual Option objects representing search results to display.
        """

        search_results_view: OptionList = self.query_one("#search_results", OptionList)
        search_results_view.clear_options()
        search_results_view.add_options(results)

    def display_download(self, download: Option) -> None:
        """Add a new download to the progress view.

        Appends a download progress option to the downloads list, allowing
        users to monitor active downloads.

        Parameters
        ----------
        download : Option
            A Textual Option object representing the download to display.
        """

        search_results_view: OptionList = self.query_one("#downloads_view", OptionList)
        search_results_view.add_option(download)

    async def on_option_list_option_selected(
        self, event: OptionList.OptionMessage
    ) -> None:
        """Handle track selection from the search results list.

        Dispatches a TrackSelected message when the user selects a track,
        triggering the audio source selection workflow.

        Parameters
        ----------
        event : OptionList.OptionMessage
            The option selection event containing the selected index.

        Notes
        -----
        - Only processes events from the search_results widget.
        """

        if event.option_list.id == "search_results":
            self.app.post_message(TrackSelected(event.option_index))


class AudioSource(ModalScreen):
    """Modal dialog for selecting or entering an audio source U.R.L.

    This screen is used to collect a YouTube source U.R.L. or allow the user to choose
    from a list of suggested matches.
    """

    BINDING_GROUP_TITLE: str | None = "Audio Source Selection Screen"
    BINDINGS = [
        Binding(key="<c-q>", action="app.quit", description="Quit the application"),
        Binding(
            key="esc",
            action="app.cancel_source_select",
            description="Quit the application",
        ),
    ]

    def compose(self) -> ComposeResult:
        """Construct and yield the widgets that make up the screen layout.

        Yields
        ------
        ComposeResult
            An iterable container of Textual widgets, including the U.R.L. input field
            and a list of suggestion options.
        """
        url_field: Input = Input(id="url_field")
        source_suggestions: OptionList = OptionList(id="suggestions_view")
        url_field.border_title = "Provide YouTube URL:"
        source_suggestions.border_title = "Suggestions (press <tab> to focus)"

        yield Horizontal(Vertical(url_field, source_suggestions))

    def populate_suggestions(self, suggestions: List[Option]) -> None:
        """Populate the suggestions list with YouTube search results.

        Clears existing suggestions and adds new YouTube video options
        for the user to choose from as audio sources.

        Parameters
        ----------
        suggestions : List[Option]
            List of Textual Option objects representing YouTube search results.
        """

        suggestions_view: OptionList = self.query_one("#suggestions_view", OptionList)
        suggestions_view.clear_options()
        suggestions_view.add_options(suggestions)

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard events for modal navigation and URL submission.

        Processes Escape to close the modal and Enter to submit a manually
        entered YouTube URL for download.

        Parameters
        ----------
        event : events.Key
            The keyboard event containing the pressed key.
        """

        if event.key == "escape":
            # Prevent Input from processing it.
            event.stop()
            self.app.pop_screen()
        elif event.key == "enter":
            url = self.query_one("#url_field", Input).value.strip()
            if not url:  # add validation
                return
            event.stop()
            self.app.pop_screen()
            self.app.post_message(StartDownload(url))

    async def on_option_list_option_selected(
        self, event: OptionList.OptionMessage
    ) -> None:
        """Handle selection of a YouTube suggestion from the list.

        Dispatches a UrlSelected message when the user chooses a suggested
        video, then closes the modal to begin the download.

        Parameters
        ----------
        event : OptionList.OptionMessage
            The option selection event containing the selected suggestion index.
        """

        if event.option_list.id == "suggestions_view":
            self.app.post_message(UrlSelected(event.option_index))
            self.app.pop_screen()
