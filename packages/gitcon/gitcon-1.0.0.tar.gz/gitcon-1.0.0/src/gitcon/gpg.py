from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class GpgRunner:
    """
    Wrapper around GPG operations used by the CLI.
    """

    gpg_executable: str = "gpg"

    def list_secret_keys_long(self) -> str:
        result = subprocess.run(
            [self.gpg_executable, "--list-secret-keys", "--keyid-format", "LONG"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout
