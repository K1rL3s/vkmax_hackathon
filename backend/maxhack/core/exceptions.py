class MaxHackError(Exception):
    pass


class EntityNotFound(MaxHackError, LookupError):
    pass


class NotEnoughRights(MaxHackError, PermissionError):
    pass


class InvalidValue(MaxHackError, ValueError):
    pass
