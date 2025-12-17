"""
Getting data from [SIMBAD](https://simbad.u-strasbg.fr/simbad/)
astronomical database.
"""

from astroquery.simbad import Simbad
from astroquery import __version__ as astroqueryVersion
import re

from typing import Optional, Any, List

from ..logs.log import logger
from ..databases import tap


def findIdentificatorFromAnotherCatalogue(
    starName: str,
    otherIDname: str,
    otherIDversion: Optional[str] = None,
    withoutIDprefix: bool = True
) -> Optional[str]:
    """
    Finds object identificator from a particular catalogue. SIMBAD returns
    a list of identificators prepended with the catalogue name, and this
    function finds the identificator for the specified catalogue and returns
    just the identificator. In addition to that, some catalogues have versions,
    so it is possible to specify which one if of interest.

    For instance, if you need to find the identificator for `TWA 20` star
    in `Gaia` catalog version `DR3`, then SIMBAD will return
    `Gaia DR3 6132146982868270976` value for it, out of which this function
    will extract `6132146982868270976` as the result.

    Example:

    ``` py
    from phab.utils.databases import simbad

    otherID = simbad.findIdentificatorFromAnotherCatalogue(
        "TWA 20",
        "gaia",
        "dr3"
    )
    print(otherID)
    ```
    """
    otherID = None

    otherIDs = Simbad.query_objectids(starName)
    if otherIDs is None:
        logger.warning(
            " ".join((
                "SIMBAD database doesn't have information",
                f"about [{starName}]"
            ))
        )
    else:
        logger.debug(f"Checking SIMBAD IDs for [{starName}]:")

        # before astroquery version 0.4.8 this table had
        # an upper-cased `ID` column key, but starting
        # with version 0.4.8 it is now lower-cased `id`
        #
        # https://github.com/astropy/astropy/issues/17695
        idColumnKey: str = "ID"
        # or compare `astroquery.__version__` with `0.4.7`
        if idColumnKey not in otherIDs.colnames:
            logger.debug(
                " ".join((
                    "There is no upper-cased [ID] key",
                    "in the resulting table, will try",
                    "with lower-cased [id] key"
                ))
            )
            idColumnKey = idColumnKey.lower()  # "id"
            if idColumnKey not in otherIDs.colnames:
                errorMsg = " ".join((
                    "SIMBAD results table has neither [ID]",
                    "nor [id] column"
                ))
                logger.error(errorMsg)
                if len(otherIDs.colnames) > 0:
                    logger.debug(
                        " ".join((
                            "Here are all the columns/keys",
                            "in this table:",
                            ", ".join(otherIDs.colnames)
                        ))
                    )
                else:
                    logger.debug(
                        " ".join((
                            "There are no columns/keys",
                            "in this table at all"
                        ))
                    )
                raise KeyError(errorMsg)

        for oid in otherIDs:
            idCandidate: str = oid[idColumnKey]
            logger.debug(f"- {idCandidate}")
            if otherIDname.lower() in idCandidate.lower():
                idToLookFor = (
                    f"{otherIDname} {otherIDversion}"
                    if otherIDversion else otherIDname
                )
                if idToLookFor.lower() in idCandidate.lower():
                    if withoutIDprefix:
                        prefixRE = re.compile(
                            rf"{idToLookFor}\s?",
                            re.IGNORECASE
                        )
                        otherID = prefixRE.sub("", idCandidate)
                    else:
                        otherID = idCandidate
                    break
    return otherID


def getObjectID(
    starName: str,
    fallbackToLikeInsteadOfEqual: bool = True,
    problematicIdentifiersPrefixes: List[str] = ["SZ"]
) -> Optional[int]:
    """
    Finds object identificator for
    [SIMBAD tables](http://simbad.cds.unistra.fr/simbad/tap/tapsearch.html).
    It is stored in the `oid` field of the `basic` table.

    The discovery process is to compare all the known object identificators
    with the `main_id` field value (*also from the `basic` table*). It is
    not clear, how exactly SIMBAD maintainers choose the main ID for an object,
    so one has to iterate through all the identificators known to SIMBAD.

    Due to the (*still unresolved?*) issue(s) in SIMBAD/CDS, some identifiers
    are problematic for querying with `main_id` - they return no results
    with explicit `=` in `WHERE` clause, but they do return results
    with `LIKE` instead of `=`, so a workaround/fallback had to be implemented
    for those. This workaround/fallback is enabled by default, and if you don't
    want these potentially incorrect results to "poison" you data, then you can
    disable it by setting `fallbackToLikeInsteadOfEqual` parameter to `False`.
    Also, the `problematicIdentifiersPrefixes` parameter limits the list
    of such problematic identifiers, and so far `SZ  *` pattern (*note
    the two spaces*) seems to be one of those (*for example, `SZ  66`*),
    so `SZ` prefix is added to the list by default. Obviously, if you set
    `fallbackToLikeInsteadOfEqual` to `False`, then you don't need to care
    about this parameter at all.

    Example:

    ``` py
    from phab.utils.databases import simbad
    from typing import Optional

    oid: Optional[int] = None
    try:
        oid = simbad.getObjectID("A2 146")
    except KeyError as ex:
        print(f"Something wrong with querying SIMBAD. {repr(ex)}")
    if oid is not None:
        print(f"Object ID: {oid}")
    else:
        print("No results")
    ```
    """
    oid: Optional[int] = None

    # check if this name is already the main ID
    logger.debug(f"Checking whether [{starName}] is already the main ID")
    rez = tap.queryService(
        tap.getServiceEndpoint("simbad"),
        " ".join((
            "SELECT oid",
            "FROM basic",
            f"WHERE main_id = '{starName}'"
        ))
    )
    if rez:
        oid = rez[0]["oid"]
        logger.debug(
            " ".join((
                f"- yes, that is already the main ID,",
                "no need to iterate all the identificators.",
                f"SIMBAD object ID is: {oid}"
            ))
        )
    else:
        logger.debug(
            " ".join((
                "- no, that is not the main ID, will have to iterate",
                "all the other identificators"
            ))
        )
        ids = Simbad.query_objectids(starName)
        if ids is None:
            logger.warning(
                " ".join((
                    "SIMBAD database doesn't have information",
                    f"about [{starName}]"
                ))
            )
        else:
            logger.debug(f"Checking SIMBAD IDs for [{starName}]:")

            # before astroquery version 0.4.8 this table had
            # an upper-cased `ID` column key, but starting
            # with version 0.4.8 it is now lower-cased `id`
            #
            # https://github.com/astropy/astropy/issues/17695
            idColumnKey: str = "ID"
            # or compare `astroquery.__version__` with `0.4.7`
            if idColumnKey not in ids.colnames:
                logger.debug(
                    " ".join((
                        "There is no upper-cased [ID] key",
                        "in the resulting table, will try",
                        "with lower-cased [id] key"
                    ))
                )
                idColumnKey = idColumnKey.lower()  # "id"
                if idColumnKey not in ids.colnames:
                    errorMsg = " ".join((
                        "SIMBAD results table has neither [ID]",
                        "nor [id] column"
                    ))
                    logger.error(errorMsg)
                    if len(ids.colnames) > 0:
                        logger.debug(
                            " ".join((
                                "Here are all the columns/keys",
                                "in this table:",
                                ", ".join(ids.colnames)
                            ))
                        )
                    else:
                        logger.debug(
                            " ".join((
                                "There are no columns/keys",
                                "in this table at all"
                            ))
                        )
                    raise KeyError(errorMsg)

            for id in ids:
                idValue: str = id[idColumnKey]
                logger.debug(f"- {idValue}")

                if idValue == starName:
                    logger.debug(
                        f"...the [{idValue}] has already been tested, skipping"
                    )
                    continue
                rez = tap.queryService(
                    tap.getServiceEndpoint("simbad"),
                    " ".join((
                        "SELECT oid",
                        "FROM basic",
                        f"WHERE main_id = '{idValue}'"
                    ))
                )
                if rez:
                    oid = rez[0]["oid"]
                    logger.debug(
                        " ".join((
                            f"The [{idValue}] is the main ID for",
                            f"[{starName}], SIMBAD object ID is: {oid}"
                        ))
                    )
                    break
                else:  # fallback for known problematic identifiers
                    # database returns identifiers like `Sz  66`,
                    # but the actual `main_id` field will contain
                    # all capital `SZ  *`
                    idValueUppercased = idValue.upper()
                    if (
                        fallbackToLikeInsteadOfEqual
                        and
                        idValueUppercased.startswith(
                            tuple(problematicIdentifiersPrefixes)
                        )
                        # idValueUppercased.startswith(
                        #     # a bit of an abomination to uppercase the list
                        #     tuple(
                        #         list(
                        #             map(
                        #                 str.upper,
                        #                 problematicIdentifiersPrefixes
                        #             )
                        #         )
                        #     )
                        # )
                    ):
                        logger.debug(
                            " ".join((
                                "Did not find SIMBAD object ID for",
                                f"[{idValue}], but it is a known problematic",
                                "identifier, so will try a fallback with LIKE"
                            ))
                        )
                        rez = tap.queryService(
                            tap.getServiceEndpoint("simbad"),
                            " ".join((
                                "SELECT TOP 1 oid",
                                "FROM basic",
                                f"WHERE main_id LIKE '{idValueUppercased}'"
                            ))
                        )
                        if rez:
                            oid = rez[0]["oid"]
                            logger.debug(
                                " ".join((
                                    f"The [{idValueUppercased}] is the main",
                                    f"ID for [{starName}], SIMBAD object ID",
                                    f"is: {oid}"
                                ))
                            )
                            logger.warning(
                                " ".join((
                                    "Managed to find the SIMBAD object ID,",
                                    "but be aware that it was found with",
                                    "a fallback for problematic identifiers,",
                                    "which means using LIKE in the WHERE",
                                    "clause, so the result is not guaranteed",
                                    "to be correct"
                                ))
                            )
                            break
    return oid


def getStellarParameter(
    starName: str,
    table: str,
    param: str
) -> Optional[tuple[Any, str]]:
    """
    A convenience function for querying SIMBAD for a stellar parameter:

    1. Finds SIMBAD's object ID by the star name
    (*with `utils.databases.simbad.getObjectID`*);
    2. Queries for a stellar parameter by that object ID
    (*with `utils.databases.tap.getStellarParameterFromSimbadByObjectID`*).

    Example:

    ``` py
    from phab.utils.databases import simbad

    starName = "PPM 725297"
    param = "period"
    rez = simbad.getStellarParameter(
        starName,
        "mesVar",
        param
    )
    if rez:
        val = rez[0]
        ref = rez[1]
        print(f"Value: {val}, reference: {ref}")
    else:
        print(f"SIMBAD doesn't have data about [{param}] parameter of [{starName}] object")
    ```
    """
    rez: Optional[tuple[Any, str]] = None

    oid = getObjectID(starName)
    if oid:
        # logger.debug(
        #     f"Found the following object ID for [{starName}]: {oid}"
        # )
        rez = tap.getStellarParameterFromSimbadByObjectID(
            oid,
            table,
            param
        )

    return rez
