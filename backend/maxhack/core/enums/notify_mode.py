from enum import StrEnum


class NotifyMode(StrEnum):
    DEFAULT = "DEFAULT"  # все уведомления со звуком
    SILENT = "SILENT"  # все уведомления без звука
    DISABLE = "DISABLE"  # никаких уведомлений
