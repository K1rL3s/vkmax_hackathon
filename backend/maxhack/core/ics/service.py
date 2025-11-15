from datetime import UTC, datetime, timedelta, timezone
from typing import TypedDict

from croniter import croniter
from icalendar import Calendar, Event as ICalEvent

from maxhack.core.event.models import Cron, EventCreate
from maxhack.core.event.service import EventService
from maxhack.core.exceptions import GroupNotFound
from maxhack.core.ids import GroupId, UserId
from maxhack.core.role.ids import CREATOR_ROLE_ID, EDITOR_ROLE_ID
from maxhack.core.service import BaseService
from maxhack.core.utils.datehelp import UTC_TIMEZONE
from maxhack.database.models import EventModel, GroupModel
from maxhack.database.repos.event import EventRepo
from maxhack.database.repos.group import GroupRepo
from maxhack.database.repos.invite import InviteRepo
from maxhack.database.repos.respond import RespondRepo
from maxhack.database.repos.role import RoleRepo
from maxhack.database.repos.tag import TagRepo
from maxhack.database.repos.user import UserRepo
from maxhack.database.repos.users_to_groups import UsersToGroupsRepo
from maxhack.logger.setup import get_logger

logger = get_logger(__name__)


class ParsedICSEvent(TypedDict):
    """Структура события, распарсенного из .ics файла."""

    title: str
    description: str | None
    date: datetime
    duration: int
    timezone: int
    every_day: bool
    every_week: bool
    every_month: bool


class IcsService(BaseService):
    def __init__(
        self,
        event_service: EventService,
        event_repo: EventRepo,
        tag_repo: TagRepo,
        group_repo: GroupRepo,
        user_repo: UserRepo,
        users_to_groups_repo: UsersToGroupsRepo,
        respond_repo: RespondRepo,
        invite_repo: InviteRepo,
        role_repo: RoleRepo,
    ) -> None:
        super().__init__(
            event_repo=event_repo,
            tag_repo=tag_repo,
            group_repo=group_repo,
            user_repo=user_repo,
            users_to_groups_repo=users_to_groups_repo,
            respond_repo=respond_repo,
            invite_repo=invite_repo,
            role_repo=role_repo,
        )
        self._event_service = event_service

    def generate_ics(
        self,
        events: list[EventModel],
        groups: dict[GroupId, GroupModel],
        user_timezone: timezone,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> bytes:
        """Генерирует .ics файл для списка событий.

        Args:
            events: Список событий для экспорта
            groups: Словарь групп по group_id для получения названий групп
            start_date: Начальная дата для генерации повторяющихся событий (по умолчанию сегодня)
            end_date: Конечная дата для генерации повторяющихся событий (по умолчанию через год)

        Returns:
            bytes: Содержимое .ics файла
        """
        cal = Calendar()
        cal.add("prodid", "-//MaxHack Calendar//EN")
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        cal.add("method", "PUBLISH")

        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=365)

        current_time = datetime.now(UTC)

        for event in events:
            if event.event_happened and not event.is_cycle:
                continue
            group = groups.get(event.group_id)
            organizer_name = group.name if group else "Unknown Group"

            try:
                event_start_date = start_date.replace(tzinfo=user_timezone)
                cron = croniter(event.cron, event_start_date)
            except Exception:
                continue

            event_count = 0
            max_events = 1000
            last_date = None

            while event_count < max_events:
                try:
                    next_date = cron.get_next(datetime)
                    if next_date.tzinfo is None:
                        next_date = next_date.replace(tzinfo=user_timezone)
                    else:
                        next_date = next_date.astimezone(user_timezone)

                    if next_date > end_date.replace(tzinfo=user_timezone):
                        break

                    if last_date and next_date <= last_date:
                        break

                    if next_date < current_time.replace(tzinfo=user_timezone):
                        continue

                    ical_event = ICalEvent()
                    ical_event.add("summary", event.title)
                    ical_event.add("dtstart", next_date)
                    ical_event.add("dtstamp", datetime.now(UTC))

                    if event.duration:
                        end_datetime = next_date + timedelta(minutes=event.duration)
                        ical_event.add("dtend", end_datetime)
                    else:
                        ical_event.add("dtend", next_date + timedelta(hours=1))

                    if event.description:
                        ical_event.add("description", event.description)

                    ical_event.add("organizer", f"CN={organizer_name}:mailto:")

                    ical_event.add(
                        "uid",
                        f"event-{event.id}-{int(next_date.timestamp())}@maxhack",
                    )

                    cal.add_component(ical_event)
                    event_count += 1
                    last_date = next_date

                    if not event.is_cycle:
                        break

                except Exception:
                    break

        ics_bytes = cal.to_ical()
        return ics_bytes

    def parse_ics(self, ics_content: bytes) -> list[ParsedICSEvent]:
        """Парсит .ics файл и возвращает список событий для импорта.

        Args:
            ics_content: Содержимое .ics файла в формате bytes

        Returns:
            list[ParsedICSEvent]: Список распарсенных событий
        """
        events: list[ParsedICSEvent] = []
        try:
            cal = Calendar.from_ical(ics_content)
        except Exception:
            return events

        for component in cal.walk():
            if component.name != "VEVENT":
                continue

            try:
                summary = component.get("summary")
                if not summary:
                    continue
                title = str(summary)

                description = component.get("description")
                description_str = str(description) if description else None

                dtstart = component.get("dtstart")
                if not dtstart:
                    continue

                start_dt = dtstart.dt
                if isinstance(start_dt, datetime):
                    if start_dt.tzinfo:
                        utc_offset = start_dt.utcoffset()
                        if utc_offset:
                            timezone_offset_minutes = int(
                                utc_offset.total_seconds() / 60,
                            )
                        else:
                            timezone_offset_minutes = 0
                        start_dt = start_dt.astimezone(UTC_TIMEZONE)
                    else:
                        timezone_offset_minutes = 0
                        start_dt = start_dt.replace(tzinfo=UTC_TIMEZONE)
                else:
                    start_dt = datetime.combine(start_dt, datetime.min.time())
                    start_dt = start_dt.replace(tzinfo=UTC_TIMEZONE)
                    timezone_offset_minutes = 0

                dtend = component.get("dtend")
                duration_minutes = 60
                if dtend:
                    end_dt = dtend.dt
                    if isinstance(end_dt, datetime):
                        if end_dt.tzinfo:
                            end_dt = end_dt.astimezone(UTC_TIMEZONE)
                        else:
                            end_dt = end_dt.replace(tzinfo=UTC_TIMEZONE)
                        duration_delta = end_dt - start_dt
                        duration_minutes = int(duration_delta.total_seconds() / 60)
                        if duration_minutes <= 0:
                            duration_minutes = 60

                every_day = False
                every_week = False
                every_month = False

                rrule = component.get("rrule")
                if rrule:
                    freq = rrule.get("FREQ")
                    if freq:
                        freq_str = str(freq).upper()
                        if freq_str == "DAILY":
                            every_day = True
                        elif freq_str == "WEEKLY":
                            every_week = True
                        elif freq_str == "MONTHLY":
                            every_month = True

                events.append(
                    {
                        "title": title,
                        "description": description_str,
                        "date": start_dt,
                        "duration": duration_minutes,
                        "timezone": timezone_offset_minutes,
                        "every_day": every_day,
                        "every_week": every_week,
                        "every_month": every_month,
                    },
                )

            except Exception:
                continue

        return events

    async def import_events(
        self,
        user_id: UserId,
        ics_content: bytes,
    ) -> list[EventModel]:
        """Импортирует события из .ics файла в личную группу пользователя.

        Args:
            user_id: ID пользователя
            ics_content: Содержимое .ics файла в формате bytes

        Returns:
            list[EventModel]: Список созданных событий
        """
        logger.debug(f"Importing events from .ics file for user {user_id}")
        await self._ensure_user_exists(user_id)

        personal_group = await self._users_to_groups_repo.personal_group(user_id)
        if personal_group is None:
            logger.error(f"Personal group for user {user_id} not found")
            raise GroupNotFound(message="Личная группа не найдена")

        parsed_events = self.parse_ics(ics_content)
        logger.info(f"Parsed {len(parsed_events)} events from .ics file")

        created_events: list[EventModel] = []

        for parsed_event in parsed_events:
            try:
                cron = Cron(
                    date=parsed_event["date"],
                    every_day=parsed_event["every_day"],
                    every_week=parsed_event["every_week"],
                    every_month=parsed_event["every_month"],
                )

                if cron.date.tzinfo is None:
                    cron.date.replace(
                        tzinfo=timezone(
                            offset=timedelta(minutes=parsed_event["timezone"]),
                        ),
                    )

                event_create = EventCreate(
                    title=parsed_event["title"],
                    description=parsed_event["description"] or "",
                    cron=cron,
                    creator_id=user_id,
                    type="event",
                    group_id=personal_group.id,
                    duration=parsed_event["duration"],
                    participants_ids=[user_id],
                    tags_ids=[],
                    minutes_before=[],
                )

                event, _ = await self._event_service.create_event(event_create)
                created_events.append(event)
                logger.debug(f"Created event {event.id} from .ics import")

            except Exception as e:
                logger.error(
                    f"Error importing event '{parsed_event.get('title', 'Unknown')}': {e}",
                )
                continue

        logger.info(
            f"Successfully imported {len(created_events)} events from .ics file for user {user_id}",
        )
        return created_events

    async def export_user_events_all_groups(
        self,
        user_id: UserId,
    ) -> bytes:
        """Экспортирует все события пользователя из всех его групп в .ics формат.

        Args:
            user_id: ID пользователя

        Returns:
            bytes: Содержимое .ics файла
        """
        logger.debug(f"Exporting all user events from all groups for user {user_id}")
        user = await self._ensure_user_exists(user_id)

        user_groups = await self._users_to_groups_repo.user_groups(user_id)

        all_events: list[EventModel] = []
        groups_dict: dict[GroupId, GroupModel] = {}

        for group, _ in user_groups:
            groups_dict[group.id] = group
            events = await self._event_repo.list_user_events(
                group_id=group.id,
                user_id=user_id,
                tag_ids=None,
            )
            all_events.extend(events)

        logger.info(
            f"Found {len(all_events)} events for user {user_id} in {len(groups_dict)} groups",
        )
        return self.generate_ics(
            all_events,
            groups_dict,
            timezone(offset=timedelta(minutes=user.timezone)),
        )

    async def export_user_events_in_group(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> bytes:
        """Экспортирует все события пользователя в рамках одной группы в .ics формат.

        Args:
            group_id: ID группы
            user_id: ID пользователя

        Returns:
            bytes: Содержимое .ics файла
        """
        logger.debug(
            f"Exporting user events in group {group_id} for user {user_id}",
        )
        user = await self._ensure_user_exists(user_id)
        group = await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(user_id=user_id, group_id=group_id)

        events = await self._event_repo.list_user_events(
            group_id=group_id,
            user_id=user_id,
            tag_ids=None,
        )

        groups_dict = {group_id: group}

        logger.info(
            f"Found {len(events)} events for user {user_id} in group {group_id}",
        )
        return self.generate_ics(
            events,
            groups_dict,
            timezone(offset=timedelta(minutes=user.timezone)),
        )

    async def export_all_group_events(
        self,
        group_id: GroupId,
        user_id: UserId,
    ) -> bytes:
        """Экспортирует все события группы в .ics формат. Доступно только для ролей 1 и 2.

        Args:
            group_id: ID группы
            user_id: ID пользователя

        Returns:
            bytes: Содержимое .ics файла
        """
        logger.debug(
            f"Exporting all group events for group {group_id} by user {user_id}",
        )
        user = await self._ensure_user_exists(user_id)
        group = await self._ensure_group_exists(group_id)
        await self._ensure_membership_role(
            user_id=user_id,
            group_id=group_id,
            allowed_roles=(CREATOR_ROLE_ID, EDITOR_ROLE_ID),
        )

        events = await self._event_repo.get_by_group_id(group_id, tag_ids=None)

        groups_dict = {group_id: group}

        logger.info(f"Found {len(events)} events in group {group_id} for export")
        return self.generate_ics(
            events,
            groups_dict,
            timezone(offset=timedelta(minutes=user.timezone)),
        )
