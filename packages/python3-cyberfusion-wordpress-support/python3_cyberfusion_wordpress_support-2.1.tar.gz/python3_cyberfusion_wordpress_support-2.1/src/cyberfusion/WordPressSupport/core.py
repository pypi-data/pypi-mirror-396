"""Classes for managing core."""

import os
from typing import TYPE_CHECKING, Optional

from cyberfusion.Common import get_tmp_file
from cyberfusion.WordPressSupport.exceptions import (
    CommandFailedError,
    CoreAlreadyInstalledError,
    DirectoryNotEmptyError,
)

if TYPE_CHECKING:  # pragma: no cover
    from cyberfusion.WordPressSupport import Installation


class Core:
    """Abstraction of WordPress core."""

    NAME_COMMAND = "core"

    def __init__(self, installation: "Installation") -> None:
        """Set attributes and call functions."""
        self.installation = installation

    @property
    def is_installed(self) -> bool:
        """Set if is installed."""
        try:
            self.installation.command.execute([self.NAME_COMMAND, "is-installed"])
        except CommandFailedError:
            return False

        return True

    def download(self, version: str, locale: str, *, force: bool = False) -> None:
        """Download core files."""
        if os.listdir(self.installation.command.path):
            if not force:
                raise DirectoryNotEmptyError

        command = [
            self.NAME_COMMAND,
            "download",
            f"--locale={locale}",
            f"--version={version}",
        ]

        if force:
            command.append("--force")

        self.installation.command.execute(command)

    @property
    def version(self) -> str:
        """Get version."""
        self.installation.command.execute(
            [self.NAME_COMMAND, "version"],
        )

        return self.installation.command.stdout.rstrip()

    def update(
        self,
        only_update_minor: Optional[bool] = None,
        version: Optional[str] = None,
    ) -> None:
        """Update core."""
        command = [
            self.NAME_COMMAND,
            "update",
        ]

        if only_update_minor:
            command.append("--minor")

        if version:
            command.append(f"--version={version}")

        self.installation.command.execute(
            command,
        )

    def install(
        self,
        url: str,
        site_title: str,
        admin_username: str,
        admin_password: str,
        admin_email_address: str,
    ) -> None:
        """Install core.

        Passes admin password to stdin using --prompt.
        """
        if self.is_installed:
            raise CoreAlreadyInstalledError

        # Get tmp file for admin password

        self._tmp_file_path = get_tmp_file()

        # Write admin password to tmp file

        with open(self._tmp_file_path, "w") as apf:
            apf.write(admin_password + "\n")

        # Try/except block to ensure removal of tmp file in 'finally'

        try:
            # Open admin password file and execute command

            with open(self._tmp_file_path, "r") as apf:
                self.installation.command.execute(
                    [
                        self.NAME_COMMAND,
                        "install",
                        f"--url={url}",
                        f"--title={site_title}",
                        f"--admin_user={admin_username}",
                        f"--admin_email={admin_email_address}",
                        "--skip-email",
                        "--prompt=admin_password",
                    ],
                    stdin=apf,
                )
        finally:
            # Remove tmp file

            os.unlink(self._tmp_file_path)
