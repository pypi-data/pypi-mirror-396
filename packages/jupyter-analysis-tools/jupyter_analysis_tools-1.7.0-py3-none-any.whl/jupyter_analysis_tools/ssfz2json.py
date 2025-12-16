# -*- coding: utf-8 -*-
# ssfz2json.py

import argparse
import json
import sys
from pathlib import Path

from jupyter_analysis_tools.readdata import readSSFZ


def main():
    parser = argparse.ArgumentParser(
        description="""
            Reads and parses the embedded metadata of a .SSFZ file created by Anton Paar SAXSquant
            software, converts it to JSON format and outputs it to <stdout>.
            An output file path for the JSON data can be provided by optional argument.
            """
    )
    parser.add_argument(
        "ssfzPath",
        type=lambda p: Path(p).absolute(),
        help="Path of the input .SSFZ file to read.",
    )
    parser.add_argument(
        "-o",
        "--out",
        nargs="?",
        default="stdout",
        help=(
            "Output file path to write the JSON data to. If the filename is omitted, "
            "it is derived from the input file name by adding the .json suffix."
        ),
    )
    args = parser.parse_args()
    # print(args)
    if not args.ssfzPath.is_file():
        print(f"Provided file '{args.ssfzPath}' not found!")
        return 1
    data = readSSFZ(args.ssfzPath)
    json_args = dict(sort_keys=True, indent=2)
    if args.out == "stdout":
        print(json.dumps(data, **json_args))
    else:
        if args.out is None:
            args.out = args.ssfzPath.with_suffix(args.ssfzPath.suffix + ".json")
        if not Path(args.out).parent.is_dir():
            print(f"Directory of provided output file '{args.out}' does not exist!")
            return 1
        with open(args.out, "w") as fd:
            json.dump(data, fd, **json_args)
        print(f"Wrote '{args.out}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
