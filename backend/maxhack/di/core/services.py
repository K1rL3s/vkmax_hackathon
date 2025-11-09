from dishka import Provider, Scope, provide

from maxhack.core.event.service import EventService
from maxhack.core.group.service import GroupService
from maxhack.core.tag.service import TagService
from maxhack.core.user.service import UserService


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    user_service = provide(UserService)
    tag_service = provide(TagService)
    group_service = provide(GroupService)
    event_service = provide(EventService)
