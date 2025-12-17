"""Functions to run `occ` commands."""

import subprocess
from typing import List

from cyberfusion.Common import find_executable
from cyberfusion.NextCloudSupport.exceptions import CommandFailedError

PHP_BIN = find_executable("php")


def run_command(command: List[str], cwd: str) -> str:
    """Run command and get output."""
    command = [
        PHP_BIN,
        "-d",
        "memory_limit=512M",
        "occ",
        "--no-interaction",
    ] + command

    try:
        return subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        ).stdout.rstrip()
    except subprocess.CalledProcessError as e:
        raise CommandFailedError(
            return_code=e.returncode,
            stdout=e.stdout,
            stderr=e.stderr,
            command=command,
        )
