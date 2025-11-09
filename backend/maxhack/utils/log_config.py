import logging
import warnings
from typing import Literal

import aiomisc
from fastapi import FastAPI
from sqlalchemy import exc


def configure_logging(enable_additional_debug: bool = True) -> None:
    """
    Отключает дебаг информацию для библиотек, при необходимости
    """
    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[-1])

    logging.getLogger("AdditionalDebug").info("enabled")
    if not enable_additional_debug:
        logging.getLogger("websockets.protocol:server").setLevel(logging.ERROR)
        logging.getLogger("websockets.protocol").setLevel(logging.ERROR)
        logging.getLogger("databases").setLevel(logging.ERROR)
        logging.getLogger("sqlalchemy.engine.base.Engine").setLevel(logging.ERROR)
        logging.getLogger("aiokafka.consumer.group_coordinator").setLevel(logging.ERROR)
        logging.getLogger("aiokafka.consumer.group_coordinator").setLevel(logging.ERROR)
        logging.getLogger("aiokafka.consumer.group_coordinator").setLevel(logging.ERROR)
        logging.getLogger("aiokafka.conn").setLevel(logging.ERROR)
        logging.getLogger("aiokafka.consumer.fetcher").setLevel(logging.ERROR)
        logging.getLogger("multipart.multipart").setLevel(logging.ERROR)

        warnings.simplefilter("ignore", category=exc.SAWarning)
        # Это warning, который выплёвывает fastapi, на нашу обвязку field_schema при указании hidden=True
        warnings.filterwarnings("ignore", message=".* field is being hidden")
    else:
        logging.getLogger("sqlalchemy.engine.base.Engine").setLevel(logging.INFO)


def set_logging(
    level: Literal["DEBUG", "INFO", "ERROR", "WARNING"] = "DEBUG",
    enable_additional_debug: bool = True,
    app: FastAPI | None = None,
) -> None:
    """
    Устанавливает конфигурацию для логирования.

    Необходимо вызывать как можно раньше
    :param level: уровень выводимых логов
    """
    log_level = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
    }[level]

    configure_logging(enable_additional_debug=enable_additional_debug)

    aiomisc.log.basic_config(
        level=log_level,
        force=True,
        foramt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
