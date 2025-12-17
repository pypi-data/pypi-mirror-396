"""Classes for managing cache."""

from cyberfusion.WordPressSupport import Installation
from cyberfusion.WordPressSupport.plugins import Plugin


class Cache:
    """Abstraction of WordPress cache."""

    NAME_COMMAND = "cache"

    NAME_SUBCOMMAND_ELEMENTOR = "elementor"

    def __init__(self, installation: Installation) -> None:
        """Set attributes and call functions."""
        self.installation = installation

    def _regenerate_elementor_css(self) -> None:
        """Regenerate Elementor CSS if Elementor used."""
        if not Plugin(self.installation, self.NAME_SUBCOMMAND_ELEMENTOR).is_installed:
            return

        self.installation.command.execute([self.NAME_SUBCOMMAND_ELEMENTOR, "flush-css"])

    def flush(self) -> None:
        """Flush cache."""
        self.installation.command.execute([self.NAME_COMMAND, "flush"])

        self._regenerate_elementor_css()
