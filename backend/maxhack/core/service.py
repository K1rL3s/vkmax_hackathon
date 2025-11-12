from abc import ABC

from maxhack.core.exceptions import (
    EventNotFound,
    GroupNotFound,
    NotEnoughRights,
    RespondNotFound,
    TagNotFound,
    UserNotFound,
)
from maxhack.core.ids import EventId, GroupId, RespondId, RoleId, TagId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID, MEMBER_ROLE_ID
from maxhack.infra.database.models import (
    EventModel,
    GroupModel,
    RespondModel,
    TagModel,
    UserModel,
    UsersToGroupsModel,
)
from maxhack.infra.database.repos.event import EventRepo
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.invite import InviteRepo
from maxhack.infra.database.repos.respond import RespondRepo
from maxhack.infra.database.repos.role import RoleRepo
from maxhack.infra.database.repos.tag import TagRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo


class BaseService(ABC):
    def __init__(
        self,
        event_repo: EventRepo,
        tag_repo: TagRepo,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        users_to_groups_repo: UsersToGroupsRepo,
        respond_repo: RespondRepo,
        invite_repo: InviteRepo,
        role_repo: RoleRepo,
    ) -> None:
        self._event_repo = event_repo
        self._tag_repo = tag_repo
        self._group_repo = group_repo
        self._user_repo = user_repo
        self._users_to_groups_repo = users_to_groups_repo
        self._respond_repo = respond_repo
        self._invite_repo = invite_repo
        self._role_repo = role_repo

    async def _ensure_group_exists(self, group_id: GroupId) -> GroupModel:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise GroupNotFound
        return group

    async def _ensure_user_exists(self, user_id: UserId) -> UserModel:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound
        return user

    async def _ensure_event_exists(self, event_id: EventId) -> EventModel:
        event = await self._event_repo.get_by_id(event_id)
        if event is None:
            raise EventNotFound
        return event

    async def _ensure_tag_exists(self, tag_id: TagId) -> TagModel:
        tag = await self._tag_repo.get_by_id(tag_id)
        if tag is None:
            raise TagNotFound
        return tag

    async def _ensure_membership_role(
        self,
        user_id: UserId,
        group_id: GroupId,
        allowed_roles: tuple[RoleId, ...] = (
            CREATOR_ROLE_ID,
            EDITOR_ROLE_ID,
            MEMBER_ROLE_ID,
        ),
    ) -> UsersToGroupsModel:
        membership = await self._users_to_groups_repo.get_membership(
            user_id=user_id,
            group_id=group_id,
        )
        if membership is None or membership.role_id not in allowed_roles:
            raise NotEnoughRights("Недостаточно прав")
        return membership

    async def _ensure_respond_exists(self, respond_id: RespondId) -> RespondModel:
        respond = await self._respond_repo.get_by_id(respond_id)
        if not respond:
            raise RespondNotFound
        return respond
