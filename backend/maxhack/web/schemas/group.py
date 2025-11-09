from maxhack.core.ids import GroupId, InviteKey, MaxId, RoleId, UserId

from .core import Model


class GroupCreateRequest(Model):
    name: str
    description: str | None = None
    creator_id: UserId


class GroupUpdateRequest(Model):
    master_id: UserId
    name: str | None = None
    description: str | None = None


class GroupResponse(Model):
    id: GroupId
    name: str
    description: str | None = None

    class Config(Model.Config):
        orm_mode = True


class GroupMemberAddRequest(Model):
    user_id: UserId
    invite_key: InviteKey


class GroupMemberUpdateRequest(Model):
    master_id: UserId
    slave_id: UserId
    group_id: GroupId
    new_role_id: RoleId


class GroupMemberResponse(Model):
    user_id: UserId
    group_id: GroupId
    role_id: RoleId

    class Config(Model.Config):
        orm_mode = True


class GroupUserItem(Model):
    user_id: UserId
    group_id: GroupId
    role_id: RoleId
    max_id: MaxId
    first_name: str
    last_name: str | None = None
    phone: str


class GroupUsersResponse(Model):
    users: list[GroupUserItem]
