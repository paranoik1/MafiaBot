from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.enums import PremiumType


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Premium(Base):
    __tablename__ = "premium"

    type: Mapped[PremiumType] = mapped_column()
    expire: Mapped[DateTime] = mapped_column(DateTime)
