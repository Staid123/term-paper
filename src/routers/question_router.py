from typing import Optional
import uuid
from fastapi import APIRouter, UploadFile, File

from database import SessionDep
from database.schemas import QuestionSchema, QuestionCreateSchema, QuestionUpdateSchema
from repositories.question_repository import QuestionRepositoryDep
from s3_actions import S3ClientDep


router = APIRouter(
    prefix="/question",
    tags=["Questions"]
)

@router.post('/', response_model=QuestionSchema)
async def create_question(
    session: SessionDep,
    question_repo: QuestionRepositoryDep,
    s3_client: S3ClientDep,
    title: str,
    test_id: int,
    description: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
) -> QuestionSchema:
    question_schema = QuestionCreateSchema(title=title, description=description, test_id=test_id)
    
    if file:
        s3_file_path = f"questions/{uuid.uuid4()}_{file.filename}"
        await s3_client.upload_file(file, key=s3_file_path)
    return await question_repo.create(session, question_schema)


@router.patch('/', response_model=QuestionSchema)
async def update_question(
    session: SessionDep,
    question_repo: QuestionRepositoryDep,
    question_id_to_update: int,
    s3_client: S3ClientDep,
    title: Optional[str] = None,
    description: Optional[str] = None,
    file: UploadFile = File(None),
) -> QuestionSchema:
    question_schema = QuestionUpdateSchema(title=title, description=description)
    new_s3_file_path = None

    if file:
        new_s3_file_path = f"questions/{uuid.uuid4()}_{file.filename}"
        await s3_client.upload_file(file, key=new_s3_file_path)
    return await question_repo.update_question(session, question_id_to_update, question_schema, new_s3_file_path)


@router.delete('/')
async def delete_question(
    session: SessionDep,
    question_repo: QuestionRepositoryDep,
    question_id: int,
) -> None:
    return await question_repo.delete(session, question_id)