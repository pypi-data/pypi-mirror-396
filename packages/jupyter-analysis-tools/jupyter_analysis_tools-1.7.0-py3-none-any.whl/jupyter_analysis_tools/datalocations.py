# -*- coding: utf-8 -*-
# datalocations.py

import glob
import os
import shutil
import tempfile
from pathlib import Path

from .utils import indent, isList


def getWorkDir(workDir=None, skip=False):
    """Find a local work dir for temporary files, created during analysis.
    The default is *$HOME/data*."""
    if skip:  # stay in the current directory if desired
        return os.path.abspath(".")
    if not workDir or not len(workDir):
        workDir = Path.home() / "data"
    else:
        workDir = Path(workDir).resolve()
    if not workDir.is_dir():
        os.mkdir(workDir)
    print("Using '{}' as working directory.".format(workDir))
    return workDir


def prepareWorkDir(workDir, srcDir, useExisting=False):
    """Create a temporary working directory and copy
    the input data (series) to it if not already present."""
    # source dir has to exist
    if not os.path.isdir(srcDir):
        raise RuntimeError("Provided source directory '{}' not found!".format(srcDir))
    srcDir = os.path.realpath(srcDir)
    # no separate work dir requested?
    if os.path.samefile(workDir, os.getcwd()):
        print("Working in current directory '{}'.".format(os.getcwd()))
        return srcDir  # nothing to do
    prefix = os.path.basename(srcDir) + "_"
    if useExisting:  # use an existing work dir, avoid copying
        dirs = glob.glob(os.path.join(workDir, prefix + "*"))
        if len(dirs):
            return dirs[0]  # use the first match
        print("No existing work dir found, creating a new one.")
    # copy all data from src dir to a newly created work dir
    workDir = tempfile.mkdtemp(dir=workDir, prefix=prefix)
    print("Copying data to {}:".format(workDir))
    for dn in os.listdir(srcDir):
        srcPath = os.path.join(srcDir, dn)
        dstPath = os.path.join(workDir, dn)
        if os.path.isdir(srcPath):
            shutil.copytree(srcPath, dstPath)
            print(indent, dn)
        if os.path.isfile(srcPath):
            shutil.copy(srcPath, dstPath)
            print(indent, dn)
    print("Done preparing work dir.")
    return workDir


def printFileList(fnlst, numParts=2, limit=20):
    def printlst(lst):
        return [print(indent, fn) for fn in lst]

    def shorten(lst):
        return [os.path.join(*Path(fn).parts[-numParts:]) for fn in lst]

    if len(fnlst) > limit:
        printlst(shorten(fnlst[:3]))
        print(indent, "[...]")
        printlst(shorten(fnlst[-3:]))
    else:
        printlst(shorten(fnlst))


def getDataDirs(dataDir, noWorkDir=False, reuseWorkDir=True, workDir=None):
    """Create a local work dir with a copy of the input data and for storing the results.
    (Data might reside in synced folders which creates massive traffic once batch processing
    results get replaced repeately.)

    Parameters
    ----------
    noWorkDir: bool
        False: Copy input data to a new working dir (default),
        True: otherwise, use data where it is.
    reuseWorkDir: bool
        False: Create a new working dir each time,
        True: reuse the work dir if it exists already (default).

    Returns
    -------
    A list of absolute directory paths.
    """
    basedir = getWorkDir(workDir=workDir, skip=noWorkDir)
    workDir = prepareWorkDir(basedir, dataDir, useExisting=reuseWorkDir)
    print("Entering '{}':".format(workDir))
    dirs = sorted([dn for dn in Path(workDir).iterdir() if dn.is_dir()])
    dirs.append(Path(workDir))
    # [print(os.path.join(*dn.parts[-2:])) for dn in dirs]
    printFileList(dirs, numParts=1)
    return dirs


def getDataFiles(dataDirs, include=None, exclude=None):
    """Return absolute file paths from given directories."""

    def getFiles(dn, include=None):
        if not include:
            include = "*"
        if not isList(include):
            include = (include,)
        return [path for inc in include for path in glob.glob(os.path.join(dn, inc))]

    if not exclude:
        exclude = ()
    if not isList(exclude):
        exclude = (exclude,)
    if not isList(dataDirs):
        dataDirs = (dataDirs,)

    files = [
        fn
        for dn in dataDirs
        for fn in getFiles(dn, include)
        if not any([(ex in fn) for ex in exclude])
    ]
    print("{} files to be analyzed in subdirectories.".format(len(files)))
    return sorted(files)
