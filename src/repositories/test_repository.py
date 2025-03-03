from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database.models import Question, Test
from database.schemas import TestSchema
from repositories.base_repository import BaseRepository
from custom_exceptions import (
    TestEntityException,
    TestCreateException,
    TestDeleteException,
    TestGetException,
    TestUpdateException,
    ActionEnum
)


class TestRepository(BaseRepository[Test, TestSchema, TestEntityException]):
    model = Test
    exceptions = {
        ActionEnum.CREATE: TestCreateException,
        ActionEnum.UPDATE: TestUpdateException,
        ActionEnum.DELETE: TestDeleteException,
        ActionEnum.GET: TestGetException,
    }

    async def get_tests(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        test_id: int | None = None,
    ) -> list[TestSchema]:
        try:
            stmt = (
                select(Test)
                .options(
                    selectinload(Test.questions).selectinload(Question.answers),
                    selectinload(Test.results),
                )
                .offset(skip)
                .limit(limit)
                .order_by(Test.id)
            )

            if test_id is not None:
                stmt = stmt.filter_by(id=test_id)

            result = await session.execute(stmt)
            tests = result.scalars().all()
                    
            return [test.to_pydantic() for test in tests]
        except Exception as e:
            exc_cls = self.exceptions.get(ActionEnum.GET, TestEntityException)
            raise exc_cls(str(e))


TestRepositoryDep = Annotated[TestRepository, Depends(TestRepository)]
