"""
.. include:: ../../../../documentation/utils/logs/index.md
"""

import os

debugMode: bool = False
"""
Flag for enabling debug log. When it is set to `True`, the logging format
is extended, and the level of details being printed out is increased.
"""

if "PHAB_DEBUG" in os.environ:
    debugModeValue: str = os.environ["PHAB_DEBUG"].lower()
    if (
        debugModeValue != "0"
        and
        debugModeValue != "no"
        and
        debugModeValue != "off"
        and
        debugModeValue != "false"
        and
        debugModeValue != "disable"
    ):
        debugMode = True
