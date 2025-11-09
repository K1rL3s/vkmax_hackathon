import locale
import logging

from maxhack.logger.inject import InjectFilter


def setup_logger(log_level: str) -> None:
    logging.getLogger().setLevel(logging.getLevelName(log_level))
    locale.setlocale(category=locale.LC_ALL, locale="ru_RU.UTF-8")

    # чтобы писались как все:
    get_logger("maxo", groups=("maxo", "max"))
    get_logger("maxo.dispatcher", groups=("maxo", "max"))
    get_logger("maxo.long_polling", groups=("maxo", "max"))
    get_logger("maxo_dialog", groups=("maxo", "max"))
    get_logger("retejo", groups=("retejo",))
    get_logger("retejo.http.method", groups=("retejo",))
    get_logger("retejo.http.request", groups=("retejo",))
    get_logger("taskiq", groups=("taskiq", "scheduler"))


def get_logger(
    name: str,
    *,
    log_level: str | int | None = None,
    groups: tuple[str, ...] | str = (),
) -> logging.Logger:
    """
    Ахтунг! Если был зарегистрирован логер name=<name> и groups=<groups>,
    то при регистрации логера name=<name> и groups=<another-groups>
    второй логер будет иметь группы первого.
    Фиксить ли?
    """
    logger = logging.getLogger(name)
    if log_level is not None:
        logger.setLevel(log_level)

    # Проверка, чтобы не добавлять обработчик повторно
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = _stream_handler(groups)
        logger.addHandler(stream_handler)

    return logger


def _stream_handler(groups: tuple[str, ...] | str) -> logging.StreamHandler:
    stream_handler = logging.StreamHandler()

    if isinstance(groups, str):
        groups = (groups,)

    # stream_handler.setFormatter(JsonFormatter(groups=groups))
    stream_handler.addFilter(InjectFilter())

    return stream_handler
