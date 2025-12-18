import getpass
import logging
import netrc
import os
import warnings
from pathlib import Path

NETRC_PATH = Path.home() / ".netrc"


class AuthenticationError(Exception):
    """Exception raised when a problem happened when reading credentials."""


def ensure_credentials(host: str):
    """Ensure credentials are present in a .netrc, and prompt otherwise.

    Parameters
    ----------
    host: str
        host for which credentials are needed

    Returns
    -------
        (username, password) tuple

    Raises
    ------
    AuthenticationError
        In case an exception happens when reading credentials
    """
    creds = _get_credentials(host)
    if creds:
        return creds

    return _prompt_and_save_credentials(host)


def _get_credentials(host: str):
    """Get credentials stored in .netrc."""
    if not NETRC_PATH.exists():
        return None

    try:
        auth_data = netrc.netrc(NETRC_PATH)
        login, _, password = auth_data.authenticators(host)
        if login and password:
            return login, password
    except TypeError:
        msg = f"Host {host} doesn't exist in .netrc file."
        warnings.warn(msg)
        return None
    except netrc.NetrcParseError as exc:
        msg = f"Syntax error in .netrc file: {exc}"
        raise AuthenticationError(msg) from exc
    except (AttributeError, ValueError) as exc:
        msg = "An error happened when authenticating Aviso client."
        raise AuthenticationError(msg) from exc


def _prompt_and_save_credentials(host: str):
    """Prompt and save credentials."""
    logging.info("Credentials required for %s", host)
    login = input("Username : ")
    password = getpass.getpass("Password : ")

    with open(NETRC_PATH, "a") as f:
        f.write(f"\nmachine {host} login {login} password {password}\n")

    os.chmod(NETRC_PATH, 0o600)

    return login, password
