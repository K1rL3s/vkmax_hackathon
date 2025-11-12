from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Header, status

from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.group.service import GroupService
from maxhack.core.ids import GroupId, InviteKey, UserId
from maxhack.core.invite.service import InviteService
from maxhack.core.role.ids import CREATOR_ROLE_ID, CREATOR_ROLE_NAME, MEMBER_ROLE_ID
from maxhack.web.schemas.group import (
    GetGroupResponse,
    GroupCreateRequest,
    GroupMemberAddRequest,
    GroupMemberResponse,
    GroupMemberUpdateRequest,
    GroupUpdateRequest,
    GroupUserItem,
)
from maxhack.web.schemas.invite import InviteCreateResponse
from maxhack.web.schemas.role import RoleResponse

group_router = APIRouter(prefix="/groups", tags=["Groups"], route_class=DishkaRoute)


@group_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Создание группы. Может кто угодно.",
)
async def create_group_route(
    body: GroupCreateRequest,
    group_service: FromDishka[GroupService],
    master_id: UserId = Header(...),
) -> GetGroupResponse:
    try:
        group = await group_service.create_group(
            creator_id=master_id,
            name=body.name,
            description=body.description,
            timezone=body.timezone,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

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
    master_id: UserId = Header(...),
) -> GetGroupResponse:
    try:
        group = await group_service.update_group(
            group_id=group_id,
            editor_id=master_id,
            **body.model_dump(exclude_none=True),
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

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
async def update_group_membership(
    group_id: GroupId,
    slave_id: UserId,
    body: GroupMemberUpdateRequest,
    group_service: FromDishka[GroupService],
    master_id: UserId = Header(...),
) -> GroupMemberResponse:
    try:
        membership = await group_service.update_membership(
            group_id=group_id,
            role_id=body.role_id,
            slave_id=slave_id,
            tags=body.tags,
            master_id=master_id,
        )

        return GroupMemberResponse(
            user_id=membership.user_id,
            group_id=membership.group_id,
            role_id=membership.role_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    # TODO: Вернуть схему


@group_router.get(
    "/{group_id}",
    description="Получить группу. Могут только участники группы.",
)
async def get_group(
    *,
    group_id: GroupId,
    master_id: UserId = Header(...),
    group_service: FromDishka[GroupService],
) -> GetGroupResponse:
    try:
        group, role = await group_service.get_group(
            group_id=group_id,
            member_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return GetGroupResponse.model_validate({"group": group, "role": role})


@group_router.get(
    "/{group_id}/users/{member_id}",
    description="Получить участника группы. Могут только участники группы.",
)
async def get_group_user_route(
    group_id: GroupId,
    member_id: UserId,
    group_service: FromDishka[GroupService],
    master_id: UserId = Header(...),
) -> GroupUserItem:
    try:
        user = await group_service.get_member(
            group_id=group_id,
            user_id=member_id,
            master_id=master_id,
        )
        return GroupUserItem.model_validate(user)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@group_router.get(
    "/{group_id}/users",
    description="Получить всех пользователей группы. Могут только участники группы.",
)
async def list_group_users_route(
    group_id: GroupId,
    group_service: FromDishka[GroupService],
    master_id: UserId = Header(...),
) -> list[GroupUserItem]:
    try:
        group_users = await group_service.get_group_users(
            group_id=group_id,
            user_id=master_id,
        )
        return [GroupUserItem.model_validate(u) for u in group_users]
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
    master_id: UserId = Header(...),
) -> None:
    try:
        await group_service.remove_user_from_group(
            group_id=group_id,
            slave_id=slave_id,
            master_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@group_router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""Удалить группы. Может только "Босс".""",
)
async def delete_group_route(
    group_id: GroupId,
    group_service: FromDishka[GroupService],
    master_id: UserId = Header(...),
) -> None:
    try:
        await group_service.delete_group(
            group_id=group_id,
            editor_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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
    master_id: UserId = Header(...),
) -> InviteCreateResponse:
    invite_obj = await invite_service.recreate_invite(
        group_id=group_id,
        creator_id=master_id,
    )
    return InviteCreateResponse(invite_key=InviteKey(invite_obj.key))


# TODO: Удалить на проде
@group_router.post(
    "/join",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED,
    description="Добавление пользователя в группу",
)
async def join_group(
    body: GroupMemberAddRequest,
    group_service: FromDishka[GroupService],
    master_id: UserId = Header(...),
) -> GroupMemberResponse:
    try:
        group = await group_service.join_group(
            user_id=master_id,
            invite_key=body.invite_key,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return GroupMemberResponse(
        user_id=master_id,
        group_id=group.id,
        role_id=MEMBER_ROLE_ID,
    )
