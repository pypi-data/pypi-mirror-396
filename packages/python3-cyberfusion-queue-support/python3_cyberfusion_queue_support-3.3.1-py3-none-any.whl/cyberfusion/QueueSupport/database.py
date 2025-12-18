from typing import List, Optional
import json
from sqlalchemy import Enum

from alembic.config import Config
import os
import functools
from alembic import command
import sqlite3
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.pool.base import _ConnectionRecord
from sqlalchemy import ForeignKey, MetaData, Boolean
from sqlalchemy import create_engine, DateTime, Integer, String
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import event
from sqlalchemy.types import JSON

from cyberfusion.QueueSupport.encoders import CustomEncoder
from cyberfusion.QueueSupport.enums import QueueProcessStatus
from cyberfusion.QueueSupport.settings import settings


def set_sqlite_pragma(
    dbapi_connection: sqlite3.Connection, connection_record: _ConnectionRecord
) -> None:
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")

    cursor.close()


def run_migrations() -> None:
    """Upgrade database schema to latest version."""
    alembic_config = Config()

    alembic_config.set_main_option("sqlalchemy.url", settings.database_path)
    alembic_config.set_main_option(
        "script_location",
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "migrations"),
    )

    command.upgrade(alembic_config, "head")


def make_database_session() -> Session:
    engine = create_engine(
        settings.database_path,
        json_serializer=lambda obj: json.dumps(obj, cls=CustomEncoder),
    )

    event.listen(engine, "connect", set_sqlite_pragma)

    return sessionmaker(bind=engine)()


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = metadata_obj


class BaseModel(Base):
    """Base model."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=functools.partial(datetime.now, timezone.utc),
    )


class Queue(BaseModel):
    """Queue model."""

    __tablename__ = "queues"

    queue_items: Mapped[List["QueueItem"]] = relationship(
        "QueueItem",
        back_populates="queue",
        cascade="all, delete",
    )
    queue_processes: Mapped[List["QueueProcess"]] = relationship(
        "QueueProcess",
        back_populates="queue",
        cascade="all, delete",
    )


class QueueProcess(BaseModel):
    """QueueProcess model."""

    __tablename__ = "queue_processes"

    queue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("queues.id", ondelete="CASCADE"), index=True
    )
    preview: Mapped[bool] = mapped_column(
        Boolean,
    )
    status: Mapped[Optional[QueueProcessStatus]] = mapped_column(
        Enum(QueueProcessStatus),
    )

    queue: Mapped["Queue"] = relationship(
        "Queue", back_populates="queue_processes", uselist=False
    )
    queue_item_outcomes: Mapped[List["QueueItemOutcome"]] = relationship(
        "QueueItemOutcome",
        back_populates="queue_process",
        cascade="all, delete",
    )


class QueueItem(BaseModel):
    """QueueItem model."""

    __tablename__ = "queue_items"

    queue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("queues.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(
        String(length=255),
    )
    reference: Mapped[Optional[str]] = mapped_column(
        String(length=255),
    )
    hide_outcomes: Mapped[bool] = mapped_column(
        Boolean,
    )
    fail_silently: Mapped[bool] = mapped_column(
        Boolean,
    )
    deduplicated: Mapped[bool] = mapped_column(
        Boolean,
    )
    attributes: Mapped[dict] = mapped_column(
        JSON,
    )
    traceback: Mapped[Optional[str]] = mapped_column(
        String(),
    )

    queue: Mapped["Queue"] = relationship(
        "Queue", back_populates="queue_items", uselist=False
    )
    queue_item_outcomes: Mapped[List["QueueItemOutcome"]] = relationship(
        "QueueItemOutcome",
        back_populates="queue_item",
        cascade="all, delete",
    )


class QueueItemOutcome(BaseModel):
    """QueueItemOutcome model."""

    __tablename__ = "queue_item_outcomes"

    queue_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("queue_items.id", ondelete="CASCADE"),
        index=True,
    )
    queue_process_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("queue_processes.id", ondelete="CASCADE"),
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(length=255),
    )
    attributes: Mapped[dict] = mapped_column(
        JSON,
    )
    string: Mapped[str] = mapped_column(
        String(length=255),
    )

    queue_item: Mapped["QueueItem"] = relationship(
        "QueueItem", back_populates="queue_item_outcomes", uselist=False
    )
    queue_process: Mapped["QueueProcess"] = relationship(
        "QueueProcess", back_populates="queue_item_outcomes"
    )
