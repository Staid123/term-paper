from typing import TypeVar, Generic, Type
from sqlalchemy import inspect as inspect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from custom_exceptions import ActionEnum, EntityException, Exc
from database.models import Base
from sqlalchemy.orm import selectinload


T = TypeVar("T", bound=Base)
S = TypeVar("S", bound=BaseModel)

class BaseRepository(Generic[T, S, Exc]):
    model: Type[T]  # Клас моделі, який задаватиметься у нащадках
    exceptions: dict[ActionEnum, Type[Exc]] # Клас винятку, який задаватиметься у нащадках

    @property
    def relationships(self):
        return [rel.key for rel in inspect(self.model).relationships]

    async def before_delete(self, obj: Type[T]):
        """Метод, який можна перевизначати нащадках, якщо потрібно виконати дії перед видаленням"""
        pass

    async def create(
        self,
        session: AsyncSession,
        schema: S,
    ) -> S:
        try:
            new_object = self.model(**schema.model_dump(exclude_unset=True))
            session.add(new_object)
            await session.commit()
            await session.refresh(new_object, attribute_names=self.relationships)
            return new_object.to_pydantic()
        except Exception as e:
            await session.rollback()
            exc_cls = self.exceptions.get(ActionEnum.CREATE, EntityException)
            raise exc_cls(str(e))

    async def delete(
        self,
        session: AsyncSession,
        object_id: int
    ) -> None:
        try:
            exc_cls = self.exceptions.get(ActionEnum.DELETE, EntityException)

            obj_to_delete = await session.get(self.model, object_id)

            if not obj_to_delete:
                raise exc_cls(f"{self.model.__name__} with id {object_id} not found")

            await self.before_delete(obj_to_delete)

            await session.delete(obj_to_delete)
            await session.commit()
            return object_id
        except Exception as e:
            await session.rollback()
            raise exc_cls(str(e))

    async def update(
        self,
        session: AsyncSession,
        object_id: int,
        update_schema: S,
    ) -> S:
        try:
            exc_cls = self.exceptions.get(ActionEnum.UPDATE, EntityException)

            stmt_options = [selectinload(getattr(self.model, rel)) for rel in self.relationships]
            obj = await session.get(self.model, object_id, options=stmt_options)

            if not obj:
                raise exc_cls(f"Question with id {object_id} not found")

            update_data = update_schema.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(obj, key, value)

            await session.commit()
            await session.refresh(obj)
            return obj.to_pydantic()
        except Exception as e:
            await session.rollback()
            raise exc_cls(str(e))
