from .command.router import commands_router
from .errors.router import errors_router
from .errors.windows import errors_dialog
from .group.windows import groups_dialog
from .menu.windows import menu_dialog
from .profile.router import phone_router
from .profile.windows import profile_dialog
from .respond.router import respond_router
from .start.router import start_router
from .unknown.router import unknown_router

__all__ = (
    "commands_router",
    "errors_dialog",
    "errors_router",
    "groups_dialog",
    "menu_dialog",
    "phone_router",
    "profile_dialog",
    "respond_router",
    "start_router",
    "unknown_router",
)
