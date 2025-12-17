"""
Data processing with [Pandas](https://pandas.pydata.org) tables.

It is important to import this module with an alias, for example:

``` py
from phab.utils.datasets import pandas as pnd
```

Otherwise it will collide with the `pandas` module itself.
"""

import pandas

from typing import Optional, List, Union

from ..logs.log import logger


def mergeTables(frames: List[pandas.DataFrame]) -> pandas.DataFrame:
    """
    Merge (*concatenate*) several tables into one. Sorts the index
    and verifies integrity (*will raise an exception
    on duplicate/overlapping index*).

    Example:

    ``` py
    from phab.utils.datasets import pandas as pnd

    frames = []
    # ...
    # frames.append(someTbl1)
    # frames.append(someTbl2)
    # frames.append(someTbl3)
    # ...
    tbl = pnd.mergeTables(frames)
    #print(tbl.head(15))
    ```
    """

    mergedTable = pandas.concat(
        frames,
        verify_integrity=True
    ).sort_index()

    logger.debug(f"Total records in the resulting table: {len(mergedTable)}")
    # logger.debug("Preview of the first rows:")
    # logger.debug(mergedTable.head(15))

    return mergedTable


def deduplicateTable(
    tbl: pandas.DataFrame,
    returnUniques: bool = True
) -> pandas.DataFrame:
    """
    Find duplicate rows in the table:

    - with `returnUniques` set to `True`, returns a table without duplicate
    rows. The first occurrence is always considered to be unique
    in the resulting table, even if it has duplicates;
    - with `returnUniques` set to `False` returns only duplicate rows.

    Example:

    ``` py
    import pandas
    from phab.utils.datasets import pandas as pnd

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
    #print(deduplicatedTable)
    #    a  b  c
    # 1  1  2  3
    # 2  4  5  6
    # 4  7  8  9
    # 6  3  1  2
    #print(deduplicatedTable.index.values)
    # [1 2 4 6]

    duplicateRows = pnd.deduplicateTable(tbl, False)
    #print(duplicateRows)
    #    a  b  c
    # 3  1  2  3
    # 5  4  5  6
    # 7  4  5  6
    #print(duplicateRows.index.values)
    # [3 5 7]
    ```
    """
    duplicateRows = tbl.duplicated()
    duplicateRows = duplicateRows[duplicateRows].index  # type:ignore[assignment] # pizdit

    logger.debug(f"Unique rows count: {len(tbl) - len(duplicateRows)}")
    logger.debug(f"Duplicate rows count: {len(duplicateRows)}")
    # logger.debug(f"Indexes of duplicate rows: {duplicateRows}")

    duplicatesIndex = tbl.index.isin(duplicateRows)

    return (
        tbl[~duplicatesIndex] if returnUniques
        else tbl[duplicatesIndex]
    )


def dropMeaninglessRows(
    tbl: pandas.DataFrame,
    # the types in Union can be extended with whatever else is supported
    indicatorColumn: Optional[Union[str, int, float]] = None
) -> pandas.DataFrame:
    """
    Drop/remove meaningless rows from the table. For instance, if a table
    represents some event timeline, in which there are periods
    of activity/changes with periods of no changes between them, then it might
    make sense to drop those rows.

    At the same time, the meaningless rows just before and right after
    meaningful rows should are not dropped/removed, as they show points of time
    when activity started/ended. The first row is always kept and is used
    as a baseline for comparison.

    If `indicatorColumn` is provided, than that cell value from the baseline
    row is used to determine meaningless rows. Otherwise, the entire rows
    will be compared with the baseline one.

    Example:

    ``` py
    import pandas
    from phab.utils.datasets import pandas as pnd

    tbl = pandas.DataFrame(
        {
            "a": [0, 0, 23, 2,  0, 0, 0, 19, 1,  0, 0],
            "b": [0, 0, 2,  3,  0, 0, 0, 4,  3,  0, 0],
            "c": [0, 0, 65, 34, 0, 0, 0, 45, 2,  0, 0],
            "d": [0, 0, 33, 7,  0, 0, 0, 64, 33, 0, 0],
            "e": [0, 0, 0,  45, 0, 0, 0, 12, 11, 0, 0]
        },
        index=[4, 21, 30, 57, 59, 62, 71, 80, 81, 102, 126]
    )
    #print(tbl)
    #       a  b   c   d   e
    # 4     0  0   0   0   0
    # 21    0  0   0   0   0
    # 30   23  2  65  33   0
    # 57    2  3  34   7  45
    # 59    0  0   0   0   0
    # 62    0  0   0   0   0
    # 71    0  0   0   0   0
    # 80   19  4  45  64  12
    # 81    1  3   2  33  11
    # 102   0  0   0   0   0
    # 126   0  0   0   0   0

    rez = pnd.dropMeaninglessRows(tbl)
    #rez = pnd.dropMeaninglessRows(tbl, "a")
    #print(rez)
    #       a  b   c   d   e
    # 4     0  0   0   0   0
    # 21    0  0   0   0   0
    # 30   23  2  65  33   0
    # 57    2  3  34   7  45
    # 59    0  0   0   0   0
    # 71    0  0   0   0   0
    # 80   19  4  45  64  12
    # 81    1  3   2  33  11
    # 102   0  0   0   0   0

    rez = pnd.dropMeaninglessRows(tbl, "e")
    #print(rez)
    #       a  b   c   d   e
    # 4     0  0   0   0   0
    # 30   23  2  65  33   0
    # 57    2  3  34   7  45
    # 59    0  0   0   0   0
    # 71    0  0   0   0   0
    # 80   19  4  45  64  12
    # 81    1  3   2  33  11
    # 102   0  0   0   0   0
    ```
    """
    logger.debug(f"Original table:\n{tbl}")

    indexLength = len(tbl.index)
    rowsToDelete = []
    if indicatorColumn:  # it is enough to compare just one column values
        if indicatorColumn not in tbl.columns:
            raise ValueError(f"Table has no column [{indicatorColumn}]")
        for i in range(1, indexLength):  # first row is always kept
            if (
                tbl.at[tbl.index[i], indicatorColumn]
                == tbl.at[tbl.index[0], indicatorColumn]
                and
                tbl.at[tbl.index[i-1], indicatorColumn]
                == tbl.at[tbl.index[0], indicatorColumn]
            ):
                if i < indexLength - 1:  # not the last row
                    if (
                        tbl.at[tbl.index[i+1], indicatorColumn]
                        == tbl.at[tbl.index[0], indicatorColumn]
                    ):
                        rowsToDelete.append(tbl.index[i])
                else:
                    rowsToDelete.append(tbl.index[i])
    else:  # have to compare the entire rows
        for i in range(1, indexLength):  # first row is always kept
            if (
                tbl.iloc[i].equals(tbl.iloc[0])
                and
                tbl.iloc[i-1].equals(tbl.iloc[0])
            ):
                if i < indexLength - 1:  # not the last row
                    if tbl.iloc[i+1].equals(tbl.iloc[0]):
                        rowsToDelete.append(tbl.index[i])
                else:
                    rowsToDelete.append(tbl.index[i])

    logger.debug(f"Indexes of the rows to drop: {rowsToDelete}")

    tbl = tbl.drop(index=rowsToDelete)

    logger.debug(f"Table without meaningless rows:\n{tbl}")

    return tbl
