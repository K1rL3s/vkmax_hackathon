"""
Инициализация моделей
"""

from .base import BaseAlchemyModel
from .event import EventModel
from .event_notify import EventNotifyModel
from .group import GroupModel
from .invite import InviteModel
from .respond import RespondModel
from .role import RoleModel
from .tag import TagModel
from .tags_to_events import TagsToEvents
from .user import UserModel
from .users_to_events import UsersToEvents
from .users_to_groups import UsersToGroupsModel
from .users_to_tags import UsersToTagsModel

__all__ = (
    "BaseAlchemyModel",
    "EventModel",
    "EventNotifyModel",
    "GroupModel",
    "InviteModel",
    "RespondModel",
    "RoleModel",
    "TagModel",
    "TagsToEvents",
    "UserModel",
    "UsersToEvents",
    "UsersToGroupsModel",
    "UsersToTagsModel",
)
