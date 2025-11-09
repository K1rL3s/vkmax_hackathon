"""
Унифицированный dumps/loads во избежание проблем с форматами
"""

from typing import Any

import orjson
from pydantic import BaseModel


def dumps(data: Any, *, default: Any = None, raw: bool = False) -> str | bytes:
    if isinstance(data, BaseModel):
        data = data.dict()
    if not raw:
        return orjson.dumps(
            data,
            default=default,
            option=orjson.OPT_NON_STR_KEYS,
        ).decode("utf-8")
    return orjson.dumps(data, default=default, option=orjson.OPT_NON_STR_KEYS)


def loads(data: str | bytes) -> Any:
    return orjson.loads(data)
