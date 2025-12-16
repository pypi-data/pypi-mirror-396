# -*- coding: utf-8 -*-
# readdata.py

import tempfile
import warnings
import xml.etree.ElementTree as et
import zipfile
from pathlib import Path

import pandas as pd


def readdata(fpath, q_range=None, read_csv_args=None, print_filename=True):
    """Read a datafile pandas Dataframe
    extract a file_name
    select q-range: q_min <= q <= q_max
    """
    fpath = Path(fpath)
    if print_filename:
        print(f"Reading file '{str(fpath)}'")
    if read_csv_args is None:
        read_csv_args = dict()
    if "sep" not in read_csv_args:
        read_csv_args.update(sep=r"\s+")
    if "names" not in read_csv_args:
        read_csv_args.update(names=("q", "I", "e"))
    if "index_col" not in read_csv_args:
        read_csv_args.update(index_col=False)
    # print("f_read_data, read_csv_args:", read_csv_args) # for debugging

    file_ext = fpath.suffix
    if file_ext.lower() == ".pdh":  # for PDH files
        nrows = pd.read_csv(
            fpath,
            skiprows=2,
            nrows=1,
            usecols=[
                0,
            ],
            sep=r"\s+",
            header=None,
        ).values[0, 0]
        read_csv_args.update(skiprows=5, nrows=nrows)
    df = pd.read_csv(fpath, **read_csv_args)

    # select q-range
    if q_range is not None:
        q_min, q_max = q_range
        df = df[(df.q > q_min) & (df.q < q_max)]

    filename = fpath.stem.split("[")[0]
    return df, filename


readPDH = readdata


def convertValue(val):
    val = val.strip()
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            pass
    return val


def xmlPDHToDict(root):
    result = {}
    stack = [(root, result)]
    while stack:
        elem, parentCont = stack.pop()
        elemCont = {}
        idx = -1
        key = elem.attrib.pop("key", None)
        if (  # get a unique key, the key can occur in multiple groups in PDH
            key is not None and elem.tag == "group" and elem.attrib.get("id", None) is not None
        ):
            key = elem.attrib.pop("id")
        if (  # skip empty elements with a key only early
            not len(list(elem))
            and not len(elem.attrib)
            and not (elem.text and len(elem.text.strip()))
        ):
            continue
        if elem.tag == "list":
            elemCont = []
        else:  # add attributes & values to dict
            # Attach text, if any
            if elem.text and len(elem.text.strip()):
                if elem.tag in ("value", "reference"):
                    elemCont["value"] = convertValue(elem.text)
                else:
                    elemCont["#text"] = convertValue(elem.text)
            # Attach attributes, if any
            if elem.attrib:
                elemCont.update(
                    {k: convertValue(v) for k, v in elem.attrib.items() if len(v.strip())}
                )
            if key == "unit" and "value" in elemCont:  # fix some units
                elemCont["value"] = elemCont["value"].replace("_", "")
            if "unit" in elemCont:
                elemCont["unit"] = elemCont["unit"].replace("_", "")
            # reduce the extracted dict&attributes
            idx = elemCont.get("index", -1)  # insert last/append if no index given
            value = elemCont.get("value", None)
            if value is not None and (
                len(elemCont) == 1 or (len(elemCont) == 2 and "index" in elemCont)
            ):
                elemCont = value  # contains value only
        parentKey = elem.tag
        if key is not None and parentKey in ("list", "value", "group"):
            # skip one level in hierarchy for these generic containers
            parentKey = key
            key = None
        try:
            if isinstance(parentCont, list):
                parentCont.insert(idx, elemCont)
            elif parentKey not in parentCont:  # add as new list
                if key is None:  # make a list
                    parentCont[parentKey] = elemCont
                else:  # have a key
                    parentCont[parentKey] = {key: elemCont}
            else:  # parentKey exists already
                if not isinstance(parentCont[parentKey], list) and not isinstance(
                    parentCont[parentKey], dict
                ):
                    # if its a plain value before, make a list out of it and append in next step
                    parentCont[parentKey] = [parentCont[parentKey]]
                if isinstance(parentCont[parentKey], list):
                    parentCont[parentKey].append(elemCont)
                elif key is not None:
                    parentCont[parentKey].update({key: elemCont})
                else:  # key is None
                    parentCont[parentKey].update(elemCont)
        except AttributeError:
            raise
        # reversed for correct order
        stack += [(child, elemCont) for child in reversed(list(elem))]
    # fix some entry values, weird Anton Paar PDH format
    try:
        oldts = result["fileinfo"]["parameter"]["DateTime"]["value"]
        # timestamp seems to be based on around 2009-01-01 (a day give or take)
        delta = (39 * 365 + 10) * 24 * 3600
        # make it compatible to datetime.datetime routines
        result["fileinfo"]["parameter"]["DateTime"]["value"] = oldts + delta
    except KeyError:
        pass
    return result


def readPDHmeta(pathPDH):
    """Reads the XML metadata at the end of a .PDH file to a Python dict."""
    pathPDH = Path(pathPDH)
    if pathPDH.suffix.lower() != ".pdh":
        warnings.warn("readPDHmeta() supports .pdh files only!")
        return  # for PDH files
    lines = ""
    with open(pathPDH) as fd:
        lines = fd.readlines()
    nrows = int(lines[2].split()[0])
    xml = "".join(lines[nrows + 5 :])
    return xmlPDHToDict(et.fromstring(xml))


def readSSF(pathSSF):
    """Reads the SAXSquant session file *pathSSF* (.SSF) to a Python dict."""
    pathSSF = Path(pathSSF)
    if pathSSF.suffix.lower() != ".ssf":
        warnings.warn("readSession() supports .ssf files only!")
        return  # for PDH files
    data = ""
    with open(pathSSF, encoding="utf-8-sig") as fd:
        data = fd.read()
    return xmlPDHToDict(et.fromstring(data))


def readSSFZ(pathSSFZ):
    """Extracts and reads the SAXSquant session file (.SSF) to a Python dict.
    The .SSF is embedded in the .SSFZ provided by *pathSSFZ*."""
    assert pathSSFZ.is_file()
    # unpack the SSFZ to a temporary dir
    data = None
    with tempfile.TemporaryDirectory() as tempdir:
        with zipfile.ZipFile(pathSSFZ, "r") as zipfd:
            zipfd.extractall(tempdir)
        # read the session metadata from the extracted SSF file
        pathSSF = next(Path(tempdir).glob("*.ssf"))
        assert pathSSF.is_file()
        data = readSSF(pathSSF)
    return data
