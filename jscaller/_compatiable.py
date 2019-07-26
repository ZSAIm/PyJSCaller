

__all__ = ["PY2", "PY3"]

import sys

if sys.version_info[0] == 2:
    PY2 = True
    PY3 = False
elif sys.version_info[0] == 3:
    PY2 = False
    PY3 = True
else:
    PY2 = False
    PY3 = False
