from .core import Model


class UserCreateRequest(Model):
    max_id: int
    max_chat_id: int
    first_name: str
    last_name: str | None = None
    phone: str | None = None

    class Config(Model.Config):
        from_attributes = True


class UserUpdateRequest(Model):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None

    class Config(Model.Config):
        from_attributes = True


class UserResponse(Model):
    id: int
    max_id: int
    first_name: str
    last_name: str | None = None
    phone: str

    class Config(Model.Config):
        from_attributes = True


class UserGroupItem(Model):
    group_id: int
    name: str
    description: str | None = None
    role_id: int


class UserGroupsResponse(Model):
    groups: list[UserGroupItem]
