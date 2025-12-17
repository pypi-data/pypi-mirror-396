from typing import Optional


def floatToStringForADQLcastVarchar(
    floatValue: float,
    dropLeadingZero: bool = False
) -> str:
    """
    Convert float value to string for using in ADQL queries. For instance,
    the float value is `1.2345`, and we know that database rounds the values,
    so we need to drop the last digit and use `%` instead of it, so in ADQL
    query it will be something like:

    ``` sql
    -- ...
    WHERE CAST(some_float AS VARCHAR(10)) LIKE '1.234%'"
    ```

    Example:

    ``` py
    from phab.utils.strings import conversion
    from phab.utils.databases import tap

    dropsLeadingZeroOnCastToVarchar = tap.services.get(
        "nasa", {}
    ).get(
        "drops-leading-zero-on-cast-to-varchar", False
    )
    val = conversion.floatToStringForADQLcastVarchar(
        1.2345,
        dropsLeadingZeroOnCastToVarchar
    )
    print(val)
    ```
    """
    stringValue: str = ""

    # NASA's ADQL casts `0.123` float value as `.123` string
    if dropLeadingZero and abs(floatValue) < 1:
        if floatValue < 0:  # just in case, preserve the `-` sign
            stringValue = f"-{str(floatValue)[2:-1]}%"
        else:
            stringValue = f"{str(floatValue)[1:-1]}%"
    else:
        stringValue = f"{str(floatValue)[:-1]}%"

    return stringValue
