from datetime import datetime


def dt_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


def uuid_str(value) -> str | None:
    if value is None:
        return None
    return str(value)
