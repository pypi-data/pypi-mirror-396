# -*- coding: utf-8 -*-
# utils.py

import contextlib
import copy
import itertools
import locale
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

indent = "    "


def setLocaleUTF8():
    """Fix the Jupyter locale which is not UTF-8 by default on Windows."""
    locOld = locale.getpreferredencoding(False).lower()

    def getpreferredencoding(do_setlocale=True):
        return "utf-8"

    locale.getpreferredencoding = getpreferredencoding
    locNew = locale.getpreferredencoding(False)
    if locOld != locNew:
        print(f"Updated locale from {locOld} -> {locNew}.")


def isLinux():
    return platform.system().lower() in "linux"


def isMac():
    return platform.system().lower() in "darwin"


def isWindows():
    return platform.system().lower() in "windows"


def isList(obj):
    """Return true if the provided object is list-like including a numpy array but not a string.

    >>> isList([1, 2, 'a'])
    True
    >>> isList(tuple((1, 2, 'a')))
    True
    >>> import numpy
    >>> isList(numpy.arange(5))
    True
    >>> isList("dummy")
    False
    >>> isList(None)
    False
    """
    return isinstance(obj, (list, tuple, np.ndarray))


def shortenWinPath(path):
    if not isWindows():
        return path
    import win32api

    return win32api.GetShortPathName(path)


def appendToPATH(parentPath, subdirs=None, verbose=False):
    """Adds the given path with each subdirectory to the PATH environment variable."""
    parentPath = Path(parentPath)
    if not parentPath.is_dir():
        return  # nothing to do
    if subdirs is None:
        subdirs = ["."]
    sep = ";" if isWindows() else ":"
    PATH = os.environ["PATH"].split(sep)
    for path in subdirs:
        path = parentPath / path
        if verbose:
            print(indent, path, "[exists: {}]".format(path.is_dir()))
        if path not in PATH:
            PATH.append(str(path))
    os.environ["PATH"] = sep.join(PATH)


def addEnvScriptsToPATH():
    """Prepends the *Scripts* directory of the current Python environment base directory to systems
    PATH variable.

    It is intended for Conda (Miniforge) environments on Windows that do not have this in their PATH
    environment variable, causing them to miss many commands provided from this location.
    """
    envPath = [p for p in sys.path if p.endswith("Lib")]
    if not envPath:
        return  # probably not a Miniforge environment
    envPath = envPath[0]
    envPath = Path(envPath).parent / "Scripts"
    sep = ";" if isWindows() else ":"
    environPATH = os.environ["PATH"].split(sep)
    # print(environPATH)
    if envPath.exists() and str(envPath) not in environPATH:
        environPATH = [str(envPath)] + environPATH
        os.environ["PATH"] = sep.join(environPATH)


def networkdriveMapping(cmdOutput: str = None, resolveNames: bool = True):
    """Returns a dict of mapping drive letters to network paths (on Windows)."""
    if isWindows():
        if cmdOutput is None:
            proc = subprocess.run(["net", "use"], capture_output=True, text=True, encoding="cp850")
            cmdOutput = proc.stdout

        def resolveFQDN(uncPath):
            if not resolveNames:
                return uncPath
            parts = uncPath.split("\\")
            idx = [i for i, part in enumerate(parts) if len(part)][0]
            proc = subprocess.run(
                ["nslookup", parts[idx]], capture_output=True, text=True, encoding="cp850"
            )
            res = [line.split() for line in proc.stdout.splitlines() if line.startswith("Name:")]
            if len(res) and len(res[0]) == 2:
                parts[idx] = res[0][1]
            return "\\".join(parts)

        rows = [line.split() for line in cmdOutput.splitlines() if "Windows Network" in line]
        rows = {
            row[1]: resolveFQDN(row[2])
            for row in rows
            if row[1].endswith(":") and row[2].startswith(r"\\")
        }
        return rows
    else:  # Linux (tested) or macOS (untested)
        if cmdOutput is None:
            proc = subprocess.run(["mount"], capture_output=True, text=True)
            cmdOutput = proc.stdout

        def parse(line):
            # position of last opening parenthesis, start of options list
            lastParen = list(i for i, c in enumerate(line) if "(" == c)[-1]
            line = line[:lastParen].strip()
            spaces = list(i for i, c in enumerate(line) if " " == c)
            fstype = line[spaces[-1] :].strip()  # last remaining word is the filesystem type
            line = line[: spaces[-2]].strip()  # strip the 'type' indicator as well
            sepIdx = line.find(" on /")  # separates destination from mount point
            dest = line[:sepIdx].strip()
            mountpoint = line[sepIdx + 4 :].strip()
            yield (mountpoint, dest, fstype)

        return {
            mp: dst
            for line in cmdOutput.strip().splitlines()
            for (mp, dst, fstype) in parse(line)
            if fstype in ("nfs", "cifs", "sshfs", "afs", "ext4")
        }
    return {}


def makeNetworkdriveAbsolute(filepath, cmdOutput: str = None, resolveNames: bool = True):
    """Replaces the drive letter of the given path by the respective network path, if possible."""
    if filepath.drive.startswith(r"\\"):
        return filepath  # it's a UNC path already
    if isWindows():
        drivemap = networkdriveMapping(cmdOutput=cmdOutput, resolveNames=resolveNames)
        prefix = drivemap.get(filepath.drive, None)
        if prefix is not None:
            filepath = Path(prefix).joinpath(*filepath.parts[1:])
    else:  # Linux or macOS
        drivemap = networkdriveMapping(cmdOutput=cmdOutput, resolveNames=resolveNames)
        # search for the mountpoint, starting with the longest, most specific, first
        for mp, target in sorted(drivemap.items(), key=lambda tup: len(tup[0]), reverse=True):
            if filepath.is_relative_to(mp):
                return Path(target).joinpath(filepath.relative_to(mp))
    return filepath


def checkWinFor7z():
    """Extend the PATH environment variable for access to the 7-zip executable."""
    if not isWindows():
        return  # tests below are intended for Windows
    sevenzippath = r"C:\Program Files\7-Zip"
    if not os.path.isdir(sevenzippath):
        print(
            "7-Zip not found in '{}'.\n".format(sevenzippath)
            + "7-Zip is required for managing data files and results!."
        )
        return
    print("Adding the following directory to $PATH:")
    appendToPATH(sevenzippath)
    print("\nUpdated PATH:")
    for path in os.environ["PATH"].split(";"):
        print(indent, path)


def extract7z(fn, workdir=None):
    assert os.path.isfile(os.path.join(workdir, fn)), "Provided 7z archive '{}' not found!".format(
        fn
    )
    print(f"Extracting '{fn}': ")
    proc = subprocess.run(
        ["7z", "x", fn],
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(proc.stdout.decode(errors="ignore"))
    if len(proc.stderr):
        print("## stderr:\n", proc.stderr.decode(errors="ignore"))


# https://stackoverflow.com/a/13847807
@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)


def setPackage(globalsdict):
    """Sets the current directory of the notebook as python package to make relative module imports
    work.

    Usage: `setPackage(globals())`
    """
    path = Path().resolve()
    searchpath = str(path.parent)
    if searchpath not in sys.path:
        sys.path.insert(0, searchpath)
    globalsdict["__package__"] = path.name
    globalsdict["__name__"] = path.name
    print(f"Setting the current directory as package '{path.name}': \n  {path}.")


def grouper(iterable, n, fillvalue=None):
    """Returns an iterator over a list of tuples (grouping) for a given flat iterable."""
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def fmtErr(val, std, precision=2, width=None):
    """Formats a given value and its stdandard deviation to physics notation, e.g. '1.23(4)'."""
    if width is None:
        width = ""
    fmt = "{:" + str(width) + "." + str(precision) + "f}({:.0f})"
    # print("fmtErr val:", val, "std:", std)
    return fmt.format(val, std * 10 ** (precision))


def updatedDict(d, key, value):
    """Implements the \\|= operator for dict in Python version <3.9."""
    dd = copy.copy(d)
    dd[key] = value
    return dd


def naturalKey(name):
    """Split string into list of strings and integers. Use as *key* function for sorting files."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", name)]
