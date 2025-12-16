# -*- coding: utf-8 -*-
# __init__.py

__version__ = "1.7.1"

from .binning import reBin
from .git import checkRepo, isNBstripoutActivated, isNBstripoutInstalled, isRepo
from .plotting import createFigure, plotPDH
from .readdata import readdata, readPDH, readPDHmeta, readSSF, readSSFZ
from .utils import naturalKey, setLocaleUTF8
from .widgets import PathSelector, showBoolStatus

setLocaleUTF8()
