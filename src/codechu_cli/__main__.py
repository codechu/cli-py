"""CLI demo entrypoint — ``python -m codechu_cli``.

Cycles through spinner styles (optionally filtered by family/tag) so
users can preview the catalog before picking one.
"""

from __future__ import annotations

import argparse
import sys
import time

from . import SPINNER_FAMILIES, SPINNER_STYLES, STYLE_TAGS, Spinner


def main() -> None:
    p = argparse.ArgumentParser(prog="codechu-cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    demo = sub.add_parser("demo", help="Cycle through spinner styles")
    demo.add_argument("--family", help="Limit to one family")
    demo.add_argument("--tag", help="Limit to one tag")
    demo.add_argument(
        "--per-style",
        type=float,
        default=1.5,
        help="Seconds to show each style (default 1.5)",
    )

    sub.add_parser("list", help="Print all style names + families")

    args = p.parse_args()

    if args.cmd == "list":
        for fam, names in SPINNER_FAMILIES.items():
            print(f"\n{fam}:")
            for n in names:
                print(f"  {n}")
        return

    if args.cmd == "demo":
        styles = list(SPINNER_STYLES)
        if args.family:
            styles = SPINNER_FAMILIES.get(args.family, [])
        if args.tag:
            tagged = STYLE_TAGS.get(args.tag, set())
            styles = [s for s in styles if s in tagged]
        if not styles:
            print(
                f"No styles match family={args.family!r} tag={args.tag!r}",
                file=sys.stderr,
            )
            sys.exit(2)
        for s in styles:
            print(f"\n  {s}")
            with Spinner(f"  {s}", style=s):
                time.sleep(args.per_style)


if __name__ == "__main__":
    main()
