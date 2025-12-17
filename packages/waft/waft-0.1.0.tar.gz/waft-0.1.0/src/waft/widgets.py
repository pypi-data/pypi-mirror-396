"""Custom Textual widgets used throughout the `waft` application.

This module defines user interface components.
"""

# from rich.progress_bar import ProgressBar
from rich.table import Table
from textual.widgets import Static
from textual.widgets.option_list import Option

from waft.datatypes import DisplayedTrack
from waft.model import ApplicationModel

# from rich.padding import Padding


class Logo(Static):
    """Widget for displaying the WAFT application logo or splash text."""

    def on_mount(self) -> None:
        """Load and display the logo text.

        Reads the contents of ``splashtext.txt`` from the working
        directory and stores it in ``self.content`` for rendering.
        """

        with open("splashtext.txt", "r", encoding="utf-8") as file:
            self.content = file.read()


class StatusBar(Static):
    """
    Widget for displaying the global status message.

    The status bar reflects the ``status_message`` field of the
    application model and is updated via calls to
    :meth:`render_from_model`.
    """

    def on_mount(self):
        """Initialize static widget properties.

        The widget is styled with a ``Status`` border title and is marked
        as non-focusable to prevent accidental input capture during text
        navigation.
        """

        self.border_title = "Status"
        self.can_focus = False

    def render_from_model(self, model: ApplicationModel) -> None:
        """Update the displayed status text using the application model.

        Parameters
        ----------
        model : ApplicationModel
            The current T.E.A. model providing the status message to display.
        """

        self.update(model.status_message)


class DownloadOption(Option):
    """Custom Option widget for displaying download progress.

    Extends the base Textual Option to show track metadata along with
    a progress bar indicating download completion status.

    Parameters
    ----------
    track : DisplayedTrack
        The track metadata to display in the download option.

    Attributes
    ----------
    title : str
        The track title.
    artist : str
        The track artist.
    album : str
        The album name.
    progress : float
        Current download progress as a percentage (0-100).
    """

    def __init__(self, track: DisplayedTrack) -> None:
        self.title = track.title
        self.artist = track.artist
        self.album = track.album
        self.progress = 0
        self.label = self.render_option()
        super().__init__(self.render_option())

    def update(self, progress: float):
        """Update the download progress and refresh the display.

        Parameters
        ----------
        progress : float
            New progress value as a percentage (0-100).
        """

        self.progress = int(progress)
        self.label = self.render_option()

    def render_option(self):
        """Render the option layout with track info and progress bar.

        Returns
        -------
        Table
            A Rich Table containing the formatted track information and
            progress bar for display in the OptionList.
        """

        table: Table = Table.grid(expand=True)

        # table.
        table.add_row(f"[b]{self.title}[/b]")
        table.add_row(f"{self.artist}")
        table.add_row(f"{self.album}")

        # progress = ProgressBar(
        #     total=100, completed=self.progress, complete_style="orchid"
        # )

        # table.add_row(Padding(progress, (1, 4)))

        return table
