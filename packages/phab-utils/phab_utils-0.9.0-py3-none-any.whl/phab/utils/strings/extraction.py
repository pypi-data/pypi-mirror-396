import re

from typing import Optional

regexRefNASA = re.compile(r"<a refstr=.* href=.*\/abs\/(.*)\/abstract.*<\/a>")
"""
Regular expression for extracting short reference value from the full
reference string in NASA database.
"""


def adsRefFromFullReferenceNASA(fullRefValue: str) -> Optional[str]:
    """
    Extract just the reference value from the full reference string.

    Example:

    ``` py
    from phab.utils.strings import extraction

    val = extraction.adsRefFromFullReferenceNASA(
        "<a refstr=BORSATO_ET_AL__2014 href=https://ui.adsabs.harvard.edu/abs/2014A&A...571A..38B/abstract target=ref>Borsato et al. 2014</a>"
    )
    print(val)
    ```
    """
    refMatch = re.search(regexRefNASA, fullRefValue)
    if refMatch and not len(refMatch.groups()) < 1:
        return refMatch.group(1)
    else:
        return None
