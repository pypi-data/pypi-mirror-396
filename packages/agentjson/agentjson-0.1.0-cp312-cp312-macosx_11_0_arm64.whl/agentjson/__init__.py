"""agentjson: distribution name + import alias for `json_prob_parser`.

This package exists so code can do:

    import agentjson

while preserving the original internal module name (`json_prob_parser`) for
backwards compatibility.
"""

from __future__ import annotations

from json_prob_parser import *  # noqa: F403

from json_prob_parser import __all__ as __all__  # noqa: F401
