from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from custom_exceptions import QuestionCreateException, QuestionDeleteException, QuestionUpdateException
from database.models import Question
from database.schemas import QuestionSchema
from s3_actions import S3Client


class QuestionRepository:
    async def create_question(
        self,
        session: AsyncSession,
        question_schema: QuestionSchema,
        s3_file_path: str | None = None
    ) -> QuestionSchema:
        try:
            new_question = Question(**question_schema.model_dump(exclude_unset=True), s3_file_path=s3_file_path)
            session.add(new_question)
            await session.commit()
            await session.refresh(new_question, attribute_names=["answers"])
            return new_question.to_pydantic()
        except Exception as e:
            await session.rollback()
            raise QuestionCreateException(e)
        
    async def delete_question(
        self,
        session: AsyncSession,
        question_id: int
    ) -> None:
        try:
            question_to_delete: Question | None = await session.get(Question, question_id)
            if not question_to_delete:
                raise QuestionDeleteException(f"Question with id {question_to_delete} not found")
            
            await S3Client.delete_file(key=question_to_delete.s3_file_path)
            
            await session.delete(question_to_delete)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise QuestionDeleteException(e)

    async def update_question(
        self,
        session: AsyncSession,
        question_id_to_update: int,
        question_update: QuestionSchema,
        new_s3_file_path: str | None = None
    ) -> QuestionSchema:
        try:
            question = await session.get(Question, question_id_to_update, options=[selectinload(Question.answers)])
            if not question:
                raise QuestionUpdateException(f"Question with id {question_id_to_update} not found")
            
            await S3Client.delete_file(key=question.s3_file_path)

            update_data = question_update.model_dump(exclude_unset=True)
            if new_s3_file_path:
                update_data["new_s3_file_path"] = new_s3_file_path

            for key, value in update_data.items():
                setattr(question, key, value)

            await session.commit()
            await session.refresh(question)
            return question.to_pydantic()
        except Exception as e:
            await session.rollback()
            raise QuestionUpdateException(e)
        

QuestionRepositoryDep = Annotated[QuestionRepository, Depends(QuestionRepository)]
