from typing import Any, Self

from pydantic import Field
from pydantic.config import ExtraValues

from maxhack.core.ids import GroupId, InviteKey, MaxId, RoleId, TagId, UserId
from maxhack.infra.database.models.users_to_groups import UsersToGroupsModel
from maxhack.web.schemas.role import RoleResponse

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
    role_id: RoleId | None = Field(
        None,
        description="Идентификатор роли",
        examples=[1, 2, 3],
    )
    tags: list[TagId] | None = Field(
        None,
        description="Список идентификаторов тегов",
    )


class GroupMemberResponse(Model):
    user_id: UserId
    group_id: GroupId
    role_id: RoleId


class GroupUserItem(Model):
    user_id: UserId
    group_id: GroupId
    role: RoleResponse
    max_id: MaxId
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None

    @classmethod
    def model_validate(
        cls,
        obj: UsersToGroupsModel,
        *,
        strict: bool | None = None,
        extra: None | ExtraValues = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        return super().model_validate(
            cls(
                user_id=obj.user_id,
                group_id=obj.group_id,
                role=RoleResponse.model_validate(obj.role),
                max_id=obj.user.max_id,
                first_name=obj.user.first_name,
                last_name=obj.user.last_name,
                phone=obj.user.phone,
            ),
            strict=strict,
            extra=extra,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )
