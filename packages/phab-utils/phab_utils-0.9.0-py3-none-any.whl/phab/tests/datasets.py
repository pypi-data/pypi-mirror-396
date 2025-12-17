import pytest

import pandas
import numpy

from utils.datasets import pandas as pnd


def test_merge_pandas() -> None:
    rng = numpy.random.default_rng()
    vals = rng.integers(0, 20, size=(3, 5))
    clmns = ["a", "b", "c", "d", "e"]

    frames = [
        pandas.DataFrame(vals, index=[1, 2, 3], columns=clmns),
        pandas.DataFrame(vals, index=[4, 5, 6], columns=clmns),
        pandas.DataFrame(vals, index=[7, 8, 9], columns=clmns)
    ]

    tbl = pnd.mergeTables(frames)

    assert isinstance(tbl, pandas.DataFrame)
    assert len(tbl) == 9


def test_deduplicate_table() -> None:
    tbl = pandas.DataFrame(
        [
            [1, 2, 3],
            [4, 5, 6],
            [1, 2, 3],
            [7, 8, 9],
            [4, 5, 6],
            [3, 1, 2],
            [4, 5, 6]
        ],
        index=[1, 2, 3, 4, 5, 6, 7],
        columns=["a", "b", "c"]
    )

    deduplicatedTable = pnd.deduplicateTable(tbl, True)
    assert isinstance(deduplicatedTable, pandas.DataFrame)
    assert len(deduplicatedTable) == 4
    assert deduplicatedTable.at[1, "a"] == 1
    assert deduplicatedTable.at[6, "c"] == 2

    duplicateRows = pnd.deduplicateTable(tbl, False)
    assert isinstance(duplicateRows, pandas.DataFrame)
    assert len(duplicateRows) == 3
    assert duplicateRows.at[7, "b"] == 5


def test_drop_meaningless_rows() -> None:
    tbl = pandas.DataFrame(
        {
            "a": [0, 0, 23, 2, 0, 0, 0, 19, 1, 0, 0],
            12.3: [0, 0, 2, 3, 0, 0, 0, 4, 3, 0, 0],
            "c": [0, 0, 65, 34, 0, 0, 0, 45, 2, 0, 0],
            "d": [0, 0, 33, 7, 0, 0, 0, 64, 33, 0, 0],
            "e": [0, 0, 0, 45, 0, 0, 0, 12, 11, 0, 0]
        },
        index=[4, 21, 30, 57, 59, 62, 71, 80, 81, 102, 126]
    )

    rez = pnd.dropMeaninglessRows(tbl)
    assert isinstance(rez, pandas.DataFrame)
    assert len(rez) == 9

    rez = pnd.dropMeaninglessRows(tbl, 12.3)
    assert isinstance(rez, pandas.DataFrame)
    assert len(rez) == 9

    rez = pnd.dropMeaninglessRows(tbl, "e")
    assert isinstance(rez, pandas.DataFrame)
    assert len(rez) == 8

    invalidColumnName = "ololo"
    with pytest.raises(
        ValueError,
        match=rf"^Table has no column \[{invalidColumnName}\]$"
    ):
        rez = pnd.dropMeaninglessRows(tbl, invalidColumnName)
