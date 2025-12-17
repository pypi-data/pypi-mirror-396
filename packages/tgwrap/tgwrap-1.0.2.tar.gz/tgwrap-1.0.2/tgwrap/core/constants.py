"""Core constants and shared utilities for tgwrap."""

from __future__ import annotations

import json
from datetime import datetime


STAGES = [
    "global",
    "sbx",
    "dev",
    "qas",
    "run",
    "tst",
    "acc",
    "prd",
]


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that serialises datetime objects as ISO strings."""

    def default(self, obj):  # pylint: disable=arguments-renamed
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
