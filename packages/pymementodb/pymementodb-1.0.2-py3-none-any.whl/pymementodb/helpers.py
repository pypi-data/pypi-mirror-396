from datetime import datetime, timezone


def transform_str_to_dt(value: str) -> datetime:
    """Transforms datetime value received from Memento to datetime object.

    Args:
        value: datetime string in the format '2022-08-01T12:53:40.000Z'

    Returns:
        datetime object
    """
    isoformat_str = value.replace('Z', '+00:00')
    return datetime.fromisoformat(isoformat_str)


def transform_dt_to_str(value: datetime) -> str:
    """Transforms datetime to memento datetime string of format '2022-08-01T12:53:40+00:00'.

    Args:
        value: datetime object

    Returns:
        string of datetime
    """
    return value.astimezone(timezone.utc).isoformat(timespec='seconds')+'+00:00'
