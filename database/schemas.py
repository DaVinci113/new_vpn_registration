from datetime import datetime

from pydantic import BaseModel
from typing import List


class CreateUser(BaseModel):
    telegram_id: str
    free_plan: bool
    start_free_plan: datetime
    end_free_plan: datetime
    wallet: int


class UserUpdate(BaseModel):
    telegram_id: str
    free_plan: bool
    wallet: int
    start_plan: datetime
    end_plan: datetime
    wallet: int


class UserData(BaseModel):
    telegram_id: int
    free_plan: bool
    start_free_plan: datetime
    end_free_plan: datetime
    start_plan: datetime
    end_plan: datetime
    wallet: int


class AddUserDevice(BaseModel):
    telegram_id: str
    uuid: List[str] | None

