from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import GroupId, TagId, UserId
from maxhack.core.tag.service import TagService
from maxhack.web.schemas.tag import (
    TagAssignRequest,
    TagCreateRequest,
    TagResponse,
    TagUpdateRequest,
    TagUserItem,
)

tag_router = APIRouter(
    prefix="/groups/{group_id}/tags",
    tags=["Tags"],
    route_class=DishkaRoute,
)


@tag_router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создание тега",
)
async def create_tag_route(
    group_id: GroupId,
    body: TagCreateRequest,
    tag_service: FromDishka[TagService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> TagResponse:
    try:
        tag = await tag_service.create_tag(
            group_id=group_id,
            master_id=master_id,
            name=body.name,
            descriptions=body.descriptions,
            color=body.color,
        )
        return await TagResponse.from_orm_async(tag, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@tag_router.patch(
    "/{tag_id}",
    response_model=TagResponse,
    description="Редактирование тега",
)
async def update_tag_route(
    group_id: GroupId,
    tag_id: TagId,
    body: TagUpdateRequest,
    tag_service: FromDishka[TagService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> TagResponse:
    try:
        tag = await tag_service.update_tag(
            group_id=group_id,
            tag_id=tag_id,
            master_id=master_id,
            name=body.name,
            descriptions=body.descriptions,
            color=body.color,
        )
        return await TagResponse.from_orm_async(tag, session)
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@tag_router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление тега",
)
async def delete_tag_route(
    group_id: GroupId,
    tag_id: TagId,
    tag_service: FromDishka[TagService],
    master_id: UserId = Header(...),
) -> None:
    try:
        await tag_service.delete_tag(
            group_id=group_id,
            tag_id=tag_id,
            master_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@tag_router.post(
    "/users",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Назначить тег пользователю",
)
async def assign_tag_to_user_route(
    group_id: GroupId,
    body: TagAssignRequest,
    tag_service: FromDishka[TagService],
    master_id: UserId = Header(...),
) -> None:
    try:
        await tag_service.assign_tag_to_user(
            group_id=group_id,
            tag_id=body.tag_id,
            user_id=body.user_id,
            master_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidValue as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@tag_router.delete(
    "/users/{user_id}/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удалить тег у пользователя",
)
async def remove_tag_from_user_route(
    group_id: GroupId,
    tag_id: TagId,
    user_id: UserId,
    tag_service: FromDishka[TagService],
    master_id: UserId = Header(...),
) -> None:
    try:
        await tag_service.remove_tag_from_user(
            group_id=group_id,
            tag_id=tag_id,
            user_id=user_id,
            master_id=master_id,
        )
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@tag_router.get(
    "",
    response_model=list[TagResponse],
    description="Получить список тегов группы",
)
async def list_group_tags_route(
    group_id: GroupId,
    tag_service: FromDishka[TagService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> list[TagResponse]:
    try:
        tags = await tag_service.list_group_tags(
            group_id=group_id,
            master_id=master_id,
        )
        response_tags = [await TagResponse.from_orm_async(tag, session) for tag in tags]
        return response_tags
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@tag_router.get(
    "/{tag_id}/users",
    response_model=list[TagUserItem],
    description="Получить список пользователей, у которых назначен тег",
)
async def list_tag_users_route(
    group_id: GroupId,
    tag_id: TagId,
    tag_service: FromDishka[TagService],
    master_id: UserId = Header(...),
) -> list[TagUserItem]:
    try:
        result = await tag_service.list_tag_users(
            group_id=group_id,
            tag_id=tag_id,
            master_id=master_id,
        )
        users: list[TagUserItem] = []
        for user, role_id in result:
            users.append(
                TagUserItem(
                    user_id=user.id,
                    max_id=user.max_id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone=user.phone,
                    role_id=role_id,
                ),
            )

        return users
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
