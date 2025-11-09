import datetime
from typing import Final

MOSCOW_FROM_UTC: Final = 3
MOSCOW_TIMEZONE: Final = datetime.timezone(
    offset=datetime.timedelta(hours=MOSCOW_FROM_UTC),
)


def datetime_now(tz_offset: int = MOSCOW_FROM_UTC) -> datetime.datetime:
    return datetime.datetime.now(
        tz=datetime.timezone(offset=datetime.timedelta(hours=tz_offset)),
    )
