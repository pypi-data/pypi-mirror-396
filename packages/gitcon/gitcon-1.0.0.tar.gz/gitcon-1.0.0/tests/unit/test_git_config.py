import subprocess
import unittest
from unittest.mock import patch

from gitcon.git_config import GitConfigError, GitRunner


class TestGitRunner(unittest.TestCase):
    def test_set_global_calls_git_config(self) -> None:
        runner = GitRunner(git_executable="git")

        with patch("subprocess.run") as run:
            runner.set_global("user.name", "Alice")
            run.assert_called_once()

    def test_set_global_raises_on_failure(self) -> None:
        runner = GitRunner()

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, ["git"])):
            with self.assertRaises(GitConfigError):
                runner.set_global("user.name", "Alice")
