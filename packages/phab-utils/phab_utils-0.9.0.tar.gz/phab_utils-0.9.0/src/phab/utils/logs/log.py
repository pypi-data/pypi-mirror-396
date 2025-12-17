"""
Logging customization.
"""

import sys
import logging

from . import debugMode

_loggingLevel: int = logging.INFO
_loggingFormat: str = "[%(levelname)s] %(message)s"
if debugMode:
    _loggingLevel = logging.DEBUG
    # 8 is the length of "CRITICAL" - the longest log level name
    _loggingFormat = "%(asctime)s | %(levelname)-8s | %(message)s"
_formatter = logging.Formatter(_loggingFormat)

# create a separate logger, so it doesn't override
# logging settings in consuming projects
logger = logging.getLogger("phab")
"""
Pre-made logger object with custom formatting, printing messages
to standard output (stdout).

Example:

``` py
from phab.utils.logs.log import logger

logger.debug("Some debug message")
logger.info("Some regular message")
```

With `utils.logs.debugMode` set to `False` the output will be:

```
[INFO] Some regular message
```

otherwise:

```
2023-11-26 14:52:13,692 | DEBUG    | Some debug message
2023-11-26 14:52:13,693 | INFO     | Some regular message
```
"""

logger.setLevel(_loggingLevel)
# # disable default handler, so it doesn't duplicate logging
logger.propagate = False

_streamHandler = logging.StreamHandler(sys.stdout)
_streamHandler.setFormatter(_formatter)

logger.addHandler(_streamHandler)
