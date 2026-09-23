from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    telegram_id: int
    end_plan: datetime


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    free_plan: bool
    start_plan: datetime
    end_plan: datetime
    wallet: int

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    free_plan: Optional[bool] = None
    start_plan: Optional[datetime] = None
    end_plan: Optional[datetime] = None
    wallet: Optional[int] = Field(default=None, ge=0)

    model_config = {'extra': 'forbid'}


class AddUserDevice(BaseModel):
    telegram_id: str
    uuid: Optional[str] = None

