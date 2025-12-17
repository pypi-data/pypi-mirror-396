"""
Getting light curves data.
"""

import lightkurve
from astropy.table import Table
import pandas
from pandera import pandas as pandera
import numpy
import pathlib
import re
from packaging.version import Version

from typing import Optional, Dict, List, Pattern, Literal

from ..files import file as fl
from ..logs.log import logger

# apparently, one cannot set long/short threshold,
# hence this dictionary
#
# there are actually more authors available,
# but we are only interested in these
#
authors: Dict[str, Dict] = {
    "Kepler":
    {
        "mission": "Kepler",
        "cadence":
        {
            "long": [1800],
            "short": [60]
        }
    },
    "K2":
    {
        "mission": "K2",
        "cadence":
        {
            "long": [1800],
            "short": [60]
        }
    },
    "SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": [600],
            "short": [120],
            "fast": [20]
        }
    },
    "TESS-SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": []  # any cadence is long
        }
    }
}
"""
Dictionary of authors, their cadence values and mapping to missions.
"""

missionSectorRegExes: Dict[str, Pattern] = {
    "Kepler": re.compile(
        r"^Kepler\s\w+\s(\d+)$"  # Kepler Quarter 15
    ),
    "K2": re.compile(
        r"^K2\s\w+\s(\d+)$"  # K2 Campaign 12
    ),
    "TESS": re.compile(
        r"^TESS\s\w+\s(\d+)$"  # TESS Sector 40
    )
}
"""
Dictionary of regular expressions for extracting sectors.
"""

lightCurveFluxTableSchema = pandera.DataFrameSchema(
    {
        "time": pandera.Column(numpy.float64),
        "flux": pandera.Column(numpy.float32, nullable=True),
        "fluxError": pandera.Column(numpy.float32, nullable=True)
    },
    index=pandera.Index(int, unique=True),
    strict=True,  # only specified columns are allowed
    coerce=False  # do not cast other types to the specified one
)
"""
Table schema for light curve fluxes.
"""


def getLightCurveStats(
    starName: str,
    detailed: bool = True
) -> Dict[str, Dict]:
    """
    Gather statistics about available cadence values for a given star.

    If `detailed` is set to `False`, then function will skip collecting
    cadence values count by sectors, so resulting statistics will only
    contain total count of values.

    Example:

    ``` py
    from phab.utils.databases import lightcurves

    stats = lightcurves.getLightCurveStats("Kepler-114")
    if not stats:
        print("Didn't find any results for this star")
    else:
        missionName = "Kepler"
        cadenceType = "long"
        sectors = stats.get(
            missionName,
            {}
        ).get(cadenceType)
        if sectors is None:
            print(
                " ".join((
                    "There doesn't seem to be any sectors",
                    f"with [{cadenceType}] cadence by [{missionName}]"
                ))
            )
        else:
            totalProperty = "total"
            sectorsCount = sectors.get(totalProperty)
            if sectorsCount is None:
                print(
                    " ".join((
                        f"For some reason, the [{totalProperty}] property",
                        f"is missing from the [{cadenceType}] cadence",
                        f"collection by [{missionName}]"
                    ))
                )
            else:
                print(
                    " ".join((
                        f"Total amount of sectors with [{cadenceType}]",
                        f"cadence by [{missionName}]: {sectorsCount}",
                    ))
                )
                bySectors = sectors.get("by-sectors")
                if bySectors is None:
                    print(
                        " ".join((
                            "For some reason, the [total] property is missing",
                            f"from the [{cadenceType}] cadence collection",
                            f"by [{missionName}]"
                        ))
                    )
                else:
                    for s in bySectors:
                        print(f"- {s}: {bySectors[s]}")
    ```
    """
    stats: Dict[str, Dict] = {}

    lghtcrvs = lightkurve.search_lightcurve(
        starName,
        author=tuple(authors.keys())
    )
    if len(lghtcrvs) != 0:
        tbl: pandas.DataFrame = lghtcrvs.table.to_pandas()[
            ["author", "exptime", "mission"]
        ]
        logger.debug(tbl)

        author: str  # for mypy, but even then it is not happy with something else
        for author, group in (tbl.groupby("author")):  # type:ignore[assignment] # ya hz
            if author not in authors:
                raise ValueError(f"Unknown author: {author}")
            mission = authors[author]["mission"]
            if not stats.get(mission):
                stats[mission] = {}
            for cadence in ["long", "short", "fast"]:
                if cadence in authors[author]["cadence"]:
                    stats[mission][cadence] = {}
                    cadenceValues: List[int] = (
                        authors[author]["cadence"][cadence]
                    )
                    cadences: pandas.DataFrame
                    if len(cadenceValues) > 0:  # take only specified values
                        # perhaps both of these should be normalized to int
                        cadences = group.query("exptime == @cadenceValues")
                    else:  # any value is good
                        cadences = group

                    # total count
                    stats[mission][cadence]["total"] = len(cadences)

                    if detailed:
                        # count by sectors
                        stats[mission][cadence]["by-sectors"] = {}
                        for m in cadences["mission"]:
                            # logger.debug(cadences.query("mission == @m")[
                            #     "exptime"
                            # ].values)
                            sectorMatch = re.search(
                                missionSectorRegExes[mission],
                                m
                            )
                            if not sectorMatch:
                                raise ValueError(
                                    " ".join((
                                        "Couldn't extract sector from",
                                        f"this mission value: {m}"
                                    ))
                                )
                            sector = sectorMatch.group(1)
                            if not stats[mission][cadence]["by-sectors"].get(
                                sector
                            ):  # this sector hasn't been added yet
                                stats[mission][cadence]["by-sectors"][
                                    sector
                                ] = {}
                                # save the cadence/exptime too (assuming
                                # that it is the same for every sector entry)
                                stats[mission][cadence]["by-sectors"][sector][
                                    "exptime"
                                ] = cadences.query("mission == @m")[
                                    "exptime"
                                ].values[0]  # there must be a better way
                            try:
                                stats[mission][cadence][
                                    "by-sectors"
                                ][sector]["count"] += 1
                            except KeyError:
                                stats[mission][cadence][
                                    "by-sectors"
                                ][sector]["count"] = 1
    return stats


def getLightCurveIDs(
    starName: str
) -> Dict[str, List[str]]:
    """
    Based on available cadence values statistics for a given star,
    get names of missions and cadences. For instance, in order to pass
    them to `altaipony.lcio.from_mast()`.

    Example:

    ``` py
    from phab.utils.databases import lightcurves
    from altaipony.lcio import from_mast

    starName = "LTT 1445 A"
    lightCurveIDs = {}

    try:
        lightCurveIDs = lightcurves.getLightCurveIDs(starName)
    except ValueError as ex:
        print(f"Failed to get light curves missons and cadences. {ex}")
        raise
    if not lightCurveIDs:
        raise ValueError("Didn't find any results for this star")
    #print(lightCurveIDs)

    for m in lightCurveIDs.keys():
        #print(f"Mission: {m}")
        for c in lightCurveIDs[m]:
            #print(f"- {c}")
            flc = from_mast(
                starName,
                mode="LC",
                cadence=c,
                mission=m
            )
            #print(flc)
    ```
    """
    lightCurveIDs: Dict[str, List[str]] = {}

    stats: Dict[str, Dict] = getLightCurveStats(
        starName,
        detailed=False
    )
    if not stats:
        raise ValueError("Didn't find any results for this star")

    # the order matters, it goes from most important to least important,
    # and in fact long cadence is so not important that it is discarded
    # if there is fast or short cadence available
    cadencePriority = ["fast", "short", "long"]

    for m in stats.keys():
        lightCurveIDs[m] = []
        priorityThreshold = 0
        for cp in cadencePriority:
            # if there is already fast or short cadence in the list,
            # don't take long cadence (except for mission K2, because
            # its long cadence is what's most important even if
            # there are also fast and short ones)
            if any(lightCurveIDs[m]) and priorityThreshold > 1 and m != "K2":
                break
            if cp in stats[m]:
                # print(f"Count [{cp}]: {stats[m][cp]['total']}")
                totalCnt = stats[m][cp].get("total")
                if totalCnt and totalCnt != 0:
                    lightCurveIDs[m].append(cp)
                # else:
                #     print(
                #         " ".join((
                #             f"[WARNING] The [{cp}] cadence count",
                #             f"in [{m}] is 0 (or missing)"
                #         ))
                #     )
            priorityThreshold += 1

    return lightCurveIDs


def fitsToPandas(
    fitsFilePath: str,
    fitsType: Optional[Literal["tess", "kepler"]] = None,
    qualityBitmask: Literal["none", "default", "hard", "hardest"] = "default",
    dropNanTimes: bool = True,
    convertTimesToSeconds: bool = False
) -> pandas.DataFrame:
    """
    Open a generic light curves [FITS](https://en.wikipedia.org/wiki/FITS) file
    and create a Pandas table from it. Only the fluxes, their times
    and errors columns are taken.

    Handles the big/little endians problem when converting from FITS to Pandas.

    Example:

    ``` py
    from phab.utils.databases import lightcurves

    pnd = lightcurves.fitsToPandas(
        "./data/tess2019006130736-s0007-0000000266744225-0131-s_lc.fits",
        fitsType="tess",
        qualityBitmask="default",
        dropNanTimes=True,
        convertTimesToSeconds=True
    )

    #print(pnd)
    ```
    """
    lc = None
    fitsFile: Optional[pathlib.Path] = fl.fileExists(fitsFilePath)
    if fitsFile is None:
        raise ValueError(
            f"Provided path to [{fitsFilePath}] seems to be wrong"
        )
    else:
        lc = Table.read(fitsFile)

    # exclude values which do not satisfy the required quality
    if fitsType is not None:
        msk = None
        if fitsType == "tess":
            msk = lightkurve.utils.TessQualityFlags.create_quality_mask(
                quality_array=lc["QUALITY"],
                bitmask=qualityBitmask
            )
        elif fitsType == "kepler":
            msk = lightkurve.utils.KeplerQualityFlags.create_quality_mask(
                quality_array=lc["QUALITY"],
                bitmask=qualityBitmask
            )
        else:
            print(
                " ".join((
                    "[WARNING] Unknown FITS type, don't know",
                    "which quality mask to use"
                ))
            )
        lc = lc[msk]

    narr = numpy.array(lc)
    # FITS stores data in big-endian, but pandas works with little-endian,
    # so the byte order needs to be swapped
    # https://stackoverflow.com/a/30284033/1688203
    if Version(numpy.__version__) > Version("1.26.4"):
        # if that doesn't work, then you might need to downgrade to 1.26.4
        narr = narr.view(narr.dtype.newbyteorder()).byteswap()
    else:
        # have to ignore this in mypy
        narr = narr.byteswap().newbyteorder()  # type: ignore[attr-defined]

    # astropy.time does not(?) support NaN
    if dropNanTimes:
        nantimes = numpy.isnan(narr["TIME"].data)
        if numpy.any(nantimes):
            print(
                " ".join((
                    f"[DEBUG] {numpy.sum(nantimes)} rows were excluded,",
                    "because their time values are NaN"
                ))
            )
        narr = narr[~nantimes]

    # apparently, one cannot just take columns from `lc`/`narr` directly,
    # hence this intermediate table
    pndraw = pandas.DataFrame(narr)
    logger.debug(f"Light curve table columns: {pndraw.columns}")

    flux = pandas.DataFrame(
        columns=[
            "time",
            "flux",
            "fluxError"
        ]
    )
    flux["time"] = pndraw["TIME"]
    flux["flux"] = pndraw["PDCSAP_FLUX"]
    flux["fluxError"] = pndraw["PDCSAP_FLUX_ERR"]

    # in case excluding NaN times right after `Table.read()` is less efficient
    # if dropNanTimes:
    #     flux = flux.dropna(subset=["time"])

    if convertTimesToSeconds:
        flux["time"] = flux["time"] * 24 * 60 * 60

    if dropNanTimes:
        lightCurveFluxTableSchema.validate(flux)
    else:
        lightCurveFluxTableSchema.update_column(
            "time",
            dtype=numpy.float64,
            nullable=True
        ).validate(flux)

    return flux


def lightCurveTessToPandas(
    lightKurve: lightkurve.lightcurve.TessLightCurve,
    convertTimesToSeconds: bool = False
) -> pandas.DataFrame:
    """
    Converting a TESS light curve object to a Pandas table. In general,
    it does almost the same thing as
    `utils.databases.lightcurves.fitsToPandas()`,
    but here there it uses a TESS-specific reading function, and also
    there is no need to drop NaN times "manually" (*and fiddle with endians?*).

    Example:

    ``` py
    from phab.utils.databases import lightcurves
    import lightkurve

    downloadLC: bool = False
    lc = None
    if downloadLC:
        search_result = lightkurve.search_lightcurve(
            "Karmn J07446+035",
            author="SPOC",
            cadence="short"
        )
        lc = search_result[0].download(
            quality_bitmask="default"
        )
    else:
        lc = lightkurve.TessLightCurve.read(
            "./data/tess2019006130736-s0007-0000000266744225-0131-s_lc.fits",
            quality_bitmask="default"
        )

    pnd = lightcurves.lightCurveTessToPandas(lc, convertTimesToSeconds=True)

    #print(pnd)
    ```
    """
    pndraw = lightKurve.to_pandas()
    logger.debug(f"Light curve table columns: {pndraw.columns}")

    flux = pandas.DataFrame(
        columns=[
            "time",
            "flux",
            "fluxError"
        ]
    )

    flux["time"] = pndraw.index
    flux["flux"] = pndraw["pdcsap_flux"].values
    flux["fluxError"] = pndraw["pdcsap_flux_err"].values

    if convertTimesToSeconds:
        flux["time"] = flux["time"] * 24 * 60 * 60

    lightCurveFluxTableSchema.validate(flux)

    return flux
