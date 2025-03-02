from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from database.schemas.answer_schemas import AnswerSchema


class QuestionBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: Optional[str] = None


class QuestionSchema(QuestionBaseSchema):

    id: int
    created_at: datetime
    updated_at: datetime
    answers: List["AnswerSchema"]


class QuestionCreateSchema(QuestionBaseSchema):
    pass


class QuestionUpdateSchema(QuestionBaseSchema):
    title: Optional[str] = None