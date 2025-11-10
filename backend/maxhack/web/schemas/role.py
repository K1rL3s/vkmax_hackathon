from typing import Literal

from pydantic import Field

from maxhack.web.schemas.core import Model


class RoleResponse(Model):
    id: int
    name: Literal["Босс", "Начальник", "Участник"] = Field(
        ...,
        examples=["Босс"],
    )
