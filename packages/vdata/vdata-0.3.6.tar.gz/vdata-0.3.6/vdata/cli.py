import argparse
import subprocess
import traceback
from pathlib import Path

import ch5mpy as ch
from py import sys

import vdata
from vdata.update.update import update_vdata
from vdata.utils import copy_vdata


def print_err(msg: str) -> None:
    print("\033[31m[ERROR] " + msg + "\033[0m", file=sys.stderr)


def update() -> int:
    parser = argparse.ArgumentParser(prog="vdata-update", description="Update a VData from an older version")

    parser.add_argument("filename")
    parser.add_argument("-o", "--out-file", default=None, type=str)
    parser.add_argument("-v", "--verbose", default=False, action="store_true")

    args = parser.parse_args()

    data = ch.H5Dict.read(args.filename, mode=ch.H5Mode.READ_WRITE)

    ez_filename = Path(data.filename)
    ez_filename = ez_filename.with_stem("~" + ez_filename.stem)

    try:
        update_vdata(data, output_file=args.out_file, verbose=args.verbose)

    except Exception as e:
        print_err(" ".join(filter(lambda a: isinstance(a, str), e.args)))  # pyright: ignore[reportUnnecessaryIsInstance]

        if args.verbose:
            traceback.print_tb(e.__traceback__)

        return 1

    print("\033[32m[Done]\033[0m")
    return 0


def copy() -> int:
    parser = argparse.ArgumentParser(prog="vdata-copy", description="Copy a VData to a new location")

    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("-e", "--exclude", default=[], action="append", choices=["obsm", "obsp", "varm", "varp", "uns"])
    parser.add_argument("-v", "--verbose", default=False, action="store_true")

    args = parser.parse_args()

    try:
        copy_vdata(args.source, args.destination, args.exclude, verbose=args.verbose)

    except BaseException as e:
        print_err(" ".join(filter(lambda a: isinstance(a, str), e.args)))  # pyright: ignore[reportUnnecessaryIsInstance]

        if args.verbose:
            traceback.print_tb(e.__traceback__)

        return 1

    print("\033[32m[Done]\033[0m")
    return 0


def info() -> int:
    parser = argparse.ArgumentParser(prog="vdata-copy", description="Copy a VData to a new location")

    parser.add_argument("filename")

    args = parser.parse_args()

    size = subprocess.check_output(["du", "-sh", args.filename]).split()[0].decode("utf-8")
    data = vdata.read(args.filename)

    print(f"""\
size:      \t{size}

name:      \t{data.name}
timepoints:\t{", ".join(map(str, data.timepoints_values))}
shape:     \t{data.n_obs} obs x {data.n_var} vars x {data.n_timepoints} timepoints

layers:    \t{", ".join(data.layers.keys())}
obs:       \t{", ".join(data.obs.columns)}
obsm:      \t{", ".join(data.obsm.keys())}
obsp:      \t{", ".join(data.obsp.keys())}
var:       \t{", ".join(data.var.keys())}
varm:      \t{", ".join(data.varm.keys())}
varp:      \t{", ".join(data.varp.keys())}
uns:       \t{", ".join(data.uns.keys())}
""")
    return 0
