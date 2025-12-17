"""
Getting data from various databases
via [TAP](https://ivoa.net/documents/TAP/) interface.
"""

# what is available for importing from __init__.py
# __all__ = [
#     "services",
#     "queryService",
#     ...
# ]

import pyvo
import re

from typing import Optional, Dict, List, Tuple, Any, cast

from ..logs.log import logger
from ..strings import extraction, conversion

services: Dict[str, Dict] = {
    "nasa":
    {
        # case-sensitive URL
        "endpoint": "https://exoplanetarchive.ipac.caltech.edu/TAP",
        "parameters-that-are-strings":
        [
            "st_metratio",
            "st_spectype"
        ],
        "parameters-that-have-errors":
        [
            "period",
            "pl_massj",
            "pl_orbper",
            "pl_orbsmax",
            "pl_radj",
            "semi_major_axis"
        ],
        "drops-leading-zero-on-cast-to-varchar": True
    },
    "padc":
    {
        "endpoint": "http://voparis-tap-planeto.obspm.fr/tap",
        "drops-leading-zero-on-cast-to-varchar": False
    },
    "gaia":
    {
        "endpoint": "https://gea.esac.esa.int/tap-server/tap",
        "drops-leading-zero-on-cast-to-varchar": False
    },
    "simbad":
    {
        "endpoint": "http://simbad.cds.unistra.fr/simbad/sim-tap/sync"
        # does not support CAST, so no "drops-leading-zero-on-cast-to-varchar"
    }
}
"""
Dictionary of the most common TAP services.
"""

mappings: Dict[str, Dict] = {
    "NASA-to-PADC":
    {
        "planets":
        {
            "ima_flag": "ima_flag",
            "pl_massj": "mass",
            "pl_massjerr1": "mass_error_max",
            "pl_massjerr2": "mass_error_min",
            "pl_massjlim": "pl_massjlim",
            "pl_name": "granule_uid",
            "pl_orbeccen": "eccentricity",
            "pl_orbincl": "inclination",
            "pl_orbper": "period",
            "pl_orbpererr1": "period_error_max",
            "pl_orbpererr2": "period_error_min",
            "pl_orbperlim": "pl_orbperlim",
            "pl_orbsmax": "semi_major_axis",
            "pl_orbsmaxerr1": "semi_major_axis_error_max",
            "pl_orbsmaxerr2": "semi_major_axis_error_min",
            "pl_orbsmaxlim": "pl_orbsmaxlim",
            "pl_radj": "radius",
            "pl_radjerr1": "radius_error_max",
            "pl_radjerr2": "radius_error_min",
            "pl_radjlim": "pl_radjlim",
            "rv_flag": "rv_flag",
            "tran_flag": "tran_flag",
            "ttv_flag": "ttv_flag"
        },
        "stars":
        {
            "cb_flag": "cb_flag",
            "hostname": "star_name",
            "ra": "ra",
            "st_age": "star_age",
            "st_lum": "st_lum",
            "st_mass": "star_mass",
            "st_met": "star_metallicity",
            "st_metratio": "st_metratio",
            "st_rad": "star_radius",
            "st_rotp": "st_rotp",
            "st_spectype": "star_spec_type",
            "st_teff": "star_teff",
            "sy_dist": "sy_dist",
            "sy_pnum": "sy_pnum",
            "sy_snum": "sy_snum"
        }
    }
}
"""
Mapping tables columns between different databases.
"""


def getServiceEndpoint(tapServiceName: str) -> str:
    """
    Get TAP service endpoint by the service/database name.

    Example:

    ``` py
    from phab.utils.databases import tap

    tapServiceEndpoint = tap.getServiceEndpoint("padc")
    print(tapServiceEndpoint)
    ```
    """
    tapService = services.get(tapServiceName)
    if tapService:
        tapServiceEndpoint = tapService.get("endpoint")
        if tapServiceEndpoint:
            return tapServiceEndpoint
        else:
            raise ValueError(
                f"The [{tapServiceName}] service has no registered endpoint"
            )
    else:
        raise ValueError(
            f"There is no TAP service under the name [{tapServiceName}]"
        )


def escapeSpecialCharactersForAdql(rawQuery: str) -> str:
    """
    Escape certain special characters in ADQL query. For now only escapes
    a single quote character.

    Example:

    ``` py
    from phab.utils.databases import tap

    rawQuery = " ".join((
        "SELECT oid FROM basic",
        "WHERE main_id = 'NAME Teegarden's Star'",
        "AND main_id != 'someone else's star'"
    ))
    print(rawQuery)
    escapedQuery = tap.escapeSpecialCharactersForAdql(rawQuery)
    print(escapedQuery)
    ```
    """
    escapedQuery: str = re.sub(
        r"('([^']*)(')([^']*)')",
        r"'\g<2>'\g<3>\g<4>'",
        rawQuery
    )
    return escapedQuery


def queryService(
    tapEndpoint: str,
    adqlQuery: str,
    tryToReExecuteOnFailure: bool = True
) -> Optional[pyvo.dal.tap.TAPResults]:
    """
    Send [ADQL](https://ivoa.net/documents/ADQL/) request to the TAP service
    and return results. Those can be then converted to
    a [Pandas](https://pandas.pydata.org) table.

    Example:

    ``` py
    from phab.utils.databases import tap

    tbl = tap.queryService(
        tap.getServiceEndpoint("padc"),
        " ".join((
            "SELECT star_name, granule_uid, mass, radius, period, semi_major_axis",
            "FROM exoplanet.epn_core",
            "WHERE star_name = 'Kepler-107'",
            "ORDER BY granule_uid"
        ))
    )
    if tbl:
        print(tbl.to_table().to_pandas())
    else:
        print("No results")
    ```
    """
    tapService = pyvo.dal.TAPService(tapEndpoint)
    logger.debug(f"ADQL query to execute: {adqlQuery}")
    results = None
    try:
        results = tapService.search(adqlQuery)
    except pyvo.dal.exceptions.DALQueryError as ex:
        if tryToReExecuteOnFailure:
            logger.warning(
                " ".join((
                    "The query failed, will try to execute again,",
                    "but this time with escaped characters. Original",
                    f"error message: {ex}"
                ))
            )
            adqlQueryEscaped = escapeSpecialCharactersForAdql(adqlQuery)
            logger.debug(f"Escaped ADQL query to execute: {adqlQueryEscaped}")
            results = tapService.search(adqlQueryEscaped)
        else:
            raise
    if results is not None and len(results) > 0:
        logger.debug(f"Results: {len(results)}")
        return results
    else:
        return None


def getParametersThatAreDoubleInNASA() -> List[str]:
    """
    Get the list of parameters names in the NASA `ps` table that have
    the `double` type. That is needed so you knew when to apply
    `CAST(PARAMETER_NAME_HERE AS REAL)` in your `SELECT` statements
    or `CAST(PARAMETER_NAME_HERE AS VARCHAR(30))` in your `WHERE`
    statements, otherwise NASA returns rounded values by default
    (according to their `format` value in `tap_schema.columns`),
    so you might not get the expected results.

    Example:

    ``` py
    from phab.utils.databases import tap

    doubles = tap.getParametersThatAreDoubleInNASA()
    print(doubles)
    ```
    """
    doubles: List[str] = list()

    results = queryService(
        getServiceEndpoint("nasa"),
        " ".join((
            f"SELECT column_name",
            f"FROM tap_schema.columns",
            f"WHERE table_name = 'ps' AND datatype = 'double'"
        ))
    )
    if results:
        doubles = list(results.getcolumn("column_name").flatten())

    return doubles


def getStellarParameterFromNASA(
    systemName: str,
    param: str,
    parameterTypeIsDouble: bool = False
) -> Optional[Any]:
    """
    Get the latest (*the newest*) published stellar parameter
    from NASA database.

    The `parameterTypeIsDouble` argument  is a workaround for the problem with
    [inconsistent values](https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#float-values-are-rounded-on-select-but-compared-to-originals-in-where)
    in `SELECT`/`WHERE`.

    Example:

    ``` py
    from phab.utils.databases import tap

    doubles = tap.getParametersThatAreDoubleInNASA()
    param = "st_teff"
    val = tap.getStellarParameterFromNASA(
        "Kepler-11",
        param,
        parameterTypeIsDouble=(param in doubles)
    )
    print(val)
    ```
    """
    results = queryService(
        getServiceEndpoint("nasa"),
        " ".join((
            # TOP is broken in NASA: https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#top-clause-is-broken
            (
                f"SELECT {param}"
                if not parameterTypeIsDouble else
                f"SELECT CAST({param} AS REAL) AS {param}_real"
            ),
            f"FROM ps",
            f"WHERE hostname = '{systemName}' AND {param} IS NOT NULL",
            "ORDER BY pl_pubdate DESC"
        ))
    )
    if results:
        # logger.debug(f"All results for this parameter:\n{results}")
        return (
            results[0].get(param)
            if not parameterTypeIsDouble else
            results[0].get(f"{param}_real")
        )
    else:
        return None


def getPlanetaryParameterFromNASA(
    planetName: str,
    param: str,
    parameterTypeIsDouble: bool = False
) -> Optional[Any]:
    """
    Get the latest (*the newest*) published planetary parameter
    from NASA database.

    The `parameterTypeIsDouble` argument  is a workaround for the problem with
    [inconsistent values](https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#float-values-are-rounded-on-select-but-compared-to-originals-in-where)
    in `SELECT`/`WHERE`.

    Example:

    ``` py
    from phab.utils.databases import tap

    doubles = tap.getParametersThatAreDoubleInNASA()
    param = "pl_massj"
    val = tap.getPlanetaryParameterFromNASA(
        "Kepler-11 b",
        param,
        parameterTypeIsDouble=(param in doubles)
    )
    print(val)
    ```
    """
    results = queryService(
        getServiceEndpoint("nasa"),
        " ".join((
            # TOP is broken in NASA: https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#top-clause-is-broken
            (
                f"SELECT {param}"
                if not parameterTypeIsDouble else
                f"SELECT CAST({param} AS REAL) AS {param}_real"
            ),
            f"FROM ps",
            f"WHERE pl_name = '{planetName}' AND {param} IS NOT NULL",
            "ORDER BY pl_pubdate DESC"
        ))
    )
    if results:
        # logger.debug(f"All results for this parameter:\n{results}")
        return (
            results[0].get(param)
            if not parameterTypeIsDouble else
            results[0].get(f"{param}_real")
        )
    else:
        return None


def getPlanetaryParameterReferenceFromNASA(
    planetName: str,
    paramName: str,
    paramValue: int | float | str,
    parameterTypeIsDouble: bool = False,
    tryToReExecuteIfNoResults: bool = True,
    returnOriginalReferenceOnFailureToExtract: bool = True
) -> Optional[Any]:
    """
    Get the publication reference for the given planetary parameter value
    from NASA database.

    The `parameterTypeIsDouble` argument  is a workaround for the problem with
    [inconsistent values](https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#float-values-are-rounded-on-select-but-compared-to-originals-in-where)
    in `SELECT`/`WHERE`.

    Example:

    ``` py
    from phab.utils.databases import tap

    doubles = tap.getParametersThatAreDoubleInNASA()
    param = "pl_massj"
    val = tap.getPlanetaryParameterReferenceFromNASA(
        "KOI-4777.01",
        param,
        0.31212,
        parameterTypeIsDouble=(param in doubles)
    )
    print(val)
    ```
    """
    fullRefValue: Optional[str] = None

    if tryToReExecuteIfNoResults and not parameterTypeIsDouble:
        logger.warning(
            " ".join((
                "The re-execution flag is passed, but parameter type",
                "is not double, so the query will not be re-executed"
            ))
        )

    parameterIsString: bool = False
    if isinstance(paramValue, str):
        # logger.debug(f"The {paramName} value {paramValue} is a string")
        parameterIsString = True
    results = queryService(
        getServiceEndpoint("nasa"),
        " ".join((
            f"SELECT pl_refname",  # TOP is broken in NASA: https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#top-clause-is-broken
            f"FROM ps",
            f"WHERE pl_name = '{planetName}' AND {paramName}",
            (
                f"= {paramValue}"
                if not parameterIsString else
                f"= '{paramValue}'"
            ),
            "ORDER BY pl_pubdate DESC"
        ))
    )
    if results:
        # logger.debug(f"All results:\n{results}")
        fullRefValue = results[0].get("pl_refname")
    # might be because of that doubles precision problem, thank you, NASA
    elif (
        results is None
        and
        parameterTypeIsDouble
        and
        tryToReExecuteIfNoResults
    ):
        logger.warning(
            " ".join((
                "The query returned no results, will try to execute again,",
                "but this time with the parameter casted from double to string"
            ))
        )
        paramValueLength = len(str(paramValue))
        paramValue = cast(float, paramValue)
        paramValueString = conversion.floatToStringForADQLcastVarchar(
            paramValue,
            dropLeadingZero=True
        )
        results = queryService(
            getServiceEndpoint("nasa"),
            " ".join((
                f"SELECT pl_refname",  # TOP is broken in NASA: https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#top-clause-is-broken
                f"FROM ps",
                f"WHERE pl_name = '{planetName}'",
                " ".join((
                    f"AND CAST({paramName} AS VARCHAR({paramValueLength}))",
                    f"LIKE '{paramValueString}'"
                )),
                "ORDER BY pl_pubdate DESC"
            ))
        )
        if results:
            # logger.debug(f"All results:\n{results}")
            fullRefValue = results[0].get("pl_refname")
    else:
        return None

    if fullRefValue is not None:
        ref = extraction.adsRefFromFullReferenceNASA(fullRefValue)
        if ref is None and returnOriginalReferenceOnFailureToExtract:
            return fullRefValue
        return ref
    else:
        return None


def getParameterFromNASA(
    systemName: str,
    planetName: str,
    param: str,
    parameterTypeIsDouble: bool = False
) -> Optional[Any]:
    """
    Get the latest (*the newest*) published parameter from NASA database.
    The parameter kind (*stellar or planetary*) is determined
    based on the `utils.databases.tap.mappings` list. This might be
    convenient when one only has a list of parameters names
    without specifying which one is of which kind.

    The `parameterTypeIsDouble` argument  is a workaround for the problem with
    [inconsistent values](https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#float-values-are-rounded-on-select-but-compared-to-originals-in-where)
    in `SELECT`/`WHERE`.

    Example:

    ``` py
    from phab.utils.databases import tap

    systemName = "Kepler-11"
    planetName = "Kepler-11 b"
    params = ["st_teff", "pl_massj"]
    doubles = tap.getParametersThatAreDoubleInNASA()
    for p in params:
        val = tap.getParameterFromNASA(
            systemName,
            planetName,
            p,
            parameterTypeIsDouble=(p in doubles)
        )
        print(val)
    ```
    """
    result = None
    if param in mappings["NASA-to-PADC"]["stars"]:  # get stellar parameter
        result = getStellarParameterFromNASA(
            systemName,
            param,
            parameterTypeIsDouble
        )
    else:  # get planetary parameter
        result = getPlanetaryParameterFromNASA(
            planetName,
            param,
            parameterTypeIsDouble
        )
    return result


def getParameterErrorsFromNASA(
    systemName: str,
    planetName: str,
    param: str
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get the latest (*the newest*) published stellar or planetary
    parameter errors from NASA database. This is a convenience function
    that uses `utils.databases.tap.getParameterFromNASA`
    to get `PARAMerr2` (*minimum error*) and `PARAMerr1` (*maximum error*).

    Example:

    ``` py
    from phab.utils.databases import tap

    systemName = "Kepler-11"
    planetName = "Kepler-11 b"
    params = ["st_teff", "pl_massj"]
    for p in params:
        errMin, errMax = tap.getParameterErrorsFromNASA(
            systemName,
            planetName,
            p
        )
        print(errMin, errMax)
    ```
    """
    errMin = getParameterFromNASA(systemName, planetName, f"{param}err2")
    errMax = getParameterFromNASA(systemName, planetName, f"{param}err1")
    return errMin, errMax


def getParameterFromPADC(
    planetName: str,
    param: str
) -> Optional[Any]:
    """
    Get stellar or planetary parameter from PADC database.

    Example:

    ``` py
    from phab.utils.databases import tap

    val = tap.getParameterFromPADC("Kepler-11 b", "mass")
    print(val)
    ```
    """
    results = queryService(
        getServiceEndpoint("padc"),
        " ".join((
            f"SELECT {param}",
            f"FROM exoplanet.epn_core",
            f"WHERE granule_uid = '{planetName}' AND {param} IS NOT NULL"
        ))
    )
    if results:
        return results[0].get(param)
    else:
        return None


def getParameterErrorsFromPADC(
    planetName: str,
    param: str
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get stellar or planetary parameter errors from PADC database.
    This is a convenience function that uses
    `utils.databases.tap.getParameterFromPADC` to get `PARAM_error_min`
    and `PARAM_error_max`.

    Example:

    ``` py
    from phab.utils.databases import tap

    errMin, errMax = tap.getParameterErrorsFromPADC("Kepler-11 b", "mass")
    print(errMin, errMax)
    ```
    """
    errMin = getParameterFromPADC(planetName, f"{param}_error_min")
    errMax = getParameterFromPADC(planetName, f"{param}_error_max")
    return errMin, errMax


def getStellarParameterFromSimbadByMainID(
    mainID: str,
    table: str,
    param: str,
) -> Optional[tuple[Any, str]]:
    """
    Get the latest (*the newest*) published stellar parameter from SIMBAD
    by using the main ID - star name that is chosen to be stored in `main_id`
    field of the `basic` table.

    Example:

    ``` py
    from phab.utils.databases import tap

    val, ref = tap.getStellarParameterFromSimbadByMainID(
        "CD-29 2360",
        "mesVar",
        "period"
    )
    print(f"Value: {val}, reference: {ref}")
    ```
    """
    results = queryService(
        getServiceEndpoint("simbad"),
        " ".join((
            f"SELECT TOP 1 v.{param}, v.bibcode",
            f"FROM {table} AS v",
            "JOIN basic AS b ON v.oidref = b.oid",
            f"WHERE b.main_id = '{mainID}' AND {param} IS NOT NULL",
            "ORDER BY bibcode DESC"
        ))
    )
    if results:
        return (
            results[0].get(param),
            results[0].get("bibcode")
        )
    else:
        return None


def getStellarParameterFromSimbadByObjectID(
    objectID: int,
    table: str,
    param: str
) -> Optional[tuple[Any, str]]:
    """
    Get the latest (*the newest*) published stellar parameter from SIMBAD
    by using the SIMBAD's object ID.

    If you only have the star name, then first you will need to find
    the object ID with `utils.databases.simbad.getObjectID`.

    Example:

    ``` py
    from phab.utils.databases import simbad
    from phab.utils.databases import tap

    oid = simbad.getObjectID("PPM 725297")
    if not oid:
        print("Could not find SIMBAD object ID")
    else:
        val, ref = tap.getStellarParameterFromSimbadByObjectID(
            oid,
            "mesVar",
            "period"
        )
        print(f"Value: {val}, reference: {ref}")
    ```

    There is also a convenience function `utils.databases.simbad.getStellarParameter`.
    """
    results = queryService(
        getServiceEndpoint("simbad"),
        " ".join((
            f"SELECT TOP 1 {param}, bibcode",
            f"FROM {table}",
            f"WHERE oidref = {objectID} AND {param} IS NOT NULL",
            "ORDER BY bibcode DESC"
        ))
    )
    if results:
        return (
            results[0].get(param),
            results[0].get("bibcode")
        )
    else:
        return None
