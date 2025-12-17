"""Classes for interaction with WP-CLI."""

import json
import os
import subprocess
from typing import List, Optional

from _io import TextIOWrapper

from cyberfusion.Common import find_executable
from cyberfusion.WordPressSupport.exceptions import CommandFailedError


class WPCLICommand:
    """Abstract WP-CLI implementation for use in scripts."""

    def __init__(
        self,
        path: str,
        *,
        binary_path: Optional[str] = None,
    ) -> None:
        """Construct, execute and validate command execute."""
        self.path = path
        self._binary_path = binary_path

    @property
    def binary_path(self) -> str:
        """Get path to WP-CLI."""
        if self._binary_path:
            return self._binary_path

        return find_executable("wp")

    def execute(
        self,
        command: List[str],
        json_format: bool = False,
        stdin: Optional[TextIOWrapper] = None,
    ) -> None:
        """Set attributes and execute command."""
        self.command = [self.binary_path]
        self.command.extend(command)
        self.command.append(f"--path={self.path}")

        # Add --format if JSON

        if json_format:
            self.command.append("--format=json")

        # Execute command

        try:
            output = subprocess.run(
                self.command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.path,
                env=os.environ.copy()
                | {
                    "PWD": self.path,
                },
                stdin=stdin,
            )
        except subprocess.CalledProcessError as e:
            raise CommandFailedError(
                command=self.command,
                return_code=e.returncode,
                stdout=e.stdout,
                stderr=e.stderr,
            )

        # Set attributes

        self.stdout = output.stdout.rstrip("\n")

        # Cast if JSON

        if json_format:
            self.stdout = json.loads(self.stdout)
