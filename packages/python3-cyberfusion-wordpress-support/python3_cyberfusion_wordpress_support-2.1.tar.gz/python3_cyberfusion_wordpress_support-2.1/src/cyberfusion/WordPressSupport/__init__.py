"""Classes for managing WordPress."""

from typing import Optional

from cyberfusion.WordPressSupport.wp_cli import WPCLICommand


class Installation:
    """Abstraction of WordPress installation."""

    def __init__(self, path: str, *, wp_cli_binary_path: Optional[str] = None) -> None:
        """Set attributes and call functions."""
        self.command = WPCLICommand(path, binary_path=wp_cli_binary_path)
