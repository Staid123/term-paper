from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from database.schemas.question_schemas import QuestionSchema
from database.schemas.test_result_schemas import TestResultSchema


class TestBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: Optional[str] = None


class TestSchema(TestBaseSchema):

    id: int
    created_at: datetime
    updated_at: datetime
    questions: Optional[List["QuestionSchema"]] = None
    results: Optional[List["TestResultSchema"]] = None


class TestCreateSchema(TestBaseSchema):
    pass


class TestUpdateSchema(TestBaseSchema):
    title: Optional[str] = None