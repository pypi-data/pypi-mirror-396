import unittest
from dataclasses import dataclass

from gitcon.interactive import InteractiveSetup


@dataclass
class FakePrompter:
    answers: list[str]
    idx: int = 0

    def ask(self, prompt: str) -> str:
        value = self.answers[self.idx]
        self.idx += 1
        return value


@dataclass
class SpyGit:
    calls: list[tuple[str, str]]

    def set_global(self, key: str, value: str) -> None:
        self.calls.append((key, value))

    def set_global_bool(self, key: str, enabled: bool) -> None:
        self.set_global(key, "true" if enabled else "false")


class FakeGpg:
    def list_secret_keys_long(self) -> str:
        return "sec rsa4096/DEADBEEF 2020-01-01 [SC]\n"


class TestInteractiveSetup(unittest.TestCase):
    def test_interactive_gpg_enables_tag_signing_by_default(self) -> None:
        calls: list[tuple[str, str]] = []
        git = SpyGit(calls=calls)
        gpg = FakeGpg()

        # merge choice, name, email, website, signing choice, gpg key, tag signing choice
        prompter = FakePrompter(["1", "Alice", "a@example.com", "", "1", "DEADBEEF", ""])

        setup = InteractiveSetup(git=git, gpg=gpg, prompter=prompter)  # type: ignore[arg-type]
        setup.run()

        self.assertIn(("commit.gpgsign", "true"), calls)
        self.assertIn(("tag.gpgSign", "true"), calls)
