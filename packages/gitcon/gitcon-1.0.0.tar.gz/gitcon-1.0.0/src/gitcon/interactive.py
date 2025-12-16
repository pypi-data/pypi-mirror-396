from __future__ import annotations

from dataclasses import dataclass

from .git_config import GitRunner
from .gpg import GpgRunner


@dataclass(frozen=True)
class InteractivePrompter:
    """
    A small interface to allow mocking user input in tests.
    """

    def ask(self, prompt: str) -> str:
        return input(prompt)


@dataclass
class InteractiveSetup:
    git: GitRunner
    gpg: GpgRunner
    prompter: InteractivePrompter = InteractivePrompter()

    def run(self) -> None:
        self._configure_merge_strategy()
        self._configure_identity()
        self._configure_signing()

    def _configure_merge_strategy(self) -> None:
        print("Choose your merge strategy:")
        print("  1) Merge commit (default)")
        print("  2) Fast-forward only")
        print("  3) Rebase (for git pull)")
        choice = self.prompter.ask("Your choice (1/2/3): ").strip()

        if choice == "2":
            self.git.set_global("merge.ff", "only")
            self.git.set_global_bool("pull.rebase", False)
        elif choice == "3":
            self.git.set_global_bool("pull.rebase", True)
        else:
            self.git.set_global("merge.ff", "true")
            self.git.set_global_bool("pull.rebase", False)

    def _configure_identity(self) -> None:
        name = self.prompter.ask("Enter your Git user name: ").strip()
        email = self.prompter.ask("Enter your Git email: ").strip()
        self.git.set_global("user.name", name)
        self.git.set_global("user.email", email)

        website = self.prompter.ask("Enter your website (optional): ").strip()
        if website:
            self.git.set_global("user.website", website)

    def _configure_signing(self) -> None:
        print("\nChoose your commit signing method:")
        print("  1) GPG signing (recommended)")
        print("  2) No signing")
        choice = self.prompter.ask("Your choice (1/2): ").strip()

        if choice == "1":
            print("\nAvailable GPG keys:")
            try:
                print(self.gpg.list_secret_keys_long())
            except Exception as exc:  # keep interactive friendly
                print("Error listing GPG keys:", exc)

            key_id = self.prompter.ask("Enter your GPG key ID: ").strip()
            self.git.set_global_bool("commit.gpgsign", True)
            self.git.set_global("user.signingkey", key_id)
            self.git.set_global("gpg.program", "gpg")

            tag_choice = self.prompter.ask("Also sign tags by default? (Y/n): ").strip().lower()
            sign_tags = tag_choice != "n"
            self.git.set_global_bool("tag.gpgSign", sign_tags)
            return

        # Default: no signing
        self.git.set_global_bool("commit.gpgsign", False)
        self.git.set_global_bool("tag.gpgSign", False)
