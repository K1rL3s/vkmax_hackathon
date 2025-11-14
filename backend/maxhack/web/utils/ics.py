from datetime import datetime, timedelta, timezone

from icalendar import Calendar, Event as ICalEvent
from croniter import croniter

from maxhack.core.ids import GroupId
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

    # Фильтруем события, которые уже случились (для не повторяющихся)
    current_time = datetime.now(timezone.utc)

    for event in events:
        # Пропускаем события, которые уже случились и не повторяющиеся
        if event.event_happened and not event.is_cycle:
            continue
        group = groups.get(event.group_id)
        organizer_name = group.name if group else "Unknown Group"

        # Создаем timezone для события на основе timezone события (в минутах)
        event_tz_offset = timedelta(minutes=event.timezone)
        event_timezone = timezone(event_tz_offset)

        # Парсим cron выражение
        try:
            # Используем start_date с учетом timezone события
            event_start_date = start_date.replace(tzinfo=event_timezone)
            cron = croniter(event.cron, event_start_date)
        except Exception:
            # Если cron невалидный, пропускаем событие
            continue

        # Генерируем события на основе cron
        event_count = 0
        max_events = 1000  # Ограничение на количество событий
        last_date = None

        while event_count < max_events:
            try:
                next_date = cron.get_next(datetime)
                # Приводим к timezone события
                if next_date.tzinfo is None:
                    next_date = next_date.replace(tzinfo=event_timezone)
                else:
                    next_date = next_date.astimezone(event_timezone)

                if next_date > end_date.replace(tzinfo=event_timezone):
                    break

                # Проверяем, что не генерируем одно и то же событие дважды
                if last_date and next_date <= last_date:
                    break

                # Пропускаем события, которые уже в прошлом
                if next_date < current_time.replace(tzinfo=event_timezone):
                    continue

                # Создаем событие в календаре
                ical_event = ICalEvent()
                ical_event.add("summary", event.title)
                ical_event.add("dtstart", next_date)
                ical_event.add("dtstamp", datetime.now(timezone.utc))

                # Добавляем длительность
                if event.duration:
                    end_datetime = next_date + timedelta(minutes=event.duration)
                    ical_event.add("dtend", end_datetime)
                else:
                    # Если длительность не указана, событие длится 1 час
                    ical_event.add("dtend", next_date + timedelta(hours=1))

                # Описание
                if event.description:
                    ical_event.add("description", event.description)

                # Организатор (email оставляем пустым)
                ical_event.add("organizer", f"CN={organizer_name}:mailto:")

                # Location оставляем пустым (не добавляем поле)

                # UID для уникальности события
                ical_event.add(
                    "uid",
                    f"event-{event.id}-{int(next_date.timestamp())}@maxhack",
                )

                cal.add_component(ical_event)
                event_count += 1
                last_date = next_date

                # Если событие не повторяющееся, выходим после первого
                if not event.is_cycle:
                    break

            except Exception:
                # Если ошибка при генерации следующей даты, пропускаем
                break

    # Конвертируем календарь в bytes
    ics_bytes = cal.to_ical()
    return ics_bytes

