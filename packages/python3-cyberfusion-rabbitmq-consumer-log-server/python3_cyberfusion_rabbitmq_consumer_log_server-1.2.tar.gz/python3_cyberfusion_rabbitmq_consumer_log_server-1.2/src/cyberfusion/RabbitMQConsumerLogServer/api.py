"""App."""

import json
from typing import Any
from fastapi import Body
from fastapi import Depends, HTTPException, status
from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer import pydantic_models
from cyberfusion.RabbitMQConsumerLogServer.dependencies import (
    get_database_session,
    validate_api_token,
)

from sqlalchemy.orm import Session
from fastapi import APIRouter

router = APIRouter(dependencies=[Depends(validate_api_token)])


@router.post(  # type: ignore[untyped-decorator]
    "/api/v1/rpc-requests",
    summary="Log RPC request",
    status_code=status.HTTP_201_CREATED,
    response_model=pydantic_models.APIDetailMessage,
    responses={
        status.HTTP_201_CREATED: {
            "model": pydantic_models.APIDetailMessage,
            "description": "RPC request logged",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": pydantic_models.APIDetailMessage,
            "description": "Invalid API token",
        },
    },
)
def log_rpc_request(
    database_session: Session = Depends(get_database_session),
    body: pydantic_models.RPCRequestLogAPI = Body(),
) -> Any:
    object_ = database.RPCRequestLog(
        correlation_id=str(body.correlation_id),
        request_payload=json.dumps(body.request_payload),
        virtual_host_name=body.virtual_host_name,
        hostname=body.hostname,
        rabbitmq_username=body.rabbitmq_username,
        exchange_name=body.exchange_name,
        queue_name=body.queue_name,
    )

    database_session.add(object_)
    database_session.commit()

    return pydantic_models.APIDetailMessage(detail="Object created")


@router.post(  # type: ignore[untyped-decorator]
    "/api/v1/rpc-responses",
    summary="Log RPC response",
    status_code=status.HTTP_201_CREATED,
    response_model=pydantic_models.APIDetailMessage,
    responses={
        status.HTTP_201_CREATED: {
            "model": pydantic_models.APIDetailMessage,
            "description": "RPC response logged",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": pydantic_models.APIDetailMessage,
            "description": "No RPC response with correlation ID",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": pydantic_models.APIDetailMessage,
            "description": "Invalid API token",
        },
    },
)
def log_rpc_response(
    database_session: Session = Depends(get_database_session),
    body: pydantic_models.RPCResponseLogAPI = Body(),
) -> Any:
    rpc_request = (
        database_session.query(database.RPCRequestLog)
        .filter(database.RPCRequestLog.correlation_id == str(body.correlation_id))
        .first()
    )

    if not rpc_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No RPC response with correlation ID {body.correlation_id}",
        )

    object_ = database.RPCResponseLog(
        correlation_id=str(body.correlation_id),
        response_payload=json.dumps(body.response_payload),
        traceback=body.traceback,
    )

    database_session.add(object_)
    database_session.commit()

    return pydantic_models.APIDetailMessage(detail="Object created")
