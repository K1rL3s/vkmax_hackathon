from maxhack.core.enums.respond_action import RespondStatus
from maxhack.core.exceptions import NotEnoughRights, RespondNotFound
from maxhack.core.ids import EventId, RespondId, UserId
from maxhack.core.service import BaseService
from maxhack.infra.database.models import RespondModel


class RespondService(BaseService):
    async def create(
        self,
        user_ids: list[UserId],
        event_id: EventId,
        status: str,
    ):
        await self._respond_repo.create(user_ids, event_id, status)

    async def update(
        self,
        respond_id: RespondId,
        user_id: UserId,
        status: RespondStatus,
    ) -> RespondModel:
        respond = await self._ensure_respond_exists(respond_id)

        if respond.user_id != user_id:
            raise NotEnoughRights

        respond = await self._respond_repo.update(respond_id, status=status)
        if respond is None:
            raise RespondNotFound

        return respond

    async def get_all_responds(
        self,
        event_id: EventId,
        user_id: UserId,
    ) -> list[RespondModel]:
        await self._ensure_user_exists(user_id)
        event = await self._ensure_event_exists(event_id)
        await self._ensure_membership_role(user_id=user_id, group_id=event.group_id)

        return await self._respond_repo.get_all_responds(event_id)

    async def get_user_respond(
        self,
        event_id: EventId,
        user_id: UserId,
    ) -> RespondModel:
        await self._ensure_user_exists(user_id)
        event = await self._ensure_event_exists(event_id)
        await self._ensure_membership_role(user_id=user_id, group_id=event.group_id)

        respond = await self._respond_repo.get_user_respond(event_id, user_id)
        if respond is None:
            raise RespondNotFound

        return respond
