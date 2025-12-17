"""Execution entry point for the `waft` application.

This module initializes and runs the Textual-based WAFT application.
It constructs the root :class:`Application` object and starts the
event loop when executed as a script.

Examples
--------
To run the application from the command line::

    $ textual run src/waft
"""

from textual.app import App

from waft.application import Application

def waft() -> None:
    """TODO.

    TODO.
    """
    
    application: App = Application()
    application.run()


if __name__ == "__main__":
    waft()
