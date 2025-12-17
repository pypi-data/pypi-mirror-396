import pytest

import tempfile
import pathlib
import pandas
import numpy

from utils.files import file as fl, pickle
from . import somethingThatDoesntExist


def test_directory_exists() -> None:
    # proper existing directory
    dir1 = fl.directoryExists("./data/")
    assert dir1 is not None

    # path that does not exist
    dir2 = fl.directoryExists(f"./data/{somethingThatDoesntExist}")
    assert dir2 is None

    # path that is a file
    dir3 = fl.directoryExists(f"./data/systems-528n.pkl")
    assert dir3 is None


def test_file_exists() -> None:
    # proper existing file
    file1 = fl.fileExists("./data/systems-528n.pkl")
    assert file1 is not None

    # path that does not exist
    file2 = fl.fileExists(f"./data/{somethingThatDoesntExist}")
    assert file2 is None

    # path that is a directory
    file3 = fl.fileExists(f"./data/")
    assert file3 is None


def test_open_pickle_as_pandas_table_fail(
    somethingThatDoesntExist: str
) -> None:
    # openning a non-existent path
    with pytest.raises(
        ValueError,
        match=r"^Provided path to \[.*\] seems to be wrong$"
    ):
        tbl = pickle.openPickleAsPandasTable(somethingThatDoesntExist)
    # openning a folder instead of a file
    # (no longer raises this one)
    # with pytest.raises(ValueError, match=r"^The path \[.*\] is not a file$"):
    #     tbl = pickle.openPickleAsPandasTable(".")


def test_open_pickle_as_pandas_table() -> None:
    tbl = pickle.openPickleAsPandasTable("./data/systems-528n.pkl")
    assert tbl.index[0] == "AU Mic b"
    assert tbl.index[3] == "CoRoT-24 c"


def test_save_pandas_table_as_pickle() -> None:
    rng = numpy.random.default_rng()
    tbl = pandas.DataFrame(
        rng.integers(0, 20, size=(3, 5)),
        index=[1, 2, 3],
        columns=["a", "b", "c", "d", "e"]
    )
    with tempfile.TemporaryDirectory() as tempDir:
        tempFilePath = pathlib.Path(tempDir) / "some.pkl"
        pickle.savePandasTableAsPickle(tbl, tempFilePath)
        assert tempFilePath.exists()
        with pytest.raises(
            ValueError, match=r"^The \[.*\] file already exists$"
        ):
            pickle.savePandasTableAsPickle(tbl, tempFilePath)


def test_merge_pickles_return_as_pandas() -> None:
    tbl = pickle.mergePickles(
        "./data/merge-pickles/",
        None
    )
    assert isinstance(tbl, pandas.DataFrame)
    assert len(tbl) == 6


def test_merge_pickles_save_to_file() -> None:
    with tempfile.TemporaryDirectory() as tempDir:
        tempFilePath = pathlib.Path(tempDir) / "merged.pkl"
        rslt = pickle.mergePickles(
            "./data/merge-pickles/",
            tempFilePath
        )
        assert isinstance(rslt, type(None))
        assert tempFilePath.exists()
