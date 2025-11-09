from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.group.service import GroupService
from maxhack.core.ids import GroupId, UserId
from maxhack.core.role.ids import MEMBER_ROLE_ID
from maxhack.core.tag.service import TagService
from maxhack.web.schemas.group import (
    GroupCreateRequest,
    GroupMemberAddRequest,
    GroupMemberResponse,
    GroupMemberUpdateRequest,
    GroupResponse,
    GroupUpdateRequest,
    GroupUserItem,
    GroupUsersResponse,
)
from maxhack.web.schemas.tag import (
    TagCreateRequest,
    TagResponse,
)

group_router = APIRouter(prefix="/groups", tags=["Groups"], route_class=DishkaRoute)


@group_router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создание группы",
)
async def create_group_route(
    body: GroupCreateRequest,
    group_service: FromDishka[GroupService],
) -> GroupResponse:
    try:
        group = await group_service.create_group(
            creator_id=body.creator_id,
            name=body.name,
            description=body.description,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return GroupResponse.model_validate(group)


@group_router.patch(
    "/{group_id}",
    response_model=GroupResponse,
    description="Редактирование группы (только создатель)",
)
async def update_group_route(
    group_id: GroupId,
    body: GroupUpdateRequest,
    group_service: FromDishka[GroupService],
) -> GroupResponse:
    try:
        group = await group_service.update_group(
            group_id=group_id,
            editor_id=body.master_id,
            name=body.name,
            description=body.description,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return GroupResponse.model_validate(group)


@group_router.post(
    "/join",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED,
    description="Добавление пользователя в группу",
)
async def join_group(
    body: GroupMemberAddRequest,
    group_service: FromDishka[GroupService],
) -> GroupMemberResponse:
    try:
        group = await group_service.join_group(
            user_id=body.user_id,
            invite_key=body.invite_key,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return GroupMemberResponse(
        user_id=body.user_id,
        group_id=group.id,
        role_id=MEMBER_ROLE_ID,
    )


@group_router.patch(
    "/{group_id}/users/{user_id}",
    response_model=GroupMemberResponse,
    description="Редактирование связи пользователя и группы",
)
async def update_group_membership(
    body: GroupMemberUpdateRequest,
    group_service: FromDishka[GroupService],
) -> GroupMemberResponse:
    try:
        membership = await group_service.update_membership(
            group_id=body.group_id,
            new_role_id=body.new_role_id,
            slave_id=body.slave_id,
            master_id=body.master_id,
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
    "/{group_id}/users",
    response_model=GroupUsersResponse,
    description="Получить список всех пользователей группы",
)
async def list_group_users_route(
    group_id: GroupId,
    user_id: UserId,
    group_service: FromDishka[GroupService],
) -> GroupUsersResponse:
    try:
        group_users = await group_service.get_group_users(
            group_id=group_id,
            user_id=user_id,
        )
        return GroupUsersResponse(
            users=[
                GroupUserItem(
                    user_id=user_model.id,
                    group_id=group_id,
                    role_id=role_model.id,
                    max_id=user_model.max_id,
                    first_name=user_model.first_name,
                    last_name=user_model.last_name,
                    phone=user_model.phone,
                )
                for user_model, role_model in group_users
            ],
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@group_router.delete(
    "/{group_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление участника из группы",
)
async def remove_group_member_route(
    group_id: GroupId,
    slave_id: UserId,
    master_id: UserId | None,
    group_service: FromDishka[GroupService],
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
    description="Удаление группы (только администратор)",
)
async def delete_group_route(
    group_id: GroupId,
    user_id: UserId,
    group_service: FromDishka[GroupService],
) -> None:
    try:
        await group_service.delete_group(
            group_id=group_id,
            editor_id=user_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@group_router.post(
    "/{group_id}/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создание тега",
)
async def create_tag_route(
    group_id: GroupId,
    body: TagCreateRequest,
    tag_service: FromDishka[TagService],
    session: FromDishka[AsyncSession],
) -> TagResponse:
    try:
        tag = await tag_service.create_tag(
            group_id=group_id,
            master_id=body.master_id,
            name=body.name,
            descriptions=body.descriptions,
            color=body.color,
        )
        return await TagResponse.from_orm_async(tag, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
