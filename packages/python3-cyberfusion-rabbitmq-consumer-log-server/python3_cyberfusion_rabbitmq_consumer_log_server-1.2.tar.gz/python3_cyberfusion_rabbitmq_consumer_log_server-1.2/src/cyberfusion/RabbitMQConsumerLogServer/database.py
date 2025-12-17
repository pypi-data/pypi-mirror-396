import sqlite3
from datetime import datetime
from typing import Optional

from sqlalchemy.pool.base import _ConnectionRecord
from sqlalchemy import ForeignKey, MetaData
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from sqlalchemy import create_engine, DateTime, Integer, String
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, mapped_column, Mapped
from sqlalchemy import event


def set_sqlite_pragma(
    dbapi_connection: sqlite3.Connection, connection_record: _ConnectionRecord
) -> None:
    """Enable foreign key support.

    This is needed for cascade deletes to work.

    See https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys
    """
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


def make_database_session() -> Session:
    engine = create_engine("sqlite:///" + settings.database_path)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RPCRequestLog(BaseModel):
    """RPC request log model."""

    __tablename__ = "rpc_requests_logs"

    correlation_id: Mapped[str] = mapped_column(String(length=36), unique=True)
    request_payload: Mapped[str] = mapped_column(String())
    virtual_host_name: Mapped[str] = mapped_column(String(length=255))
    exchange_name: Mapped[str] = mapped_column(String(length=255))
    queue_name: Mapped[str] = mapped_column(String(length=255))
    hostname: Mapped[str] = mapped_column(String(length=255))
    rabbitmq_username: Mapped[str] = mapped_column(String(length=255))


class RPCResponseLog(BaseModel):
    """RPC response log model."""

    __tablename__ = "rpc_responses_logs"

    correlation_id: Mapped[str] = mapped_column(
        String(length=36),
        ForeignKey("rpc_requests_logs.correlation_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    response_payload: Mapped[str] = mapped_column(String())
    traceback: Mapped[Optional[str]] = mapped_column(String())
