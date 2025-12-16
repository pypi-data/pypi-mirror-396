# -*- coding: utf-8 -*-
# analysis.py

import numpy as np


# from https://stackoverflow.com/a/22357811
# and https://github.com/joferkington/oost_paper_code/blob/master/utilities.py#L167
# (code with MIT License)
def getModZScore(points):
    """
    Returns a boolean array with True if points are outliers and False
    otherwise.
    **Note**:
    Similar to https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.zscore.html
    but uses the median instead of the mean.

    :param points: An numobservations by numdimensions array of observations
    :param thresh: The modified z-score to use as a threshold. Observations with
        a modified z-score (based on the median absolute deviation) greater
        than this value will be classified as outliers.

    Returns
    -------
    mask: numpy array
        A numobservations-length boolean array.

    References
    ----------
    Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
    Handle Outliers", The ASQC Basic References in Quality Control:
    Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    if len(points.shape) == 1:
        points = points[:, None]
    median = np.median(points, axis=0)
    diff = np.sqrt(np.sum((points - median) ** 2, axis=-1))
    med_abs_deviation = np.median(diff)

    # scale being the inverse of the standard normal quantile function at 0.75,
    # which is approximately 0.67449, see also:
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.median_abs_deviation.html
    # modified_z_score = 0.6745 * diff / med_abs_deviation
    # let this indicator be =1 for the same data, makes it more intuitive to understand
    modified_z_score = diff / med_abs_deviation

    return modified_z_score
