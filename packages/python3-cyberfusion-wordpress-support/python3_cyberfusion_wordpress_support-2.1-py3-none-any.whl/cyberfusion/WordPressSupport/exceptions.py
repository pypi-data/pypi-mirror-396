"""Exceptions."""

from dataclasses import dataclass
from typing import List


class DirectoryNotEmptyError(Exception):
    """Directory is not empty."""

    pass


class ThemeError(Exception):
    """Error related to themes."""

    pass


class ThemeNotInstalledError(ThemeError):
    """Theme is not installed."""

    pass


class ThemeAlreadyActivatedError(ThemeError):
    """Theme is already activated."""

    pass


class URLMissesThemeError(ThemeError):
    """URL does not contain expected theme."""

    pass


class OptionNotExists(Exception):
    """Option doesn't exist."""

    pass


class PairNotExists(Exception):
    """Pair doesn't exist."""

    pass


@dataclass
class CommandFailedError(Exception):
    """Command failed."""

    command: List[str]
    return_code: int
    stdout: str
    stderr: str

    @property
    def streams(self) -> str:
        """Combine output streams."""
        return f"Stdout:\n\n{self.stdout}\n\nStderr:\n\n{self.stderr}"

    def __str__(self) -> str:
        """Stringify exception."""
        return self.streams


class CoreError(Exception):
    """Error related to core."""

    pass


class CoreAlreadyInstalledError(CoreError):
    """Core is already installed."""

    pass


class PluginError(Exception):
    """Error related to plugins."""

    pass


class PluginAlreadyActivatedError(PluginError):
    """Plugin is already activated."""

    pass


class PluginAlreadyInstalledError(PluginError):
    """Plugin is already installed."""

    pass
