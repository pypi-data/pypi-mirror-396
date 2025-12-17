"""Classes for managing plugins."""

from cyberfusion.WordPressSupport import Installation
from cyberfusion.WordPressSupport.exceptions import (
    CommandFailedError,
    PluginAlreadyActivatedError,
    PluginAlreadyInstalledError,
)


class Plugin:
    """Abstraction of WordPress plugin."""

    NAME_COMMAND = "plugin"

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

    def install(self) -> None:
        """Install plugin."""
        if self.is_installed:
            raise PluginAlreadyInstalledError

        self.installation.command.execute([self.NAME_COMMAND, "install", self.name])

    def activate(self) -> None:
        """Activate plugin."""
        if self.is_activated:
            raise PluginAlreadyActivatedError

        self.installation.command.execute([self.NAME_COMMAND, "activate", self.name])
