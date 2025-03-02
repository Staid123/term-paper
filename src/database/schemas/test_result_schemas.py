from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TestResultSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    user_email: str
    grade: float
    created_at: datetime