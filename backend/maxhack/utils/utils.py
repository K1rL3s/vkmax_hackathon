from uuid import uuid4

from maxhack.core.ids import InviteKey


def to_camel(string: str) -> str:
    """
    Верблюдезирует строку, со строчным написанием первого слова

    to_camel_case -> toCamelCase

    :param string: строка в snake case'е
    :type string: str
    :return: строка в camel case'е
    :rtype: str
    """
    return "".join(
        word if i == 0 else word.capitalize()
        for i, word in enumerate(string.split("_"))
    )


def generate_invite_key() -> InviteKey:
    return InviteKey(str(uuid4()))
