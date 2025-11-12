from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, override

from maxhack.core.ids import GroupId, TagId, UserId
from maxhack.core.model import DomainModel
from maxhack.utils.utils import create_cron_expression

EventType = Literal["event"]


@dataclass(kw_only=True)
class Cron(DomainModel):
    date: datetime | None = field(default=None)
    every_day: bool = field(default=False)
    every_week: bool = field(default=False)
    every_month: bool = field(default=False)

    @property
    def expression(self) -> str:
        return create_cron_expression(
            self.date,
            self.every_day,
            self.every_week,
            self.every_month,
        )

    @property
    def is_cycle(self) -> bool:
        return self.every_day or self.every_week or self.every_month


@dataclass(kw_only=True)
class EventCreate(DomainModel):
    title: str
    cron: Cron
    creator_id: UserId
    description: str = field(default="")
    event_date: datetime | None = field(default=None)
    type: EventType = field(default="event")
    timezone: int | None = field(default=None)
    group_id: GroupId
    participants_ids: list[UserId] = field(default_factory=list[UserId])
    tags_ids: list[TagId] = field(default_factory=list[TagId])
    minutes_before: list[int] = field(default_factory=list)


@dataclass(kw_only=True)
class EventUpdate(DomainModel):
    title: str | None = field(default=None)
    description: str | None = field(default=None)
    type: str | None = field(default=None)
    timezone: int | None = field(default=None)
    cron: Cron | None = field(default=None)

    @override
    def to_dict(
        self,
        exclude: set[str] | None = None,
        exclude_none: bool = False,
    ) -> dict[str, Any]:
        obj = super().to_dict(exclude=exclude, exclude_none=exclude_none)
        if self.cron:
            obj["cron"] = self.cron.expression
        return obj
