"""
Common file operations.
"""

import pathlib

from ..logs.log import logger

from typing import Union, Optional


def directoryExists(
    directoryCandidate: Union[str, pathlib.Path]
) -> Optional[pathlib.Path]:
    """
    Check whether provided path exists and is a directory.

    Example:

    ``` py
    from phab.utils.files import file as fl

    someDirectoryPath: str = "/path/to/some/directory/"
    someDirectory = fl.directoryExists(someDirectoryPath)
    if someDirectory is None:
        raise ValueError(
            f"Provided path to [{someDirectoryPath}] seems to be wrong"
        )
    else:
        # now you can do something with that directory
    ```
    """
    directoryPath: pathlib.Path = pathlib.Path()

    if isinstance(directoryCandidate, str):
        directoryPath = pathlib.Path(directoryCandidate)
    elif isinstance(directoryCandidate, pathlib.Path):
        directoryPath = directoryCandidate
    else:
        msg = " ".join((
            "Unsupported type of the directory path:",
            type(directoryCandidate)
        ))
        logger.error(msg)
        # raise ValueError(msg)
        return None

    if not directoryPath.exists():
        msg = f"The path [{directoryPath}] does not exist"
        logger.error(msg)
        # raise ValueError(msg)
        return None

    if not directoryPath.is_dir():
        msg = f"The path [{directoryPath}] is not a directory"
        logger.error(msg)
        # raise ValueError(msg)
        return None

    return directoryPath


def fileExists(
    fileCandidate: Union[str, pathlib.Path]
) -> Optional[pathlib.Path]:
    """
    Check whether provided path exists and is a file.

    Example:

    ``` py
    from phab.utils.files import file as fl

    someFilePath: str = "/path/to/some.file"
    someFile = fl.fileExists(someFilePath)
    if someFile is None:
        raise ValueError(
            f"Provided path to [{someFilePath}] seems to be wrong"
        )
    else:
        # now you can do something with that file
    ```
    """
    filePath: pathlib.Path = pathlib.Path()

    if isinstance(fileCandidate, str):
        filePath = pathlib.Path(fileCandidate)
    elif isinstance(fileCandidate, pathlib.Path):
        filePath = fileCandidate
    else:
        msg = " ".join((
            "Unsupported type of the file path:",
            type(fileCandidate)
        ))
        logger.error(msg)
        # raise ValueError(msg)
        return None

    if not filePath.exists():
        msg = f"The path [{filePath}] does not exist"
        logger.error(msg)
        # raise ValueError(msg)
        return None

    if not filePath.is_file():
        msg = f"The path [{filePath}] is not a file"
        logger.error(msg)
        # raise ValueError(msg)
        return None

    return filePath
