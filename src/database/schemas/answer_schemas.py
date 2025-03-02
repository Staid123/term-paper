from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AnswerBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: Optional[str] = None
    s3_file_path: Optional[str] = None
    points: float
    is_correct: bool
    is_required: bool


class AnswerSchema(AnswerBaseSchema):

    id: int
    created_at: datetime
    updated_at: datetime


class AnswerCreateSchema(AnswerBaseSchema):
    pass


class AnswerUpdateSchema(AnswerBaseSchema):
    pass