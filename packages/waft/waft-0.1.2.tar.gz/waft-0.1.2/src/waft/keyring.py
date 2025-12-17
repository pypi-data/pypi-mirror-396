"""Utilities for securely storing and retrieving locally persisted credentials.

This module wraps the `securecredentials` library to provide a portable,
encrypted credential store for the application. It is used to load
previously saved credentials at startup and to persist new ones supplied
by the user.

Notes
-----
- ``securecredentials`` does not ship with type stubs, so imports are
  marked with ``type: ignore``.
"""

from typing import Optional, Tuple

from securecredentials import SecureCredentials  # type: ignore[import-untyped]
from securecredentials.exceptions import (  # type: ignore[import-untyped]
    MasterDatabaseNotFoundError, UserDatabaseNotFoundError)


def retrieve_credentials() -> Optional[Tuple[str, str, str]]:
    """Retrieve any stored Spotify and YouTube credentials.

    This function attempts to load the application's encrypted master key
    and then fetch the saved credential fields from the user database.
    If the master key or user database does not exist, they are created
    or treated as empty respectively.

    Returns
    -------
    tuple[str, str, str] | None
        A 3-tuple containing the stored Spotify client ID, Spotify client
        secret, and YouTube A.P.I. key. Returns ``None`` if the user
        credential database is missing.
    """
    # Check for master key.
    try:
        # There was no better way to do this that would be cross-platform.
        SecureCredentials._load_master_key()  # pylint: disable=protected-access
    except MasterDatabaseNotFoundError:
        SecureCredentials.store_master_key(
            master_key=SecureCredentials.generate_master_key(), user_confirmation=False
        )

    try:
        return (
            SecureCredentials.get_secure("SPOTIFY ID"),
            SecureCredentials.get_secure("SPOTIFY SECRET"),
            SecureCredentials.get_secure("YOUTUBE KEY"),
        )
    except UserDatabaseNotFoundError:
        return None


def store_credentials(client_id: str, client_secret: str, youtube_api_key: str) -> None:
    """Store user-provided Spotify and YouTube credentials securely.

    Parameters
    ----------
    client_id : str
        The Spotify Client ID to store.
    client_secret : str
        The Spotify Client Secret to store.
    youtube_api_key : str
        The YouTube Data API key to store.
    """

    SecureCredentials.set_secure(field="SPOTIFY ID", plaintext=client_id)
    SecureCredentials.set_secure(field="SPOTIFY SECRET", plaintext=client_secret)
    SecureCredentials.set_secure(field="YOUTUBE KEY", plaintext=youtube_api_key)
