"""Classes for managing users."""

import os
from typing import List, Optional

from cyberfusion.Common import get_tmp_file
from cyberfusion.WordPressSupport import Installation
from cyberfusion.WordPressSupport.exceptions import (
    PluginAlreadyInstalledError,
    PluginAlreadyActivatedError,
)
from cyberfusion.WordPressSupport.plugins import Plugin


class User:
    """Abstraction of WordPress user."""

    NAME_COMMAND = "user"

    NAME_SUBCOMMAND_ONE_TIME_LOGIN = "one-time-login"

    NAME_ROLE_ADMINISTRATOR = "administrator"

    def __init__(self, installation: Installation, id_: int) -> None:
        """Set attributes and call functions."""
        self.installation = installation

        self.id = id_

    def update_password(self, password: str) -> None:
        """Update password.

        Passes password to stdin using --prompt.
        """
        _tmp_file_path = get_tmp_file()

        with open(_tmp_file_path, "w") as dupf:
            dupf.write(password + "\n")

        try:
            with open(_tmp_file_path, "r") as dupf:
                self.installation.command.execute(
                    [
                        self.NAME_COMMAND,
                        "update",
                        str(self.id),
                        "--prompt=user_pass",
                    ],
                    stdin=dupf,
                )
        finally:
            os.unlink(_tmp_file_path)

    def get_one_time_login_url(self) -> str:
        """Get one time login URL."""

        # Install plugin

        plugin = Plugin(self.installation, self.NAME_SUBCOMMAND_ONE_TIME_LOGIN)

        try:
            plugin.install()
        except PluginAlreadyInstalledError:
            pass

        try:
            plugin.activate()
        except PluginAlreadyActivatedError:
            pass

        # Execute command

        self.installation.command.execute(
            [
                self.NAME_COMMAND,
                self.NAME_SUBCOMMAND_ONE_TIME_LOGIN,
                str(self.id),
            ],
        )

        return self.installation.command.stdout


class Users:
    """Abstraction of WordPress users."""

    NAME_COMMAND = "user"

    def __init__(self, installation: Installation) -> None:
        """Set attributes and call functions."""
        self.installation = installation

    def get(self, role: Optional[str] = None) -> List[User]:
        """Get and set users."""
        results: List[User] = []

        # Construct command

        command = [self.NAME_COMMAND, "list"]

        if role:
            command.append(f"--role={role}")

        # Execute command

        self.installation.command.execute(
            command,
            json_format=True,
        )

        # Iterate over results

        for user in self.installation.command.stdout:
            results.append(User(self.installation, user["ID"]))

        return results
