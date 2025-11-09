from datetime import datetime

from maxhack.core.group.service import GroupService
from maxhack.core.ids import UserId, GroupId
from maxhack.infra.database.models import InviteModel
from maxhack.infra.database.repos.invite import InviteRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.utils.utils import generate_invite_key


class InviteService:
    def __init__(
            self,
            invite_repo: InviteRepo,
            group_repo: GroupService,
            user_repo: UserRepo,
    ) -> None:
        self._invite_repo = invite_repo
        self._group_repo = group_repo
        self._user_repo = user_repo

    async def create_invite_link(self, group_id: GroupId, creator_id: UserId,
                                 expires_at: datetime | None) -> InviteModel:
        key = generate_invite_key()
        invite_obj = await self._invite_repo.create(key=key, group_id=group_id, creator_id=creator_id,
                                                    expires_at=expires_at)
        return invite_obj
