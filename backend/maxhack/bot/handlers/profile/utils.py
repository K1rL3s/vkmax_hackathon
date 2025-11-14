from typing import Any
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

from maxhack.core.utils.datehelp import datetime_now


def tz_name_from_latlon(lat: float, lon: float) -> str:
    tf = TimezoneFinder(in_memory=True)
    name = tf.timezone_at(lat=lat, lng=lon)
    if name is None:
        name = tf.certain_timezone_at(lat=lat, lng=lon)
    return name


def utc_offset_minutes(tz_name: str) -> int:
    tz = ZoneInfo(tz_name)
    when = datetime_now()
    aware = when.replace(tzinfo=tz)
    return int(aware.utcoffset().total_seconds() // 60)


def parse_vcard(vcard_str: str) -> dict[str, Any]:
    lines = vcard_str.strip().split("\r\n")
    data = {}

    for line in lines:
        if line.startswith("END:VCARD"):
            break
        if ":" in line:
            key, value = line.split(":", 1)
            if ";" in key:
                field_key, params_str = key.split(";", 1)
                params = {}
                for param in params_str.split(";"):
                    if "=" in param:
                        pkey, pval = param.split("=", 1)
                        params[pkey] = pval
                data[field_key] = {"value": value, "params": params}
            else:
                data[key] = {"value": value, "params": {}}

    return data
