from ...core.ids import GroupId, RoleId, TagId, UserId
from .core import Model


class TagCreateRequest(Model):
    master_id: UserId
    name: str
    descriptions: str | None = None
    color: str


class TagUpdateRequest(Model):
    master_id: UserId
    name: str | None = None
    descriptions: str | None = None
    color: str | None = None


class TagResponse(Model):
    id: UserId
    group_id: GroupId
    name: str
    descriptions: str | None = None
    color: str


class TagDeleteRequest(Model):
    master_id: UserId


class TagAssignRequest(Model):
    master_id: UserId
    user_id: UserId
    tag_id: TagId


class TagAssignmentResponse(Model):
    user_id: UserId
    tag_id: TagId


class GroupTagsResponse(Model):
    tags: list[TagResponse]


class UserTagsResponse(Model):
    tags: list[TagResponse]


class TagUserItem(Model):
    user_id: UserId
    max_id: int
    first_name: str
    last_name: str | None = None
    phone: str
    role_id: RoleId


class TagUsersResponse(Model):
    users: list[TagUserItem]
