# api/schemas/task.py

from pydantic import BaseModel, StringConstraints, ConfigDict
from typing import Annotated
from datetime import date, datetime


TitleStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=120)]
DescStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid") # from_attributes=True, 

    title: TitleStr
    description: DescStr | None = None
    due_date: date | None = None

class TaskResponse(BaseModel):
    # model_config = ConfigDict(from_attributes=True)

    id: int
    title: TitleStr 
    status: str
    description: DescStr | None = None
    due_date: date | None = None
    created_at: datetime
    updated_at: datetime | None = None

class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TitleStr
    description: DescStr | None = None
    due_date: date | None = None

class TaskPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TitleStr | None = None
    description: DescStr | None = None
    due_date: date | None = None