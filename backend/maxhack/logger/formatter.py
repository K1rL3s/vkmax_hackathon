import json
import logging
from datetime import datetime

from maxhack.core.utils.datehelp import MOSCOW_TIMEZONE

DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        datefmt: str = DEFAULT_DATETIME_FORMAT,
        groups: tuple[str, ...],
    ) -> None:
        super().__init__(datefmt=datefmt)
        self.groups = groups

    def format(self, record: logging.LogRecord) -> str:
        logging_data = {
            "level": record.levelname,
            "time": self.format_time(record, datefmt=self.datefmt),
            "message": record.getMessage(),
            "lineno": record.lineno,
            "logger_name": record.name,
            "exception": None,
        }
        maxo_data = {
            "update_id": getattr(record, "update_id", None),
            "max_id": getattr(record, "max_id", None),
            "start_state": getattr(record, "start_state", None),
            "end_state": getattr(record, "end_state", None),
            "event_type": getattr(record, "event_type", None),
        }
        scheduler_data = {
            "task_id": getattr(record, "scheduler_task_id", None),
            "task_name": getattr(record, "scheduler_task_name", None),
        }
        extra_data = {
            **getattr(record, "extra_data", {}),
            **getattr(record, "meta", {}),
        }

        if record.exc_info:
            logging_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            {**logging_data, **maxo_data, **scheduler_data, **extra_data},
            ensure_ascii=False,
        )

    def format_time(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        ct = datetime.fromtimestamp(record.created, tz=MOSCOW_TIMEZONE)
        if datefmt:
            return ct.strftime(datefmt)
        return str(ct)
