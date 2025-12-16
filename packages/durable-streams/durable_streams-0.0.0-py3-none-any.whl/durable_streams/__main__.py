from __future__ import annotations

import argparse
import sys

from . import __version__

REPO_URL = "https://github.com/durable-streams/durable-streams"


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="durable-streams",
        description="durable-streams (placeholder): implementation in progress.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"durable-streams {__version__} (placeholder)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    _build_parser().parse_args(argv)

    print(
        "durable-streams is not released yet.\n"
        "This is a placeholder package so the name resolves on PyPI.\n"
        f"Follow progress: {REPO_URL}\n",
        file=sys.stderr,
    )
    # Non-zero so it’s obvious this isn’t a working tool yet.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
