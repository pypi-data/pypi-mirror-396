import pytest

from utils.strings import extraction, conversion
from . import somethingThatDoesntExist


def test_ref_from_full_reference_nasa(
    somethingThatDoesntExist: str
) -> None:
    ref = extraction.adsRefFromFullReferenceNASA(
        "<a refstr=BORSATO_ET_AL__2014 href=https://ui.adsabs.harvard.edu/abs/2014A&A...571A..38B/abstract target=ref>Borsato et al. 2014</a>"
    )
    assert ref == "2014A&A...571A..38B"

    ref = extraction.adsRefFromFullReferenceNASA(
        somethingThatDoesntExist
    )
    assert ref is None, \
        " ".join((
            "There can't be a reference value in",
            f"\"{somethingThatDoesntExist}\" string"
        ))


def test_float_to_string_for_adql_cast_varchar() -> None:
    val = conversion.floatToStringForADQLcastVarchar(1.2345, False)
    assert val == "1.234%"

    val = conversion.floatToStringForADQLcastVarchar(1.2345, True)
    assert val == "1.234%"

    val = conversion.floatToStringForADQLcastVarchar(0.2345, False)
    assert val == "0.234%"

    val = conversion.floatToStringForADQLcastVarchar(0.2345, True)
    assert val == ".234%"

    val = conversion.floatToStringForADQLcastVarchar(-1.2345, False)
    assert val == "-1.234%"

    val = conversion.floatToStringForADQLcastVarchar(-1.2345, True)
    assert val == "-1.234%"

    val = conversion.floatToStringForADQLcastVarchar(-0.2345, False)
    assert val == "-0.234%"

    val = conversion.floatToStringForADQLcastVarchar(-0.2345, True)
    assert val == "-.234%"
