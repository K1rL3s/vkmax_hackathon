from datetime import datetime, timedelta, timezone
from typing import TypedDict

from icalendar import Calendar, Event as ICalEvent
from croniter import croniter

from maxhack.core.ids import GroupId
from maxhack.core.utils.datehelp import UTC_TIMEZONE
from maxhack.database.models import EventModel, GroupModel


def generate_ics_for_events(
    events: list[EventModel],
    groups: dict[GroupId, GroupModel],
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

    current_time = datetime.now(timezone.utc)

    for event in events:
        if event.event_happened and not event.is_cycle:
            continue
        group = groups.get(event.group_id)
        organizer_name = group.name if group else "Unknown Group"

        event_tz_offset = timedelta(minutes=event.timezone)
        event_timezone = timezone(event_tz_offset)

        try:
            event_start_date = start_date.replace(tzinfo=event_timezone)
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
                    next_date = next_date.replace(tzinfo=event_timezone)
                else:
                    next_date = next_date.astimezone(event_timezone)

                if next_date > end_date.replace(tzinfo=event_timezone):
                    break

                if last_date and next_date <= last_date:
                    break

                if next_date < current_time.replace(tzinfo=event_timezone):
                    continue

                ical_event = ICalEvent()
                ical_event.add("summary", event.title)
                ical_event.add("dtstart", next_date)
                ical_event.add("dtstamp", datetime.now(timezone.utc))

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


class ParsedICSEvent(TypedDict):
    """Структура события, распарсенного из .ics файла."""

    title: str
    description: str | None
    date: datetime
    duration: int  # в минутах
    timezone: int  # offset в минутах от UTC
    every_day: bool
    every_week: bool
    every_month: bool


def parse_ics_file(ics_content: bytes) -> list[ParsedICSEvent]:
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
                        timezone_offset_minutes = int(utc_offset.total_seconds() / 60)
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

