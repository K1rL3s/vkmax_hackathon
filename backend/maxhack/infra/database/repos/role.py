from sqlalchemy import select

from maxhack.core.ids import RoleId
from maxhack.infra.database.models import RoleModel
from maxhack.infra.database.repos.base import BaseAlchemyRepo


class RoleRepo(BaseAlchemyRepo):
    async def get_role(self, role_id: RoleId) -> RoleModel | None:
        stmt = select(RoleModel).where(
            RoleModel.id == role_id,
            RoleModel.is_not_deleted,
        )
        return await self._session.scalar(stmt)
