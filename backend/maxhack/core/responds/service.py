from maxhack.core.exceptions import EntityNotFound, NotEnoughRights
from maxhack.core.ids import EventId, RespondId, UserId
from maxhack.infra.database.models import RespondModel
from maxhack.infra.database.repos.event import EventRepo
from maxhack.infra.database.repos.respond import RespondRepo
from maxhack.infra.database.repos.user import UserRepo


class RespondService:
    def __init__(
        self,
        event_repo: EventRepo,
        user_repo: UserRepo,
        respond_repo: RespondRepo,
    ) -> None:
        self._event_repo = event_repo
        self._user_repo = user_repo
        self._respond_repo = respond_repo

    async def _ensure_respond_exists(self, respond_id: RespondId):
        if not (respond := await self._respond_repo.get_by_id(respond_id)):
            return EntityNotFound("Отклик не найден")
        return respond

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
        event_id: EventId,
        user_id: UserId,
        status: str,
    ) -> RespondModel:
        respond = await self._ensure_respond_exists(respond_id)

        if respond.user_id != user_id:
            raise NotEnoughRights("Пользователь  не может редактировать не свой отклик")
        values = {"status": status}
        respond = await self._respond_repo.update(event_id, **values)
        if respond is None:
            raise EntityNotFound("Отклик не найден")

        return respond
