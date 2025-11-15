import datetime
from typing import Final

UTC_FROM_UTC: Final = 0
UTC_TIMEZONE: Final = datetime.timezone(
    offset=datetime.timedelta(hours=UTC_FROM_UTC),
)
MOSCOW_TIMEZONE_MINUTES = 180


def datetime_now(tz_offset: int = UTC_FROM_UTC) -> datetime.datetime:
    return datetime.datetime.now(
        tz=datetime.timezone(offset=datetime.timedelta(hours=tz_offset)),
    )
