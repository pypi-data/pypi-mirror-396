"""
Mathematical statistics.
"""

import numpy
import pandas

from typing import List, Hashable

from ..logs.log import logger


def findOutliers(
    srs: pandas.Series,
    sigma: int = 3,
    joinNeighbouringOutliers: bool = True,
    howManyCountAsNeighbours: int = 3
) -> pandas.Series:
    """
    Find outliers in the array and return the mask where outliers
    are marked with `True`. NaNs and INFs, if any, do not count
    as outliers.

    If `joinNeighbouringOutliers` is `True`, then non-outlier values
    between neighbouring outliers will be marked as outliers too. The same
    goes for starting/ending elements, if they are close enough to an outlier.

    Example with `joinNeighbouringOutliers` set to `True`:

    ``` py
    import pandas
    import numpy

    from phab.utils.math import statistics

    srs = pandas.Series(
        [4, 111, 4, 4, 5, 6, numpy.inf, 2, 4, 4, numpy.nan, 1, 1e15, 4, 3, 3, 101, 2, 4, 3]
    )

    markedOutliers = statistics.findOutliers(
        srs,
        sigma=3,
        joinNeighbouringOutliers=True,
        howManyCountAsNeighbours=3
    )

    for i, v in srs.items():
        if markedOutliers[i] == True:
            print(f"{v} - outlier")
        else:
            print(f"{v} - regular")
    # 4.0 - outlier
    # 111.0 - outlier
    # 4.0 - regular
    # 4.0 - regular
    # 5.0 - regular
    # 6.0 - regular
    # inf - regular
    # 2.0 - regular
    # 4.0 - regular
    # 4.0 - regular
    # nan - regular
    # 1.0 - regular
    # 1000000000000000.0 - outlier
    # 4.0 - outlier
    # 3.0 - outlier
    # 3.0 - outlier
    # 101.0 - outlier
    # 2.0 - outlier
    # 4.0 - outlier
    # 3.0 - outlier
    ```

    Example with `joinNeighbouringOutliers` set to `False`:

    ``` py
    # ...

    markedOutliers = statistics.findOutliers(
        srs,
        sigma=3,
        joinNeighbouringOutliers=False,
        howManyCountAsNeighbours=3
    )

    for i, v in srs.items():
        if markedOutliers[i] == True:
            print(f"{v} - outlier")
        else:
            print(f"{v} - regular")
    # 4.0 - regular
    # 111.0 - outlier
    # 4.0 - regular
    # 4.0 - regular
    # 5.0 - regular
    # 6.0 - regular
    # inf - regular
    # 2.0 - regular
    # 4.0 - regular
    # 4.0 - regular
    # nan - regular
    # 1.0 - regular
    # 1000000000000000.0 - outlier
    # 4.0 - regular
    # 3.0 - regular
    # 3.0 - regular
    # 101.0 - outlier
    # 2.0 - regular
    # 4.0 - regular
    # 3.0 - regular
    ```
    """
    # tbl = pandas.DataFrame({"vls": srs})
    tbl = pandas.DataFrame(srs)

    # find NaNs/INFs
    tbl["finite"] = numpy.isfinite(srs)

    # every element is an outlier by default
    tbl["outliers"] = numpy.ones(len(tbl.index), dtype=bool)

    # NaNs and INFs are not outliers
    # print(tbl["finite"].loc[lambda x: x == False].index)
    tbl.loc[
        tbl["finite"] == False,
        "outliers"
    ] = False

    tableFinite = tbl[tbl["finite"] == True].iloc[:, 0]

    med = numpy.median(tableFinite.values)  # type:ignore[arg-type] # ya hz
    sig = 1.48 * numpy.median(numpy.abs(tableFinite - med))  # type:ignore[operator] # ya hz

    for i, v in tableFinite.items():
        if v > med - sigma * sig:
            tbl.at[i, "outliers"] = False

    for i, v in tableFinite.items():
        if v >= med + sigma * sig:
            tbl.at[i, "outliers"] = True

    if not joinNeighbouringOutliers:
        # the entire table with all columns (the original and two new ones,
        # "finite" and "ouliers")
        # return tbl
        #
        # or just two columns: first one with the values and "outliers"
        # return tbl.iloc[:,0:3:2]
        #
        # or just the outliers
        return tbl["outliers"]
        #
        # or just the "outliers" that are True, because it's a waste to pass
        # around all the values, let alone the entire table
        # return tbl[tbl["outliers"] == True]["outliers"]
    else:
        outlrs: pandas.Series = tbl["outliers"].copy()
        elementsSincePreviousOutlier: int = 0
        #
        # later we might want to have the number of neighbours to scale
        # with the list length, but for now it is passed as a fixed
        # number in the `howManyCountAsNeighbours` argument of the function
        # howManyCountAsNeighbours = round(len(outlrs.index) / 10)
        #
        # intuitively it should be `False`, but we need to account
        # for possible neighbours from the very start
        countingSincePreviousOutlier: bool = True
        potentialNeighbourOutliers: List[Hashable] = []
        for i, v in outlrs.items():
            if v == True:
                if countingSincePreviousOutlier:
                    # make all the previous elements to be outliers too
                    for pno in potentialNeighbourOutliers:
                        outlrs[pno] = True
                    potentialNeighbourOutliers = []
                    elementsSincePreviousOutlier = 0
                else:
                    countingSincePreviousOutlier = True
            else:
                if countingSincePreviousOutlier:
                    elementsSincePreviousOutlier += 1
                    if elementsSincePreviousOutlier > howManyCountAsNeighbours:
                        elementsSincePreviousOutlier = 0
                        countingSincePreviousOutlier = False
                        potentialNeighbourOutliers = []
                    else:
                        potentialNeighbourOutliers.append(i)
        # if there are some pending potential neighbour outliers
        # after we finished iterating the list, make them outliers
        if len(potentialNeighbourOutliers) > 0:
            for pno in potentialNeighbourOutliers:
                outlrs[pno] = True
            potentialNeighbourOutliers = []
        return outlrs
