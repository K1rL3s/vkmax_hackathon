from dishka import Provider, Scope, provide

from maxhack.infra.database.repos.event import EventRepo
from maxhack.infra.database.repos.group import GroupRepo
from maxhack.infra.database.repos.invite import InviteRepo
from maxhack.infra.database.repos.tag import TagRepo
from maxhack.infra.database.repos.user import UserRepo
from maxhack.infra.database.repos.users_to_groups import UsersToGroupsRepo


class ReposProvider(Provider):
    scope = Scope.REQUEST

    user_repo = provide(UserRepo)
    group_repo = provide(GroupRepo)
    invite_repo = provide(InviteRepo)
    users_to_groups_repo = provide(UsersToGroupsRepo)
    tag_repo = provide(TagRepo)
    event_repo = provide(EventRepo)
