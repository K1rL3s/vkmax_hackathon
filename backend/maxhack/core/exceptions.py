class MaxHackError(Exception):
    pass


class EntityNotFound(MaxHackError, LookupError):
    pass


class UserNotFound(EntityNotFound):
    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)


class GroupNotFound(EntityNotFound):
    def __init__(self, message: str = "Group not found") -> None:
        super().__init__(message)


class InviteNotFound(EntityNotFound):
    def __init__(self, message: str = "Invite not found") -> None:
        super().__init__(message)


class EventNotFound(EntityNotFound):
    def __init__(self, message: str = "Event not found") -> None:
        super().__init__(message)


class TagNotFound(EntityNotFound):
    def __init__(self, message: str = "Tag not found") -> None:
        super().__init__(message)


class TagAssignmentNotFound(EntityNotFound):
    def __init__(self, message: str = "Tag assignment not found") -> None:
        super().__init__(message)


class RespondNotFound(EntityNotFound):
    def __init__(self, message: str = "Respond not found") -> None:
        super().__init__(message)


class ParticipantNotFound(EntityNotFound):
    def __init__(self, message: str = "Participant not found") -> None:
        super().__init__(message)


class NotEnoughRights(MaxHackError, PermissionError):
    def __init__(self, message: str = "Недостаточно прав") -> None:
        super().__init__(message)


class InvalidValue(MaxHackError, ValueError):
    pass
