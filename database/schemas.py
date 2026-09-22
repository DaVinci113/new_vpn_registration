from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import List


class UserCreate(BaseModel):
    telegram_id: int
    end_plan: datetime


class UserUpdate(BaseModel):
    id: int
    telegram_id: str
    free_plan: bool
    wallet: int
    start_plan: datetime
    end_plan: datetime
    wallet: int


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    free_plan: bool
    start_plan: datetime
    end_plan: datetime
    wallet: int

    model_config = ConfigDict(from_attributes=True)


class AddUserDevice(BaseModel):
    telegram_id: str
    uuid: List[str] | None

