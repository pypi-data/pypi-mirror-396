from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Sequence

from snx.runner import run_program_from_file


def _get_version() -> str:
    try:
        return version("snx-simulator")
    except PackageNotFoundError:
        return "dev"


PROG_NAME = "snx"
VERSION = _get_version()
DESCRIPTION = "Simulate execution of SN/X assembly programs."
EPILOG = """\
Examples:
  snx sample.s
  snx ./examples/fib.s
  snx ~/snx-programs/demo.s

Project: https://github.com/snowykr/snx-simulator
"""


class SNXArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        sys.stderr.write(f"{self.prog}: error: {message}\n")
        sys.stderr.write(f"For help, run: {self.prog} -h\n")
        self.exit(2)


def create_parser() -> SNXArgumentParser:
    parser = SNXArgumentParser(
        prog=PROG_NAME,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.add_argument(
        "path",
        metavar="PATH",
        type=Path,
        help="path to an SN/X assembly source file (.s)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    return run_program_from_file(args.path)


if __name__ == "__main__":
    sys.exit(main())
