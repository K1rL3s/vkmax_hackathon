from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq import async_shared_broker

from maxhack.core.event.service import EventService
from maxhack.core.max import MaxMailer
from maxhack.logger import get_logger

logger = get_logger(__name__, groups="tasks")


@async_shared_broker.task(
    task_name="send_notifies",
    schedule=[{"cron": "* * * * *"}],
)
@inject(patch_module=True)
async def send_notifies(
    *,
    max_mailer: FromDishka[MaxMailer],
    events_service: FromDishka[EventService],
) -> None:
    notifies = await events_service.get_notify_by_date_interval()
    for users, event in notifies:
        await max_mailer.event_notify(event, users)
