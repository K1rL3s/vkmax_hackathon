from maxhack.core.enums.respond_action import RespondStatus
from maxhack.core.exceptions import NotEnoughRights, RespondNotFound
from maxhack.core.ids import EventId, RespondId, UserId
from maxhack.core.service import BaseService
from maxhack.database.models import RespondModel
from maxhack.logger.setup import get_logger

logger = get_logger(__name__)


class RespondService(BaseService):
    async def create(
        self,
        user_ids: list[UserId],
        event_id: EventId,
        status: str,
    ):
        logger.debug(
            f"Creating responds for users {user_ids} for event {event_id} with status {status}",
        )
        await self._respond_repo.create(user_ids, event_id, status)
        logger.info(
            f"Responds for users {user_ids} for event {event_id} created successfully",
        )

    async def update(
        self,
        respond_id: RespondId,
        user_id: UserId,
        status: RespondStatus,
    ) -> RespondModel:
        logger.debug(
            f"Updating respond {respond_id} by user {user_id} with status {status}",
        )
        respond = await self._ensure_respond_exists(respond_id)

        if respond.user_id != user_id:
            logger.warning(
                f"User {user_id} has no rights to update respond {respond_id}",
            )
            raise NotEnoughRights

        updated_respond = await self._respond_repo.update(respond_id, status=status)
        if updated_respond is None:
            logger.error(f"Respond {respond_id} not found for update")
            raise RespondNotFound

        logger.info(f"Respond {respond_id} updated successfully")
        return updated_respond

    async def get_all_responds(
        self,
        event_id: EventId,
        user_id: UserId,
    ) -> list[RespondModel]:
        logger.debug(f"Getting all responds for event {event_id} by user {user_id}")
        await self._ensure_user_exists(user_id)
        event = await self._ensure_event_exists(event_id)
        await self._ensure_membership_role(user_id=user_id, group_id=event.group_id)

        responds = await self._respond_repo.get_all_responds(event_id)
        logger.info(f"Found {len(responds)} responds for event {event_id}")
        return responds

    async def get_user_respond(
        self,
        event_id: EventId,
        user_id: UserId,
    ) -> RespondModel:
        logger.debug(f"Getting respond for user {user_id} for event {event_id}")
        await self._ensure_user_exists(user_id)
        event = await self._ensure_event_exists(event_id)
        await self._ensure_membership_role(user_id=user_id, group_id=event.group_id)

        respond = await self._respond_repo.get_user_respond(event_id, user_id)
        if respond is None:
            logger.error(f"Respond not found for user {user_id} for event {event_id}")
            raise RespondNotFound

        logger.info(
            f"Respond {respond.id} found for user {user_id} for event {event_id}",
        )
        return respond
