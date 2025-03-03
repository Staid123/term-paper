from enum import Enum
from typing import Type, TypeVar


class ActionEnum(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    GET = "get"


class EntityException(Exception):
    """Базовий виняток для сутностей."""

    def __init__(self, entity: str, action: ActionEnum, message: str):
        self.message = f"Failed to {action.value} {entity}: {message}"
        super().__init__(self.message)

class TestEntityException(EntityException):
    """Базовий виняток для Test"""
    pass

class QuestionEntityException(EntityException):
    """Базовий виняток для Question"""
    pass

Exc = TypeVar("Exc", bound=EntityException)

def create_exception_class(entity: str, action: ActionEnum, exception_class: Type[Exc]) -> Type[Exc]:
    """Фабрика винятків для сутності."""
    class CustomException(exception_class):
        def __init__(self, message: str):
            super().__init__(entity, action, message)
    return CustomException


TestCreateException = create_exception_class("test", ActionEnum.CREATE, TestEntityException)
TestDeleteException = create_exception_class("test", ActionEnum.DELETE, TestEntityException)
TestGetException = create_exception_class("test", ActionEnum.GET, TestEntityException)
TestUpdateException = create_exception_class("test", ActionEnum.UPDATE, TestEntityException)

QuestionCreateException = create_exception_class("question", ActionEnum.CREATE, QuestionEntityException)
QuestionDeleteException = create_exception_class("question", ActionEnum.DELETE, QuestionEntityException)
QuestionUpdateException = create_exception_class("question", ActionEnum.UPDATE, QuestionEntityException)
