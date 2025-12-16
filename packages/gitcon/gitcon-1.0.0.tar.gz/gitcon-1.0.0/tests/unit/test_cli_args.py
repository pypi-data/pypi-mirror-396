import unittest

from gitcon.cli import build_parser


class TestCliArgs(unittest.TestCase):
    def test_parser_accepts_known_args(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--merge-option",
                "rebase",
                "--name",
                "John Doe",
                "--email",
                "john@example.com",
                "--signing",
                "gpg",
                "--gpg-key",
                "ABCDEF123456",
                "--tag-signing",
                "auto",
            ]
        )

        self.assertEqual(args.merge_option, "rebase")
        self.assertEqual(args.signing, "gpg")
        self.assertEqual(args.tag_signing, "auto")
