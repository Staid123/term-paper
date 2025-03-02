from datetime import datetime
from typing import List, Optional, TypeVar, get_args
from pydantic import BaseModel
from sqlalchemy import TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    mapped_column,
    relationship
)

from database.schemas import AnswerSchema, QuestionSchema, TestResultSchema, TestSchema

ModelType = TypeVar("ModelType", bound="Base")

class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)

    def to_pydantic(self: ModelType) -> BaseModel:
        """Automatically converts SQLAlchemy model to Pydantic schema"""
        schema_class = getattr(self.__class__, "Schema", None)

        if not schema_class:
            raise ValueError(f"Pydantic-schema for {self.__class__.__name__} not defined")
        
        schema_data = {}
        for field in schema_class.model_fields:
            value = getattr(self, field, None)
            if isinstance(value, list):
                related_schema = get_args(schema_class.model_fields[field].annotation)[0]
                schema_data[field] = [item.to_pydantic() for item in value]
            elif isinstance(value, Base):
                schema_data[field] = value.to_pydantic()
            else:
                schema_data[field] = value
        
        return schema_class(**schema_data)


class Test(Base):
    __tablename__ = "test"
    Schema = TestSchema

    title: Mapped[str] = mapped_column(unique=False)
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    questions: Mapped[List["Question"]] = relationship('Question', back_populates='test')
    results: Mapped[List["TestResult"]] = relationship('TestResult', back_populates='test')

class Question(Base):
    __tablename__ = "question"
    Schema = QuestionSchema

    title: Mapped[Optional[str]] = mapped_column(unique=False)
    description: Mapped[Optional[str]]
    s3_file_path: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    test_id: Mapped[int] = mapped_column(ForeignKey('test.id'))
    test: Mapped["Test"] = relationship('Test', back_populates='questions')

    answers: Mapped[List["Answer"]] = relationship('Answer', back_populates='question')

class Answer(Base):
    __tablename__ = "answer"
    Schema = AnswerSchema

    text: Mapped[Optional[str]]
    s3_file_path: Mapped[Optional[str]]
    points: Mapped[float] = mapped_column(default=0)
    is_correct: Mapped[bool]
    is_required: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    question_id: Mapped[int] = mapped_column(ForeignKey('question.id'))
    question: Mapped["Question"] = relationship('Question', back_populates='answers')

class TestResult(Base):
    __tablename__ = "test_result"
    Schema = TestResultSchema

    username: Mapped[str]
    user_email: Mapped[str]
    grade: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    test_id: Mapped[int] = mapped_column(ForeignKey('test.id'))
    test: Mapped["Test"] = relationship('Test', back_populates='results')
