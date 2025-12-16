from datetime import datetime, timezone


def iso_date_to_timestamp(datetime_string: str) -> int:
    dt_object = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int(dt_object.replace(tzinfo=timezone.utc).timestamp() * 1000)


def timestamp_to_iso_date(timestamp_ms: int) -> str:
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")
