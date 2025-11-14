from typing import Literal

from .core import Model
from maxhack.core.enums.notify_mode import NotifyMode


class UserCreateRequest(Model):
    max_id: int
    max_chat_id: int
    first_name: str
    last_name: str | None = None
    phone: str | None = None
    timezone: int = 0


class UserUpdateRequest(Model):
    first_name: str | None = None
    last_name: str | None = None
    photo: str | None = None
    phone: str | None = None
    timezone: int | None = None
    notify_mode: NotifyMode | None = None


class UserResponse(Model):
    id: int
    max_id: int
    max_chat_id: int
    max_photo: str | None = None
    first_name: str
    last_name: str | None = None
    phone: str | None = None
    timezone: int
    notify_mode: NotifyMode


class UserGroupItem(Model):
    group_id: int
    name: str
    description: str | None = None
    role_id: int


class PersonalGroupResponse(Model):
    id: int
    name: Literal["Личная"]
    description: str | None = None
    timezone: int


class UserGroupsResponse(Model):
    groups: list[UserGroupItem]
