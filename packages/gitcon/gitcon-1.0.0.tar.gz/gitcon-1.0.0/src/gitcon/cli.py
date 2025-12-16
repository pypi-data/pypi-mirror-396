from __future__ import annotations

import argparse

from .git_config import GitRunner
from .interactive import InteractiveSetup
from .gpg import GpgRunner


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gitcon",
        description="Configure global Git settings interactively or via CLI arguments.",
    )
    p.add_argument("--interactive", action="store_true", help="Run interactive setup")

    p.add_argument("--merge-option", choices=["merge", "fast-forward", "rebase"])
    p.add_argument("--name")
    p.add_argument("--email")
    p.add_argument("--website")

    p.add_argument("--signing", choices=["gpg", "none"], help="Commit signing method")
    p.add_argument("--gpg-key", help="GPG key ID (required if --signing gpg)")

    p.add_argument(
        "--tag-signing",
        choices=["auto", "none"],
        help="Tag signing policy (auto enables tag.gpgSign)",
    )
    return p


def apply_non_interactive(args: argparse.Namespace, git: GitRunner) -> None:
    # Merge strategy
    if args.merge_option:
        if args.merge_option == "fast-forward":
            git.set_global("merge.ff", "only")
            git.set_global_bool("pull.rebase", False)
        elif args.merge_option == "rebase":
            git.set_global_bool("pull.rebase", True)
        else:
            git.set_global("merge.ff", "true")
            git.set_global_bool("pull.rebase", False)

    # Identity
    if args.name:
        git.set_global("user.name", args.name)
    if args.email:
        git.set_global("user.email", args.email)
    if args.website:
        git.set_global("user.website", args.website)

    # Commit signing
    if args.signing:
        if args.signing == "gpg":
            if not args.gpg_key:
                raise SystemExit("Error: --gpg-key is required when --signing gpg is used.")
            git.set_global_bool("commit.gpgsign", True)
            git.set_global("user.signingkey", args.gpg_key)
            git.set_global("gpg.program", "gpg")
        else:
            git.set_global_bool("commit.gpgsign", False)

    # Tag signing policy
    if args.tag_signing:
        git.set_global_bool("tag.gpgSign", args.tag_signing == "auto")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    git = GitRunner()
    gpg = GpgRunner()

    # Run interactive if explicitly requested OR if nothing meaningful was provided.
    if args.interactive or not any(
        [args.merge_option, args.name, args.email, args.website, args.signing, args.tag_signing]
    ):
        InteractiveSetup(git=git, gpg=gpg).run()
        return 0

    apply_non_interactive(args, git)
    return 0
