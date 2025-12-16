"""Entry point that builds a Trie from stdin and renders it via Graphviz."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, List, Tuple

from graphviz.backend import ExecutableNotFound

from .trie import Trie


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and render a Trie from newline-separated stdin strings.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="trie",
        help="Base name for the rendered file (without extension).",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="pdf",
        help="Graphviz output format (e.g., png, svg, pdf).",
    )
    parser.add_argument(
        "-v",
        "--view",
        action="store_true",
        help="Open the generated image using the system viewer.",
    )
    return parser.parse_args()


def _read_lines(source: Iterable[str]) -> List[str]:
    """Read non-empty lines, preserving trailing whitespace except newline."""
    entries: List[str] = []
    for raw_line in source:
        line = raw_line.rstrip("\n")
        if not line:
            continue
        entries.append(line)
    return entries


def _render(
    trie: Trie,
    filename: str = 'trie',
    format: str = 'png',
    view: bool = False,
    renderer: str = 'cairo',
) -> Tuple[str, bool]:
    """Render the trie as an image file. Returns (path, rendered_successfully)."""
    dot = trie.as_dot()
    dot_path = dot.save(f"{filename}.dot")

    try:
        rendered_path = dot.render(
            filename,
            format=format,
            view=view,
            renderer=renderer,
            cleanup=True,
        )
        return rendered_path, True
    except ExecutableNotFound:
        print(
            f"Graphviz executables not found; kept DOT source at {dot_path}. "
            "Install Graphviz (e.g., https://graphviz.org/download/) to render.",
            file=sys.stderr,
        )
        return dot_path, False


def main() -> int:
    args = _parse_args()
    lines = _read_lines(sys.stdin)

    if not lines:
        print("No input received; nothing to render.", file=sys.stderr)
        return 1

    trie = Trie()
    for entry in lines:
        trie.insert(entry)

    trie = trie.minimize()
    rendered_path, rendered = _render(
        trie,
        filename=args.output,
        format=args.format,
        view=args.view,
    )
    if rendered:
        print(f"Rendered trie for {len(lines)} entries at {rendered_path}")
        return 0

    return 1


def cli() -> None:
    """Console entrypoint used by the installed `charity` script."""
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
