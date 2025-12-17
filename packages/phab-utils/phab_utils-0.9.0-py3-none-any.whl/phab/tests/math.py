import pytest
import numpy
import pandas

from utils.math import statistics


@pytest.mark.parametrize(
    "srs",
    [
        [4, 111, 4, 4, 5, 6, numpy.inf, 2, 4, 4, numpy.nan, 1, 1e15, 4, 3, 3, 101, 2, 4, 3],
        [4, 111, 4, 3, 4, 5, numpy.nan, 4, 2, 4, numpy.inf, 1, 1e14, 3, 3, 4, 102, 3, 2, 4]
    ]
)
def test_find_outliers(srs: pandas.Series) -> None:
    markedOutliers = statistics.findOutliers(srs, 3, True, 3)
    assert numpy.array_equal(
        markedOutliers.values,  # type:ignore[arg-type] # ya hz
        numpy.array(
            [
                True,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True
            ]
        )
    )

    markedOutliers = statistics.findOutliers(srs, 3, False, 3)
    assert numpy.array_equal(
        markedOutliers.values,  # type:ignore[arg-type] # ya hz
        numpy.array(
            [
                False,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
                True,
                False,
                False,
                False
            ]
        )
    )
