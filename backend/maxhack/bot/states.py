from maxo.fsm.state import State, StatesGroup


class Errors(StatesGroup):
    error_intent = State()
    unexcepted_error = State()


class Menu(StatesGroup):
    menu = State()


class Profile(StatesGroup):
    my = State()


class Groups(StatesGroup):
    all = State()
    join = State()
