"""Entry point for the news-image-20261122 entry.

Draws the 22 November 2026 world-news poster fresh on every run with the
pure-stdlib renderer in make_image.py and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png in the grading sandbox).
No network, no input files, no clock, no randomness, so both graded runs
produce identical bytes.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from make_image import build_entry


def run():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    target = os.path.join(out, "entry.png")
    size = build_entry(target)
    print("wrote %s (%d bytes)" % (target, size))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
