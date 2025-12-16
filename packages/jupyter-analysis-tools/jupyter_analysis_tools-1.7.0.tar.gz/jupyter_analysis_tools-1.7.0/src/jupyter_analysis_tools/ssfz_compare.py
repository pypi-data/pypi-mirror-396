# -*- coding: utf-8 -*-
# ssfz2json.py

import argparse
import difflib
import json
import sys
from pathlib import Path

from jupyter_analysis_tools.readdata import readSSFZ


def main():
    parser = argparse.ArgumentParser(
        description="""
            Reads and parses the embedded metadata of two .SSFZ files created by Anton Paar
            SAXSquant software, converts them to JSON format and performs a diff-like comparison
            which is output on <stdout>.
            """
    )
    parser.add_argument(
        "fromfile",
        type=lambda p: Path(p).absolute(),
        help="Path of the first .SSFZ file to compare.",
    )
    parser.add_argument(
        "tofile",
        type=lambda p: Path(p).absolute(),
        help="Path of the second .SSFZ file to compare to.",
    )
    json_args = dict(sort_keys=True, indent=2)
    args = parser.parse_args()
    # print(args)
    if not args.fromfile.is_file():
        print(f"Provided file '{args.fromfile}' not found!")
        return 1
    if not args.tofile.is_file():
        print(f"Provided file '{args.tofile}' not found!")
        return 1
    olddata = readSSFZ(args.fromfile)
    newdata = readSSFZ(args.tofile)
    diff = difflib.unified_diff(
        json.dumps(olddata, **json_args).splitlines(keepends=True),
        json.dumps(newdata, **json_args).splitlines(keepends=True),
        fromfile=str(args.fromfile),
        tofile=str(args.tofile),
    )
    for line in diff:
        print(line, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
