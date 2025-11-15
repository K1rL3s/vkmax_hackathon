from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from maxhack.core.enums.notify_mode import NotifyMode
from maxhack.core.group.service import GroupService
from maxhack.core.ids import GroupId, UserId
from maxhack.core.invite.service import InviteService
from maxhack.core.max import QRCoder
from maxhack.core.role.ids import CREATOR_ROLE_ID, CREATOR_ROLE_NAME, MEMBER_ROLE_ID
from maxhack.web.dependencies import CurrentUser
from maxhack.web.schemas.group import (
    GetGroupResponse,
    GroupCreateRequest,
    GroupMemberAddRequest,
    GroupMemberResponse,
    GroupMemberUpdateRequest,
    GroupNotifyModeRequest,
    GroupUpdateRequest,
    GroupUserItem,
)
from maxhack.web.schemas.invite import InviteCreateResponse, InviteGetResponse
from maxhack.web.schemas.role import RoleResponse

group_router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
    route_class=DishkaRoute,
)


@group_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Создание группы. Может кто угодно.",
)
async def create_group_route(
    body: GroupCreateRequest,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> GetGroupResponse:
    group = await group_service.create_group(
        master_id=current_user.db_user.id,
        name=body.name,
        description=body.description,
        timezone=body.timezone,
    )

    return GetGroupResponse.model_validate(
        {"group": group, "role": RoleResponse(id=CREATOR_ROLE_ID, name="Босс")},
    )


@group_router.patch(
    "/{group_id}",
    description="""Редактирование группы. Может только "Босс".""",
)
async def update_group_route(
    group_id: GroupId,
    body: GroupUpdateRequest,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> GetGroupResponse:
    group = await group_service.update_group(
        group_id=group_id,
        master_id=current_user.db_user.id,
        **body.model_dump(exclude_none=True),
    )

    return GetGroupResponse.model_validate(
        {
            "group": group,
            "role": RoleResponse(id=CREATOR_ROLE_ID, name=CREATOR_ROLE_NAME),
        },
    )


@group_router.patch(
    "/{group_id}/users/{slave_id}",
    description="""Смена роли юзера в группе. Может только "Босс".""",
)
async def update_group_membership_route(
    group_id: GroupId,
    slave_id: UserId,
    body: GroupMemberUpdateRequest,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> GroupMemberResponse:
    membership = await group_service.update_membership(
        group_id=group_id,
        role_id=body.role_id,
        slave_id=slave_id,
        tags=body.tags,
        master_id=current_user.db_user.id,
    )

    return GroupMemberResponse.model_validate(membership)


@group_router.get(
    "/{group_id}",
    description="Получить группу. Могут только участники группы.",
)
async def get_group(
    *,
    group_id: GroupId,
    current_user: CurrentUser,
    group_service: FromDishka[GroupService],
) -> GetGroupResponse:
    group, role = await group_service.get_group(
        group_id=group_id,
        member_id=current_user.db_user.id,
    )

    return GetGroupResponse.model_validate({"group": group, "role": role})


@group_router.get(
    "/{group_id}/users/{member_id}",
    description="Получить участника группы. Могут только участники группы.",
)
async def get_group_user_route(
    group_id: GroupId,
    member_id: UserId,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> GroupUserItem:
    user = await group_service.get_member(
        group_id=group_id,
        user_id=member_id,
        master_id=current_user.db_user.id,
    )
    return GroupUserItem.model_validate(user)


@group_router.get(
    "/{group_id}/users",
    description="Получить всех пользователей группы. Могут только участники группы.",
)
async def list_group_users_route(
    group_id: GroupId,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> list[GroupUserItem]:
    group_users = await group_service.get_group_users(
        group_id=group_id,
        user_id=current_user.db_user.id,
    )
    return [GroupUserItem.model_validate(u) for u in group_users]


@group_router.delete(
    "/{group_id}/users/{slave_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""
Удаление участника из группы.
"Босс" может удалить всех, "Начальник" не может удалить "Босса"
""".strip(),
)
async def remove_group_member_route(
    group_id: GroupId,
    slave_id: UserId,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> None:
    await group_service.remove_user_from_group(
        group_id=group_id,
        slave_id=slave_id,
        master_id=current_user.db_user.id,
    )


@group_router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""Удалить группы. Может только "Босс".""",
)
async def delete_group_route(
    group_id: GroupId,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> None:
    await group_service.delete_group(
        group_id=group_id,
        editor_id=current_user.db_user.id,
    )


@group_router.get(
    "/{group_id}/invite",
    status_code=status.HTTP_200_OK,
    description="""
Получит ссылку-приглашение в группу.
В группе может быть только одно активное приглашение.
""".strip(),
)
async def get_invite_route(
    group_id: GroupId,
    invite_service: FromDishka[InviteService],
    current_user: CurrentUser,
    qrcoder: FromDishka[QRCoder],
) -> InviteGetResponse:
    invite_obj = await invite_service.get_invite(
        group_id=group_id,
        user_id=current_user.db_user.id,
    )
    return InviteGetResponse(
        invite_key=invite_obj.key,
        invite_link=qrcoder.invite_deeplink(invite_obj.key),
    )


@group_router.post(
    "/{group_id}/invite",
    status_code=status.HTTP_201_CREATED,
    description="""
Создать (перевыпустить) приглашение в группу.
В группе может быть только одно активное приглашение.
""".strip(),
)
async def create_invite_route(
    group_id: GroupId,
    invite_service: FromDishka[InviteService],
    current_user: CurrentUser,
    qrcoder: FromDishka[QRCoder],
) -> InviteCreateResponse:
    invite_obj = await invite_service.recreate_invite(
        group_id=group_id,
        creator_id=current_user.db_user.id,
    )
    return InviteCreateResponse(
        invite_key=invite_obj.key,
        invite_link=qrcoder.invite_deeplink(invite_obj.key),
    )


@group_router.delete(
    "/{group_id}/invite",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""
Удалить приглашение в группу.
В группе может быть только одно активное приглашение, поэтому удалится оно.
""".strip(),
)
async def delete_invite_route(
    group_id: GroupId,
    invite_service: FromDishka[InviteService],
    current_user: CurrentUser,
) -> None:
    await invite_service.delete_invite(
        group_id=group_id,
        user_id=current_user.db_user.id,
    )


# TODO: Удалить на проде
@group_router.post(
    "/join",
    status_code=status.HTTP_201_CREATED,
    description="Добавление пользователя в группу",
)
async def join_group(
    body: GroupMemberAddRequest,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> GroupMemberResponse:
    group = await group_service.join_group(
        user_id=current_user.db_user.id,
        invite_key=body.invite_key,
    )

    return GroupMemberResponse(
        user_id=current_user.db_user.id,
        group_id=group.id,
        role_id=MEMBER_ROLE_ID,
        notify_mode=NotifyMode.DEFAULT,
    )


@group_router.patch(
    "/{group_id}/notify",
    status_code=status.HTTP_200_OK,
    description="Изменить режим уведомлений в группе для самого себя.",
)
async def update_group_notify_mode(
    group_id: GroupId,
    body: GroupNotifyModeRequest,
    group_service: FromDishka[GroupService],
    current_user: CurrentUser,
) -> GroupMemberResponse:
    membership = await group_service.update_membership(
        group_id=group_id,
        slave_id=current_user.db_user.id,
        master_id=current_user.db_user.id,
        role_id=None,
        tags=None,
        notify_mode=body.notify_mode,
    )

    return GroupMemberResponse.model_validate(membership)
