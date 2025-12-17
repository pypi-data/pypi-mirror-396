"""Classes for managing database."""

from cyberfusion.WordPressSupport import Installation


class Database:
    """Abstraction of WordPress database."""

    NAME_COMMAND_SEARCH_REPLACE = "search-replace"

    def __init__(self, installation: Installation) -> None:
        """Set attributes and call functions."""
        self.installation = installation

    def search_replace(self, *, search_string: str, replace_string: str) -> int:
        """Search and replace string in database."""
        self.installation.command.execute(
            [
                self.NAME_COMMAND_SEARCH_REPLACE,
                search_string,
                replace_string,
                "--format=count",
            ],
        )

        return int(self.installation.command.stdout)
