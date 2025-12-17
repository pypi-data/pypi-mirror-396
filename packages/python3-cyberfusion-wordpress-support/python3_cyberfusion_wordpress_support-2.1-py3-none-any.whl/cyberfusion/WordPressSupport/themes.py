"""Classes for managing themes."""

import os
from typing import Optional
from zipfile import ZipFile

from cyberfusion.Common import download_from_url
from cyberfusion.WordPressSupport import Installation
from cyberfusion.WordPressSupport.exceptions import (
    CommandFailedError,
    ThemeAlreadyActivatedError,
    ThemeNotInstalledError,
    URLMissesThemeError,
)


class Theme:
    """Abstraction of WordPress theme."""

    NAME_COMMAND = "theme"

    def __init__(self, installation: Installation, name: str) -> None:
        """Set attributes and call functions."""
        self.installation = installation
        self.name = name

    @property
    def is_installed(self) -> bool:
        """Set if is installed."""
        try:
            self.installation.command.execute(
                [self.NAME_COMMAND, "is-installed", self.name]
            )
        except CommandFailedError:
            return False

        return True

    @property
    def is_activated(self) -> bool:
        """Set if is activated."""
        try:
            self.installation.command.execute(
                [self.NAME_COMMAND, "is-active", self.name]
            )
        except CommandFailedError:
            return False

        return True

    @property
    def version(self) -> str:
        """Get version."""
        if not self.is_installed:
            raise ThemeNotInstalledError

        self.installation.command.execute(
            [self.NAME_COMMAND, "get", self.name, "--field=version"],
            json_format=True,
        )

        return self.installation.command.stdout

    def install_from_repository(self, *, version: Optional[str] = None) -> None:
        """Install theme from WordPress repository.

        If theme is already installed, theme is updated/downgraded to specified
        version or latest version.
        """
        command = [self.NAME_COMMAND, "install", self.name]

        if version:
            command.append(f"--version={version}")

        if self.is_installed:
            command.append("--force")

        self.installation.command.execute(command)

    @staticmethod
    def get_theme_name_by_zip_file(zip_file_url: str) -> str:
        """Get theme name by ZIP file containing theme."""
        path = download_from_url(zip_file_url)

        theme_name = os.path.normpath(ZipFile(path).namelist()[0])

        os.unlink(path)

        return theme_name

    def install_from_url(self, *, url: str) -> None:
        """Install theme from WordPress URL.

        If theme is already installed, theme is updated/downgraded to theme at
        URL.
        """
        if self.get_theme_name_by_zip_file(url) != self.name:
            raise URLMissesThemeError

        command = [self.NAME_COMMAND, "install", url]

        if self.is_installed:
            command.append("--force")

        self.installation.command.execute(command)

    def activate(self) -> None:
        """Activate theme."""
        if self.is_activated:
            raise ThemeAlreadyActivatedError

        self.installation.command.execute([self.NAME_COMMAND, "activate", self.name])
