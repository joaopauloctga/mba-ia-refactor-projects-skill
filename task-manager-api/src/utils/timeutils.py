"""Time helpers.

`utcnow()` replaces the deprecated `datetime.utcnow()` (removed-in-future in
Python 3.12+) while keeping NAIVE UTC semantics, so it stays comparable with the
naive datetimes stored in the SQLite columns (mixing aware/naive would raise).
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
