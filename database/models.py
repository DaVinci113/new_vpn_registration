from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sqlalchemy import DateTime, func, ForeignKey


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int]
    free_plan: Mapped[bool] = mapped_column(default=True)
    start_free_plan: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_free_plan: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    start_plan: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_plan: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    wallet: Mapped[int] = mapped_column(default=0)
