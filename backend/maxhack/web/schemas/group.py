from maxhack.core.ids import GroupId, InviteKey, MaxId, RoleId, UserId

from .core import Model


class GroupCreateRequest(Model):
    name: str
    description: str | None = None


class GroupUpdateRequest(Model):
    name: str | None = None
    description: str | None = None


class GroupResponse(Model):
    id: GroupId
    name: str
    description: str | None = None



class GroupMemberAddRequest(Model):
    invite_key: InviteKey


class GroupMemberUpdateRequest(Model):
    slave_id: UserId
    group_id: GroupId
    new_role_id: RoleId


class GroupMemberResponse(Model):
    user_id: UserId
    group_id: GroupId
    role_id: RoleId



class GroupUserItem(Model):
    user_id: UserId
    group_id: GroupId
    role_id: RoleId
    role_name: str
    max_id: MaxId
    first_name: str
    last_name: str | None = None
    phone: str
