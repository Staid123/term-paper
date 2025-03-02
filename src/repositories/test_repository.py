from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from custom_exceptions import TestCreateException, TestDeleteException, TestGetException, TestUpdateException
from database.models import Test
from database.schemas import TestSchema


class TestRepository:
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
                    selectinload(Test.questions),
                    selectinload(Test.results),
                )
                .offset(skip)
                .limit(limit)
                .order_by(Test.id)
            )

            if test_id is not None:
                stmt = stmt.filter_by(id=test_id)
            
            tests = await session.scalars(stmt)
            return [test.to_pydantic() for test in tests.all()]
        except Exception as e:
            raise TestGetException(e)
    
    async def create_test(
        self,
        session: AsyncSession,
        test_schema: TestSchema
    ) -> TestSchema:
        try:
            new_test = Test(**test_schema.model_dump(exclude_unset=True))
            session.add(new_test)
            await session.commit()
            await session.refresh(new_test, attribute_names=["questions", "results"])
            return new_test.to_pydantic()
        except Exception as e:
            await session.rollback()
            raise TestCreateException(e)
        
    async def delete_test(
        self,
        session: AsyncSession,
        test_id: int
    ) -> None:
        try:
            test_to_delete: Test | None = await session.get(Test, test_id)
            if not test_to_delete:
                raise TestDeleteException(f"Test with id {test_to_delete} not found")
            
            await session.delete(test_to_delete)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise TestDeleteException(e)

    async def update_test(
        self,
        session: AsyncSession,
        test_id_to_update: int,
        test_update: TestSchema
    ) -> TestSchema:
        try:
            test = await session.get(Test, test_id_to_update, options=[selectinload(Test.questions), selectinload(Test.results)])
            if not test:
                raise TestUpdateException(f"Test with id {test_id_to_update} not found")

            update_data = test_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(test, key, value)

            await session.commit()
            await session.refresh(test)
            return test.to_pydantic()
        except Exception as e:
            await session.rollback()
            raise TestUpdateException(e)
        

TestRepositoryDep = Annotated[TestRepository, Depends(TestRepository)]
