from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    free_plan: Mapped[bool] = mapped_column(default=True)
    start_plan: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_plan: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    wallet: Mapped[int] = mapped_column(default=0)
