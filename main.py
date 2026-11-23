"""Build the 22 November 2026 news poster and save it as entry.png.

The picture is drawn from scratch on every run by the renderer in
make_image.py, using only the Python standard library. The destination is
$MAKEFUN_OUTPUT_DIR/entry.png, falling back to /output/entry.png in the
grading sandbox. The program touches no network, reads no files and uses
no clock or randomness, so repeated runs write byte-identical output.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import make_image


def main():
    destination_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "entry.png"
    written = make_image.build_entry(str(destination))
    print("wrote {} ({} bytes)".format(destination, written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
