from __future__ import annotations

import subprocess
from dataclasses import dataclass


class GitConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitRunner:
    """
    Thin wrapper around `git config` calls so we can mock it in tests.
    """

    git_executable: str = "git"

    def set_global(self, key: str, value: str) -> None:
        try:
            subprocess.run(
                [self.git_executable, "config", "--global", key, value],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise GitConfigError(f"Failed to set git config {key}={value}") from exc

    def set_global_bool(self, key: str, enabled: bool) -> None:
        self.set_global(key, "true" if enabled else "false")
