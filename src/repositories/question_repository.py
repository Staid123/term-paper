from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from custom_exceptions import ActionEnum, QuestionEntityException, QuestionCreateException, QuestionDeleteException, QuestionUpdateException
from database.models import Question
from database.schemas import QuestionSchema
from repositories.base_repository import BaseRepository
from s3_actions import S3Client


class QuestionRepository(BaseRepository[Question, QuestionSchema, QuestionEntityException]):
    model = Question
    exceptions = {
        ActionEnum.CREATE: QuestionCreateException,
        ActionEnum.UPDATE: QuestionUpdateException,
        ActionEnum.DELETE: QuestionDeleteException,
    }
    
    async def before_delete(self, obj):
        """Видаляємо S3-файл перед видаленням питання"""
        if hasattr(obj, "s3_file_path") and obj.s3_file_path:
            from s3_actions import S3Client
            await S3Client.delete_file(key=obj.s3_file_path)

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

            if question.s3_file_path:
                await S3Client.delete_file(key=question.s3_file_path)

            update_data = question_update.model_dump(exclude_unset=True)
            if new_s3_file_path:
                update_data["s3_file_path"] = new_s3_file_path

            for key, value in update_data.items():
                setattr(question, key, value)

            return await super().update(
                session=session,
                object_id=question_id_to_update,
                update_schema=question_update,
            )
        except Exception as e:
            exc_cls = self.exceptions.get(ActionEnum.UPDATE, QuestionEntityException)
            raise exc_cls(str(e))
   

QuestionRepositoryDep = Annotated[QuestionRepository, Depends(QuestionRepository)]