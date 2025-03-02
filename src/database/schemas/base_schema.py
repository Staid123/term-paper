from typing import TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

T = TypeVar("T")  # Тип ORM-модели
S = TypeVar("S", bound=BaseModel)  # Тип Pydantic-схемы

class BaseRepository(Generic[T, S]):
    model: Type[T]  # Класс модели, который будет задаваться в потомках

    async def create(
        self,
        session: AsyncSession,
        schema: S,
        **extra_fields
    ) -> S:
        """Создание объекта"""
        try:
            new_object = self.model(**schema.model_dump(exclude_unset=True), **extra_fields)
            session.add(new_object)
            await session.commit()
            await session.refresh(new_object)
            return new_object.to_pydantic()
        except Exception as e:
            await session.rollback()
            raise Exception(f"Error creating {self.model.__name__}: {e}")

    async def delete(
        self,
        session: AsyncSession,
        object_id: int
    ) -> None:
        """Удаление объекта по ID"""
        try:
            obj_to_delete = await session.get(self.model, object_id)
            if not obj_to_delete:
                raise Exception(f"{self.model.__name__} with id {object_id} not found")

            await session.delete(obj_to_delete)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise Exception(f"Error deleting {self.model.__name__}: {e}")

    async def update(
        self,
        session: AsyncSession,
        object_id: int,
        update_schema: S
    ) -> S:
        """Обновление объекта"""
        try:
            obj = await session.get(self.model, object_id)
            if not obj:
                raise Exception(f"{self.model.__name__} with id {object_id} not found")

            update_data = update_schema.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(obj, key, value)

            await session.commit()
            await session.refresh(obj)
            return obj.to_pydantic()
        except Exception as e:
            await session.rollback()
            raise Exception(f"Error updating {self.model.__name__}: {e}")
