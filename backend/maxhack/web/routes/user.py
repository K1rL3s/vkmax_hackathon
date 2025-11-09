from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from maxhack.core.exceptions import EntityNotFound, InvalidValue, NotEnoughRights
from maxhack.core.ids import GroupId, MaxChatId, MaxId, UserId
from maxhack.core.tag.service import TagService
from maxhack.core.user.service import UserService
from maxhack.web.schemas.tag import TagResponse
from maxhack.web.schemas.user import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)

user_router = APIRouter(prefix="/users", tags=["Users"], route_class=DishkaRoute)


@user_router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создание пользователя",
)
async def create_user_route(
    body: UserCreateRequest,
    user_service: FromDishka[UserService],
    session: FromDishka[AsyncSession],
) -> UserResponse:
    try:
        user = await user_service.create_user(
            max_id=MaxId(body.max_id),
            max_chat_id=MaxChatId(body.max_chat_id),
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
        )
        return await UserResponse.from_orm_async(user, session)
    except InvalidValue as e:
        # Конвертируем бизнес-исключение в HTTP 409
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@user_router.get(
    "/{user_id}",
    response_model=UserResponse,
    description="Получить одного пользователя по идентификатору",
)
async def get_user_by_id_route(
    user_id: UserId,
    user_service: FromDishka[UserService],
    session: FromDishka[AsyncSession],
) -> UserResponse:
    try:
        user = await user_service.get_user_by_id(user_id=user_id)
        return await UserResponse.from_orm_async(user, session)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@user_router.patch(
    "/",
    response_model=UserResponse,
    description="Редактирование пользователя",
)
async def update_user_route(
    body: UserUpdateRequest,
    user_service: FromDishka[UserService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> UserResponse:
    try:
        user = await user_service.update_user(
            user_id=master_id,
            first_name=body.first_name,
            last_name=body.last_name,
            phone=body.phone,
        )
        return await UserResponse.from_orm_async(user, session)
    except EntityNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# @user_router.get(
#     "/{user_id}/groups",
#     response_model=UserGroupsResponse,
#     description="Получить список групп, в которых состоит пользователь",
# )
# async def list_user_groups_route(
#     user_id: UserId,
#     user_service: FromDishka[UserService],
#     master_id: UserId = Header(...),
# ) -> UserGroupsResponse:
#     try:
#         result = await user_service.get_user_groups(
#             user_id=user_id,
#             master_id=master_id,
#         )
#         items: list[UserGroupItem] = []
#         for group, role in result:
#             items.append(
#                 UserGroupItem(
#                     group_id=group.id,
#                     name=group.name,
#                     description=group.description,
#                     role_id=role.id,
#                 ),
#             )
#
#         return UserGroupsResponse(groups=items)
#     except EntityNotFound as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
#     except NotEnoughRights as e:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@user_router.get(
    "/{user_id}/groups/{group_id}/tags",
    response_model=list[TagResponse],
    description="Получить список тегов пользователя в рамках группы",
)
async def list_user_tags_route(
    user_id: UserId,
    group_id: GroupId,
    tag_service: FromDishka[TagService],
    session: FromDishka[AsyncSession],
    master_id: UserId = Header(...),
) -> list[TagResponse]:
    try:
        tags = await tag_service.list_user_tags(
            group_id=group_id,
            user_id=user_id,
            master_id=master_id,
        )
        response_tags = [await TagResponse.from_orm_async(tag, session) for tag in tags]
        return response_tags
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRights as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
