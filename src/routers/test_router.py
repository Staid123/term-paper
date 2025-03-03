from typing import List, Optional
from fastapi import APIRouter

from database import SessionDep
from database.schemas import TestSchema, TestCreateSchema, TestUpdateSchema
from repositories.test_repository import TestRepositoryDep


router = APIRouter(
    prefix="/test",
    tags=["Tests"]
)

@router.get('/', response_model=List[TestSchema])
async def get_tests(
    session: SessionDep,
    test_repo: TestRepositoryDep,
    test_id: Optional[int] = None,
    skip: Optional[int] = 0,
    limit: Optional[int] = 10
) -> List[TestSchema]:
    return await test_repo.get_tests(session, skip, limit, test_id)


@router.post('/', response_model=TestSchema)
async def create_test(
    session: SessionDep,
    test_repo: TestRepositoryDep,
    test_schema: TestCreateSchema
) -> TestSchema:
    return await test_repo.create(session, test_schema)


@router.patch('/', response_model=TestSchema)
async def update_test(
    session: SessionDep,
    test_repo: TestRepositoryDep,
    test_id_to_update: int,
    test_schema: TestUpdateSchema
) -> TestSchema:
    return await test_repo.update(session, test_id_to_update, test_schema)


@router.delete('/')
async def delete_test(
    session: SessionDep,
    test_repo: TestRepositoryDep,
    test_id: int
):
    deleted_test_id = await test_repo.delete(session, test_id)
    return {"deleted_test_id": deleted_test_id}