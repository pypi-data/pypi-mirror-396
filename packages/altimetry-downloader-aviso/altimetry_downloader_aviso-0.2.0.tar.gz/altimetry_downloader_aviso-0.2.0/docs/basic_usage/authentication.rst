Authentication
==============

The download requests to the AVISO Thredds Data Server require user authentication.
To get credentials, please register at `AVISO User Registration <https://www.aviso.altimetry.fr/en/data/data-access/registration-form.html>`_.

This module handles authentication through a ``.netrc`` file located in the user's home directory.
It ensures that user credentials are securely stored and reused for subsequent requests.

Overview
--------

The authentication process relies on the standard UNIX-style ``.netrc`` mechanism to store
login credentials associated with specific hosts.

When the module performs an authenticated request, it proceeds as follows:

1. Checks if a valid ``.netrc`` file exists in the user's home directory.
2. If the file is missing, malformed, or does not contain the expected host entry,
   the user is prompted to enter their credentials interactively.
3. Once the credentials are provided, they are saved (or updated) in the ``.netrc`` file.
4. Future requests reuse the stored credentials automatically.

File Format
------------

The ``.netrc`` file should contain:

.. code-block:: none

   machine tds-odatis.aviso.altimetry.fr
    login <user_login>
    password <user_password>

Note that ``user_login`` is typically an email address associated with the user's account.


Example Usage
-------------

.. code-block:: python

   from altimetry_downloader_aviso import get
   get("SWOT_L3_LR_SSH_Basic", output_dir="aviso_dir", cycle_number=7, pass_number=[12, 13])

If no ``.netrc`` file is found, the module will prompt for credentials:

.. code-block:: console

   Username: my_username
   Password: ...

The credentials are then written to the ``.netrc`` file for future use.

Error Handling
--------------

If the ``.netrc`` file is malformed or credentials are invalid, the module will display a warning message.

See Also
--------

- `Python netrc module documentation <https://docs.python.org/3/library/netrc.html>`_
