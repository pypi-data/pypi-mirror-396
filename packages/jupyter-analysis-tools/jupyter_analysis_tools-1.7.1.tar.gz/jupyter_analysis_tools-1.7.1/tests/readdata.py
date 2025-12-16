# -*- coding: utf-8 -*-
# tests/readdata.py

import json
import os
import tempfile
import zipfile
from pathlib import Path

import numpy

from jupyter_analysis_tools import readdata, readPDHmeta, readSSF, readSSFZ

pathPDH1 = Path("testdata/S2842 water.pdh")
pathPDH2 = Path("testdata/S2843[9].pdh")  # desmeared silica measurement
pathSSFZ = Path("testdata/2015-03-20-Silica.ssfz")


def test_readdata1(capsys):
    assert pathPDH1.is_file()
    df, fn = readdata(pathPDH1)
    captured = capsys.readouterr()
    assert captured.out == f"Reading file 'testdata{os.sep}S2842 water.pdh'\n"
    assert fn == "S2842 water"
    assert df.shape == (1280, 3)
    assert df.columns.tolist() == ["q", "I", "e"]
    assert df.dtypes.tolist() == [numpy.float64, numpy.float64, numpy.float64]
    # checking the first data values
    assert numpy.all(
        df.loc[:2].values
        == numpy.array(
            [
                [-1.005583e00, 5.555556e-08, 2.754402e-08],
                [-9.989474e-01, 3.611111e-07, 6.568830e-08],
                [-9.923112e-01, 3.055556e-07, 6.120415e-08],
            ]
        )
    )
    # and checking the last data values
    assert numpy.all(
        df.loc[df.shape[0] - 3 :].values
        == numpy.array(
            [
                [7.381979e00, 2.972222e-06, 1.792166e-07],
                [7.388376e00, 2.944444e-06, 1.436040e-07],
                [7.394774e00, 2.388889e-06, 1.548690e-07],
            ]
        )
    )
    assert numpy.all(df.median().values == numpy.array([3.233221e00, 5.826389e-05, 8.835466e-07]))


def test_readdata2(capsys):
    # test another file with different naming scheme
    assert pathPDH2.is_file()
    df, fn = readdata(pathPDH2, print_filename=False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert fn == "S2843"
    assert df.shape == (427, 3)
    assert df.columns.tolist() == ["q", "I", "e"]
    assert numpy.all(df.median().values == numpy.array([1.470428, 0.01907878, 0.01353293]))


def test_readPDHmeta1():
    # read the meta data of the PDH file
    assert pathPDH1.is_file()
    data = readPDHmeta(pathPDH1)
    assert data is not None
    assert isinstance(data, dict)
    assert len(data)  # there should be data at all

    # writing the test JSON for comparisons on updates
    # with open(pathPDH1.with_suffix(".json"), "w") as fd:
    #     json.dump(data, fd, indent=4)

    # write the JSON formatted metadata to disk, read it back in and compare
    # it with the expected reference from testdata dir
    with open(pathPDH1.with_suffix(".json")) as fdRef, tempfile.TemporaryFile("w+") as fdNew:
        json.dump(data, fdNew, indent=4)
        fdNew.seek(0)
        assert fdRef.read() == fdNew.read()

    # if there are changes, use this to investigate:
    # from difflib import Differ
    # with open('file1.txt') as f1, open('file2.txt') as f2:
    #    differ = Differ()
    #    for line in differ.compare(f1.readlines(), f2.readlines()):
    #        print(line) # ignore lines starting with ' ' (no change)


def test_readSSF():
    assert pathSSFZ.is_file()
    # unpack the SSFZ to a temporary dir
    with tempfile.TemporaryDirectory() as tempdir:
        with zipfile.ZipFile(pathSSFZ, "r") as zipfd:
            zipfd.extractall(tempdir)
        # read the session meta data from the extracted SSF file
        pathSSF = next(Path(tempdir).glob("*.ssf"))
        assert pathSSF.is_file()
        data = readSSF(pathSSF)
        assert data is not None
        assert isinstance(data, dict)
        assert len(data)  # there should be data at all
        # writing the test JSON for comparisons on updates
        # with open(pathSSFZ.with_suffix(".ssf.json"), "w") as fd:
        #    json.dump(data, fd, indent=4)
        # write the JSON formatted session data to disk
        # and compare it with the expected JSON file from testdata dir
        with open(pathSSFZ.with_suffix(".ssf.json")) as fdRef, tempfile.TemporaryFile(
            "w+"
        ) as fdNew:
            json.dump(data, fdNew, indent=4)
            fdNew.seek(0)
            assert fdRef.read() == fdNew.read()


def test_readSSFZ():
    assert pathSSFZ.is_file()
    data = readSSFZ(pathSSFZ)
    # compare with the expected JSON file from testdata dir
    with open(pathSSFZ.with_suffix(".ssf.json")) as fdRef:
        dataRef = json.load(fdRef)
        assert dataRef == data
