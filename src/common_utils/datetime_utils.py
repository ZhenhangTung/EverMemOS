import datetime
from zoneinfo import ZoneInfo
import os
from core.observation.logger import get_logger

logger = get_logger(__name__)


def get_timezone() -> ZoneInfo:
    """
    Get timezone
    """
    tz = os.getenv("TZ", "Asia/Shanghai")
    return ZoneInfo(tz)


timezone = get_timezone()


def get_now_with_timezone() -> datetime.datetime:
    """
    Get current time with local timezone
    return datetime.datetime(2025, 9, 16, 20, 17, 41, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai'))
    """
    return datetime.datetime.now(tz=timezone)


def to_timezone(dt: datetime.datetime, tz: ZoneInfo = None) -> datetime.datetime:
    """
    Convert datetime object to specified timezone
    """
    if tz is None:
        tz = timezone
    return dt.astimezone(tz)


def to_iso_format(dt: datetime.datetime) -> str:
    """
    Convert datetime object to ISO format string (with timezone)
    return 2025-09-16T20:20:06.517301+08:00
    """
    if dt.tzinfo is None:
        # If not, since the default uses the TZ environment variable, manually set the timezone
        dt = dt.replace(tzinfo=timezone)
    # If it's UTC or similar, convert to local timezone
    return dt.astimezone(timezone).isoformat()


def from_timestamp(timestamp: int | float) -> datetime.datetime:
    """
    Convert timestamp to datetime object, automatically recognizing second-level and millisecond-level precision

    Args:
        timestamp: timestamp, supports second-level (10-digit number) and millisecond-level (13-digit number)

    Returns:
        datetime.datetime(2025, 9, 16, 20, 17, 41, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai'))
    """
    # Automatically detect timestamp precision
    # Millisecond-level timestamps usually >= 1e12 (1000000000000), approximately 13 digits
    # Second-level timestamps usually < 1e12, approximately 10 digits
    if timestamp >= 1e12:
        # Millisecond-level timestamp, convert to second-level
        timestamp_seconds = timestamp / 1000.0
    else:
        # Second-level timestamp, use directly
        timestamp_seconds = timestamp

    return datetime.datetime.fromtimestamp(timestamp_seconds, tz=timezone)


def to_timestamp(dt: datetime.datetime) -> int:
    """
    Convert datetime object to timestamp in seconds
    return 1758025061
    """
    return int(dt.timestamp())


def to_timestamp_ms(dt: datetime.datetime) -> int:
    """
    Convert datetime object to millisecond-level timestamp
    return 1758025061123
    """
    return int(dt.timestamp() * 1000)


def to_timestamp_ms_universal(time_value) -> int:
    """
    Universal function to convert various time formats to millisecond-level timestamp
    Supports multiple input formats:
    - int/float: timestamp (automatically recognize second-level or millisecond-level)
    - str: ISO format time string
    - datetime object
    - None: return 0

    Args:
        time_value: various format time values

    Returns:
        int: millisecond-level timestamp, return 0 on failure
    """
    try:
        if time_value is None:
            return 0

        # Handle numeric types (timestamp)
        if isinstance(time_value, (int, float)):
            # Automatically detect timestamp precision
            if time_value >= 1e12:
                # Millisecond-level timestamp, return directly
                return int(time_value)
            else:
                # Second-level timestamp, convert to millisecond-level
                return int(time_value * 1000)

        # Handle string type
        if isinstance(time_value, str):
            # First try parsing as number
            try:
                numeric_value = float(time_value)
                return to_timestamp_ms_universal(numeric_value)
            except ValueError:
                # Not a number, try parsing as ISO format time string
                dt = from_iso_format(time_value)
                return to_timestamp_ms(dt)

        # Handle datetime object
        if isinstance(time_value, datetime.datetime):
            return to_timestamp_ms(time_value)

        # Other types, try converting to string and then parse
        return to_timestamp_ms_universal(str(time_value))

    except Exception as e:
        logger.error(
            "[DateTimeUtils] to_timestamp_ms_universal - Error converting time value %s: %s",
            time_value,
            str(e),
        )
        return 0


def _parse_datetime_core(
    time_value, target_timezone: ZoneInfo = None
) -> datetime.datetime:
    """
    Core datetime parsing logic. Raises exception on failure.

    Supported inputs:
        - datetime object (passed through)
        - ISO format string: "2025-09-15T13:11:15.588000", "2025-09-15T13:11:15.588000Z"
        - Space-separated string: "2025-01-07 09:15:33" (Python 3.11+)
        - With timezone offset: "2025-09-15T13:11:15+08:00"

    Args:
        time_value: datetime object or time string
        target_timezone: Timezone for naive datetime (default: TZ env variable)

    Returns:
        Timezone-aware datetime object

    Raises:
        ValueError: If parsing fails
    """
    # Handle datetime object
    if isinstance(time_value, datetime.datetime):
        dt = time_value
    elif isinstance(time_value, str):
        time_str = time_value.strip()
        # Handle "Z" suffix (UTC)
        if time_str.endswith("Z"):
            time_str = time_str[:-1] + "+00:00"
        # Python 3.11+ fromisoformat supports space-separated format
        dt = datetime.datetime.fromisoformat(time_str)
    else:
        # Other types: convert to string first
        time_str = str(time_value).strip()
        if time_str.endswith("Z"):
            time_str = time_str[:-1] + "+00:00"
        dt = datetime.datetime.fromisoformat(time_str)

    # Add timezone if naive
    if dt.tzinfo is None:
        tz = target_timezone or get_timezone()
        dt_localized = dt.replace(tzinfo=tz)
    else:
        dt_localized = dt

    # Convert to system timezone
    return dt_localized.astimezone(get_timezone())


def from_iso_format(
    create_time, target_timezone: ZoneInfo = None, strict: bool = False
) -> datetime.datetime:
    """
    Parse datetime string or object to timezone-aware datetime.

    Args:
        create_time: datetime object or time string
        target_timezone: Timezone for naive datetime (default: TZ env variable)
        strict: If True, raises ValueError on failure (for data import).
                If False (default), returns current time on failure (for runtime conversion).

    Supported formats:
        - datetime object (passed through)
        - "2025-01-07 09:15:33" (space-separated)
        - "2025-01-07T09:15:33" (ISO T-separated)
        - "2025-01-07 09:15:33.123456" (with microseconds)
        - "2025-01-07T09:15:33+08:00" (with timezone)
        - "2025-01-07T09:15:33Z" (UTC)

    Returns:
        Timezone-aware datetime object. Returns current time if parsing fails (when strict=False).

    Raises:
        ValueError: If strict=True and parsing fails

    Example:
        >>> from_iso_format("2025-01-07 09:15:33")
        datetime.datetime(2025, 1, 7, 9, 15, 33, tzinfo=ZoneInfo('Asia/Shanghai'))

        >>> from_iso_format("invalid", strict=True)
        ValueError: ...
    """
    if strict:
        # Strict mode: raise exception on failure
        return _parse_datetime_core(create_time, target_timezone)
    else:
        # Lenient mode: return current time on failure
        try:
            return _parse_datetime_core(create_time, target_timezone)
        except Exception as e:
            logger.error(
                "[DateTimeUtils] from_iso_format - Error converting time: %s", str(e)
            )
            return get_now_with_timezone()
