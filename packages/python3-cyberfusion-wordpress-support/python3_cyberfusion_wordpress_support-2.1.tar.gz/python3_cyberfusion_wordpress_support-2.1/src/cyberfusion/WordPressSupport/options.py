"""Classes for managing options."""

from typing import Any, List

from cyberfusion.WordPressSupport import Installation
from cyberfusion.WordPressSupport.exceptions import OptionNotExists


class Option:
    """Abstraction of WordPress option."""

    NAME_COMMAND = "option"

    def __init__(self, installation: Installation, *, name: str, value: Any) -> None:
        """Set attributes and call functions."""
        self.installation = installation

        self.name = name
        self.value = value

    @property
    def value(self) -> Any:
        """Set value."""
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """Set value."""

        # In some cases, WP-CLI returns integer values as strings

        if isinstance(value, str) and value.isdigit():
            value = int(value)

        self._value = value

    def update(self) -> None:
        """Update option value."""
        self.installation.command.execute(
            [
                self.NAME_COMMAND,
                "update",
                self.name,
                str(
                    self.value
                ),  # Value must be string to prevent cyberfusion.Common.Command.CommandElementNotStringError
            ]
        )


class Options:
    """Abstraction of WordPress options."""

    NAME_COMMAND = "option"

    NAME_OPTION_BLOG_PUBLIC = "blog_public"  # noindex

    def __init__(self, installation: Installation) -> None:
        """Set attributes and call functions."""
        self.installation = installation

    def get_single(self, name: str) -> Option:
        """Get single option by name."""
        for option in self.get():
            if name != option.name:
                continue

            return option

        raise OptionNotExists

    def get(self) -> List[Option]:
        """Get and set options."""
        results: List[Option] = []

        # Construct command

        command = [self.NAME_COMMAND, "list", "--no-transients"]

        # Execute command

        self.installation.command.execute(command, json_format=True)

        # Iterate over results

        for option in self.installation.command.stdout:
            results.append(
                Option(
                    self.installation,
                    name=option["option_name"],
                    value=option["option_value"],
                )
            )

        return results
