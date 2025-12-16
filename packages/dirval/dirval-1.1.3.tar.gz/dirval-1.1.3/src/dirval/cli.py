from __future__ import annotations

import argparse

from dirval.core import create_stamp_file, validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dirval",
        description="Create and validate a directory stamp.",
    )
    parser.add_argument("path", type=str, help="Path of the directory")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stamp", action="store_true", help="Create a stamp for the directory")
    group.add_argument("--validate", action="store_true", help="Validate the directory")

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.stamp:
        create_stamp_file(args.path)
    else:
        validate(args.path)


if __name__ == "__main__":
    main()
