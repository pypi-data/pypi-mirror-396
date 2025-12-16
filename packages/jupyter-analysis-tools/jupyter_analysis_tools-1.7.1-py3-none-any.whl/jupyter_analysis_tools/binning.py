#!/usr/bin/env python
# -*- coding: utf-8 -*-
# binning.py

"""
Overview
========
1D rebinning.
Should take input file, read, rebin and write.
Rebins to log bins.
"""

# __author__ = "Brian R. Pauw"
# __contact__ = "brian@stack.nl"
# __license__ = "GPLv3+"
# __date__ = "2015/01/09"
# __status__ = "beta"

import argparse
import itertools
import os
import sys

import numpy as np
import pandas
from numpy import argsort, log10, reshape, shape, size, sqrt, zeros


def argparser():
    parser = argparse.ArgumentParser(
        description="""
            Re-binning function, reads three-column ASCII input files,
            and outputs re-binned three-column ASCII files"""
    )
    # binning options
    parser.add_argument("-n", "--numBins", type=int, default=50, help="Number of bins to use")
    parser.add_argument(
        "-q",
        "--qMin",
        type=float,
        default=0.0,
        help="Minimum Q to clip from original data",
    )
    parser.add_argument(
        "-Q",
        "--qMax",
        type=float,
        default=np.inf,
        help="Minimum Q to clip from original data",
    )
    parser.add_argument(
        "-e",
        "--minE",
        type=float,
        default=0.01,
        help="Minimum error is at least this times intensity value.",
    )
    parser.add_argument(
        "-s",
        "--scaling",
        type=str,
        action="store",
        default="logarithmic",
        help="q-axis scaling for binning, can be linear or logarithmic",
    )
    # csv / datafile options
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        action="store",
        default=",",
        help="Delimiter in original file. '\\t' is tab. (with quotes)",
    )
    parser.add_argument(
        "-H",
        "--headerLines",
        type=int,
        default=0,
        help="Number of header lines to skip",
    )
    parser.add_argument(
        "-D",
        "--outputDelimiter",
        type=str,
        action="store",
        default=None,
        help="Delimiter in final file (defaults to input delimiter)",
    )
    parser.add_argument(
        "-c",
        "--cleanEmpty",
        action="store_true",
        default=True,
        help="Removes empty bins before writing",
    )
    parser.add_argument(
        "-i",
        "--iScale",
        type=float,
        default=1.0,
        help="Intensity (and error) scaled by this factor on output.",
    )
    # program options
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Be verbose about the steps",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Do not save output files, test run only",
    )
    parser.add_argument(
        "-N",
        "--noBin",
        action="store_true",
        help="Do not bin, just input -> output (for translation and scaling)",
    )
    parser.add_argument(
        "fnames",
        nargs="*",
        metavar="FILENAME",
        action="store",
        help="One or more data files to rebin",
    )
    # show help if no files were provided, no arguments at all
    args = parser.parse_args()
    if len(args.fnames):
        return args
    parser.print_help(sys.stderr)
    sys.exit(1)


class reBin(object):
    """all kinds of binning-related functions"""

    # set defaults for file reading:
    pandasArgs = {
        "skipinitialspace": True,
        "skip_blank_lines": True,
        "engine": "python",
        "header": None,
    }
    # set defaults for kwargs, in case this is not called from command line:
    reBinArgs = {
        "delimiter": ";",
        "outputDelimiter": ";",
        "headerLines": 0,
        "fnames": "",
        "verbose": False,
        "qMin": -np.inf,
        "qMax": np.inf,
        "numBins": 100,
        "scaling": "logarithmic",
        "cleanEmpty": False,
        "minE": 0.01,
        "noBin": False,
    }

    def __init__(self, **kwargs):
        # process defaults:
        for kw in self.reBinArgs:
            setattr(self, kw, self.reBinArgs[kw])
        # process kwargs:
        if "verbose" in kwargs:
            self.verbose = kwargs.pop("verbose")
        for kw in kwargs:
            if self.verbose:
                print("Processing input argument {}: {}".format(kw, kwargs[kw]))
            setattr(self, kw, kwargs[kw])

        # process delimiter options
        # decode no longer necessary in python 3
        if sys.version_info <= (3, 0):
            self.delimiter = self.delimiter.decode("string-escape")
        if self.outputDelimiter is None:
            self.outputDelimiter = self.delimiter
        else:
            if sys.version_info <= (3, 0):
                self.outputDelimiter = self.outputDelimiter.decode("string-escape")

        self.pandasArgs.update({"delimiter": self.delimiter, "skiprows": self.headerLines})
        # process files individually:
        for filename in self.fnames:
            self.readFile(filename)
            self.validate()
            self.defineBinEdges()
            self.binning1D()
            if self.cleanEmpty:
                # removes bins with no intensity or error
                self.cleanup()

            if not self.test:
                # generate output file name
                ofname = self.outputFilename(filename)
                # write binned data to file name
                self.writeFile(ofname)

    def cleanup(self):
        # removes unwanted bin values
        # cannot use lists, because:
        # http://unspecified.wordpress.com/2009/02/12/thou-shalt-not-modify-a-list-during-iteration
        validi = True ^ np.isnan(self.IBin)
        validi[np.argwhere(self.binMask > 0)] = False
        self.QBin = self.QBin[validi]
        self.IBin = self.IBin[validi]
        self.EBin = self.EBin[validi]
        self.QEBin = self.QEBin[validi]
        if self.verbose:
            print("valid bins: {} of {}".format(validi.sum(), len(validi)))

    def outputFilename(self, filename):
        """returns an output filename based on the input filename"""
        of = filename.strip()
        # split at extension
        ob, oe = of.rsplit(".", 1)
        # add rebin tag and reassemble
        ofname = "{}_reBin.{}".format(ob, oe)
        if self.verbose:
            print("output filename: {}".format(ofname))
        return ofname

    def readFile(self, filename):
        if self.verbose:
            print("reading file: {} with settings: {}".format(filename, self.pandasArgs))
        dval = pandas.read_csv(filename, **self.pandasArgs).values
        assert isinstance(dval, np.ndarray)  # no problems reading?
        assert size(dval, axis=1) >= 3  # Q, I and E can be extracted
        if self.verbose:
            print("data read: {}".format(dval))
        self.Q = np.float32(dval[:, 0])
        self.I = np.float32(dval[:, 1])
        self.E = np.maximum(self.minE * self.I, np.float32(dval[:, 2]))
        numChanged = (self.minE * self.I > dval[:, 2]).sum()
        if self.verbose:
            print(
                "Minimum uncertainty set for {} out of {} ({} %) datapoints".format(
                    numChanged, size(self.Q), 100.0 * numChanged / size(self.Q)
                )
            )

    # writer modified from imp2/modules/Write1D
    def writeFile(self, ofname, hstrs=None, append=False):
        sep = self.outputDelimiter
        # scale if necessary
        iterData = itertools.zip_longest(
            self.QBin,
            self.IBin * float(self.iScale),
            self.EBin * float(self.iScale),
        )

        def writeLine(filename, line=None, append=True):
            if append:
                openarg = "a"
            else:
                openarg = "w"
            with open(filename, openarg) as fh:
                if isinstance(line, str):
                    fh.write(line)
                else:
                    # iterable object containing multiple lines
                    fh.writelines(line)

        # truncate file if exists (i.e. discard)
        if os.path.exists(ofname) and (not append):
            os.remove(ofname)

        # write header and data:
        if hstrs is not None:
            writeLine(ofname, hstrs)

        # store in file
        moreData = True
        while moreData:
            try:
                # generate formatted datastring containing column data
                wstr = sep.join(["{}".format(k) for k in next(iterData)]) + "\n"
            except StopIteration:
                # end of data reached
                moreData = False
                break
            writeLine(ofname, wstr)

    def validate(self):
        """Applies limits to the data"""
        mask = zeros(shape(self.Q), dtype="bool")
        # appy integration limits:
        iind = np.array(((self.Q < self.qMin) + (self.Q > self.qMax)), dtype=bool)
        mask[iind] = True

        # define binning limits
        (qmin, qmax) = (
            np.abs(self.Q[True ^ mask]).min(),
            np.abs(self.Q[True ^ mask]).max(),
        )
        self.iqMin = np.maximum(qmin, self.qMin)
        self.iqMax = np.minimum(qmax, self.qMax)
        self.Q = self.Q[True ^ mask]
        self.I = self.I[True ^ mask]
        self.E = self.E[True ^ mask]
        if self.verbose:
            print(
                "data Q-range: {}, integration Q-range: {}, masked: {} of {} ({}%)".format(
                    (self.Q.min(), self.Q.max()),
                    (self.iqMin, self.iqMax),
                    mask.sum(),
                    self.Q.size,
                    mask.sum() / self.Q.size,
                )
            )

    def defineBinEdges(self):
        """defines binning edges"""
        # define bin edges
        if self.scaling.lower() in ("linear", "lin"):
            qEdges = np.linspace(self.iqMin, self.iqMax, self.numBins + 1)
        else:
            qEdges = np.logspace(log10(self.iqMin), log10(self.iqMax), self.numBins + 1)
        self.qEdges = qEdges
        if self.verbose:
            print("Bin edges used: {}".format(self.qEdges))

    def binning1D(self, qError=None):
        """An unweighted binning routine.
        imp-version of binning, taking q-bin edges in which binning takes place,
        and calculates the mean q uncertainty in the bin as well from the relative
        Q uncertainties provided.

        The intensities are sorted across bins of equal size. If provided error
        is empty, the standard deviation of the intensities in the bins is
        computed.
        """
        # no binning requested, just input -> output
        if self.noBin:
            self.QBin = self.Q.copy()
            self.IBin = self.I.copy()
            self.EBin = self.E.copy()
            self.QEBin = np.zeros(np.shape(self.I))
            return

        # set values:
        q = self.Q.copy()
        intensity = self.I.copy()
        error = self.E.copy()
        numBins = self.numBins
        qEdges = self.qEdges

        # flatten q, intensity and error
        q = reshape(q, size(q))
        intensity = reshape(intensity, size(intensity))

        # sort q, let intensity and error follow sort
        sortInd = argsort(q, axis=None)
        q = q[sortInd]
        intensity = intensity[sortInd]

        # initialise storage:
        numBins = len(qEdges) - 1
        ibin = zeros(numBins)
        qbin = zeros(numBins)
        sdbin = zeros(numBins)
        sebin = zeros(numBins)
        qebin = zeros(numBins)
        binMask = zeros(numBins)  # set one for masked bin values
        if error is not None:
            error = reshape(error, size(error))
            error = error[sortInd]
        if qError is not None:
            qError = reshape(qError, size(qError))
            qError = qError[sortInd]

        # now we can fill the bins
        for bini in range(numBins):
            # limit ourselves to only the bits we're interested in:
            limMask = (q >= qEdges[bini]) & (q <= qEdges[bini + 1])

            iToBin = intensity[limMask]
            # sum the intensities in one bin and normalize by number of pixels
            if limMask.sum() == 0:
                # no pixels in bin
                (ibin[bini], sebin[bini], qebin[bini], qbin[bini]) = (
                    None,
                    None,
                    None,
                    None,
                )
                binMask[bini] = 1
                continue

            elif limMask.sum() == 1:
                ibin[bini] = iToBin.mean()
                qbin[bini] = q[limMask].mean()
                if error is not None:
                    sebin[bini] = error[limMask]
                if qError is not None:
                    qebin[bini] = qError[limMask]

            else:
                ibin[bini] = iToBin.mean()
                qbin[bini] = q[limMask].mean()
                if error is not None:
                    sebin[bini] = np.sqrt((error[limMask] ** 2).sum()) / limMask.sum()
                # now we deal with the Errors:
                # calculate the standard deviation of the intensity in the bin
                # according to the definition of sample-standard deviation
                sdbin = iToBin.std(ddof=1)
                # what we want is to have the "standard error of the mean":
                sdbin = sdbin / sqrt(1.0 * np.size(iToBin))
                # maximum between standard error and Poisson statistics
                sebin[bini] = np.maximum(sebin[bini], sdbin)
                # qebin is the mean error of the q-values in the bin, should
                # probably be superseded by the bin width
                qe = 0.0
                if qError is not None:
                    qe = np.sqrt((qError[limMask] ** 2).sum())
                # SSTD of q in bin:
                qs = np.std(q[limMask], ddof=1)  # sample standard deviation
                qebin[bini] = np.maximum(qe, qs)

        self.QBin = qbin.copy()
        self.IBin = ibin.copy()
        self.EBin = sebin.copy()
        self.QEBin = qebin.copy()
        self.binMask = binMask.copy()
        if self.verbose:
            print("qbin: {}".format(qbin))
            print("ibin: {}".format(ibin))
            print("sebin: {}".format(sebin))
            print("qebin: {}".format(qebin))
            print("binMask: {}".format(binMask))


if __name__ == "__main__":
    # process input arguments
    adict = argparser()
    # transmogrify into kwargs object
    adict = vars(adict)
    # run the reBin program
    reBin(**adict)
