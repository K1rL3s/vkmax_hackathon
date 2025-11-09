from typing import Any, Self, TypeVar

import pydantic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from maxhack.utils.utils import to_camel

ModelT = TypeVar("ModelT", bound="Model")


class Model(pydantic.BaseModel):
    """Промежуточная модель pydantic'а для унифицирования конфигов и удобного администрирования"""

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True
        from_attributes = True
        populate_by_name = True

    # noinspection Pydantic
    @classmethod
    async def from_orm_async(
        cls,
        obj: Any,
        session: AsyncSession,
    ) -> Self:
        """
        При запросе ORM моделей, с помощью асинхронной сессии, невозможно
        подгрузить отношения в асинхронном контексте "on-demand" (lazy-load при запросе вложенной сущности).
        Также, могут возникнуть проблемы для полей, с ``server_default`` параметрами.

        В связи с вышеперечисленными проблемами есть 2 варианта сериализации ORM модели к Pydantic схеме:
         * использование классического (синхронного метода ``from_orm``) с предварительной подгрузкой всех сущностей
         * использование асинхронного ``from_orm_async``

        При первом сценарии, необходимо, чтобы все маппящиеся свойства были предварительно подгружены,
        для этого можно использовать метод ``session.refresh(<entity_var>, (*<field_name>))``
        (работает и для ``server_default`` и для вложенных сущностей)
        (не забывайте слить изменения в бд через ``session.flush``,
        иначе вы откатите изменения в ORM объектах).
        Либо при составлении запроса, указывать все вложенные сущности, с помощью метода запроса ``options``,
        например, ``select(User).options(joinedload(Role))``.

        **также, необходимо помнить, что для полей ORM модели с параметром ``server_default``, работает
        стандартное правило ``expire_on_commit``**
        (правда мы не используем ``session.commit()`` явно, за редкими исключениями, но всё же)
        """

        def mapper(session: Session, obj: Any) -> Self:
            return cls.from_orm(obj)

        return await session.run_sync(mapper, obj)
