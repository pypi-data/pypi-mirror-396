import datetime

from sqlalchemy import func, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sqlalchemy_utils.types import UUIDType


class Base(AsyncAttrs, DeclarativeBase):
    """Base model"""

    pass


class StoredActivity(Base):
    """Stored activity in the database"""

    __tablename__ = "simple_storage_stored_activity"
    id: Mapped[bytes] = mapped_column(UUIDType(binary=True), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    actor: Mapped[str] = mapped_column()
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class StoredObject(Base):
    """Stored object in the database"""

    __tablename__ = "simple_storage_stored_object"
    id: Mapped[bytes] = mapped_column(UUIDType(binary=True), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    actor: Mapped[str] = mapped_column()
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
