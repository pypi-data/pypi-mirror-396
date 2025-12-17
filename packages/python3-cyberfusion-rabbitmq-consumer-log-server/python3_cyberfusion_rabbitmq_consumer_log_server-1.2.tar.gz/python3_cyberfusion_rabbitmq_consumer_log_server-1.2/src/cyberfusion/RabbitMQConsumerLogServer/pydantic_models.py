from typing import Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
from pydantic import Json, ConfigDict


class PydanticModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class APIDetailMessage(PydanticModel):
    detail: str


class RPCRequestLogAPI(PydanticModel):
    correlation_id: UUID4
    request_payload: dict | list
    virtual_host_name: str
    queue_name: str
    exchange_name: str
    hostname: str
    rabbitmq_username: str


class RPCResponseLogAPI(PydanticModel):
    correlation_id: UUID4
    response_payload: dict
    traceback: Optional[str]


class RPCRequestLogDatabase(PydanticModel):
    correlation_id: UUID4
    request_payload: Json
    virtual_host_name: str
    queue_name: str
    exchange_name: str
    hostname: str
    rabbitmq_username: str
    created_at: datetime


class RPCResponseLogDatabase(PydanticModel):
    correlation_id: UUID4
    response_payload: Json
    traceback: Optional[str]
    created_at: datetime
