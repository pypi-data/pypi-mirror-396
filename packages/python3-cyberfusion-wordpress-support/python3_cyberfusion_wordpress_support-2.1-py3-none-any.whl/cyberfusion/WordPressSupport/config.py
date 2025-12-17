"""Classes for managing config."""

import os
from enum import StrEnum
from typing import TYPE_CHECKING

from cyberfusion.Common import get_tmp_file
from cyberfusion.WordPressSupport.exceptions import PairNotExists

if TYPE_CHECKING:  # pragma: no cover
    from cyberfusion.WordPressSupport import Installation

from typing import List


class PairType(StrEnum):
    """Pair types."""

    CONSTANT = "constant"
    VARIABLE = "variable"


class Pair:
    """Abstraction of WordPress config pair."""

    NAME_COMMAND = "config"

    def __init__(
        self,
        installation: "Installation",
        *,
        name: str,
        value: str,
        type_: PairType,
    ) -> None:
        """Set attributes and call functions."""
        self.installation = installation

        self.name = name
        self.value = value
        self.type = type_

    def update(self) -> None:
        """Update pair value."""
        self.installation.command.execute(
            [
                self.NAME_COMMAND,
                "set",
                self.name,
                self.value,
                "--no-add",
                f"--type={self.type}",
            ]
        )


class Config:
    """Abstraction of WordPress config."""

    NAME_COMMAND = "config"

    def __init__(self, installation: "Installation") -> None:
        """Set attributes and call functions."""
        self.installation = installation

    def create(
        self,
        database_name: str,
        database_username: str,
        database_user_password: str,
        database_host: str,
    ) -> None:
        """Create WordPress config file.

        Passes admin password to stdin using --prompt.
        """
        self._tmp_file_path = get_tmp_file()

        with open(self._tmp_file_path, "w") as dupf:
            dupf.write(database_user_password + "\n")

        try:
            with open(self._tmp_file_path, "r") as dupf:
                self.installation.command.execute(
                    [
                        self.NAME_COMMAND,
                        "create",
                        f"--dbname={database_name}",
                        f"--dbuser={database_username}",
                        f"--dbhost={database_host}",
                        "--prompt=dbpass",
                    ],
                    stdin=dupf,
                )
        finally:
            os.unlink(self._tmp_file_path)

    def shuffle_salts(self) -> None:
        """Shuffle salts."""
        self.installation.command.execute([self.NAME_COMMAND, "shuffle-salts"])

    def get_pair(self, name: str) -> Pair:
        """Get single pair by name."""
        for pair in self.get_pairs():
            if name != pair.name:
                continue

            return pair

        raise PairNotExists

    def get_pairs(self) -> List[Pair]:
        """Get and set pairs."""
        results: List[Pair] = []

        # Construct command

        command = [self.NAME_COMMAND, "list"]

        # Execute command

        self.installation.command.execute(command, json_format=True)

        # Iterate over results

        for pair in self.installation.command.stdout:
            results.append(
                Pair(
                    self.installation,
                    name=pair["name"],
                    value=pair["value"],
                    type_=PairType(pair["type"]),
                )
            )

        return results
