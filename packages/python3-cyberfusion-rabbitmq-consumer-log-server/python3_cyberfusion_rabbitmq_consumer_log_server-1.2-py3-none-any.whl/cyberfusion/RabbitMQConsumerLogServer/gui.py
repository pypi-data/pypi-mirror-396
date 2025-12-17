from fastapi import Query
from typing import Any
from fastapi import Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from cyberfusion.RabbitMQConsumerLogServer import database, pydantic_models
from cyberfusion.RabbitMQConsumerLogServer.dependencies import (
    validate_credentials,
    get_database_session,
)
from fastapi import APIRouter

from cyberfusion.RabbitMQConsumerLogServer.settings import settings

DEFAULT_LIMIT = 20

router = APIRouter(dependencies=[Depends(validate_credentials)])

views = Jinja2Templates(directory=settings.views_directory)


@router.get(  # type: ignore[untyped-decorator]
    "/rpc-requests",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all RPC requests",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect GUI password",
        },
    },
)
def rpc_requests_overview(
    request: Request,
    database_session: Session = Depends(get_database_session),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=20),
    offset: int = Query(
        default=0,
    ),
) -> Any:
    rpc_requests_database_models = (
        database_session.query(database.RPCRequestLog)
        .order_by(database.RPCRequestLog.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    rpc_responses_database_models = (
        database_session.query(database.RPCResponseLog)
        .filter(
            database.RPCResponseLog.correlation_id.in_(
                [x.correlation_id for x in rpc_requests_database_models]
            )
        )
        .all()
    )

    rpc_requests_pydantic_models = []

    rpc_responses_pydantic_models = []

    for rpc_request in rpc_requests_database_models:
        rpc_requests_pydantic_models.append(
            pydantic_models.RPCRequestLogDatabase.model_validate(rpc_request)
        )

    for rpc_response in rpc_responses_database_models:
        rpc_responses_pydantic_models.append(
            pydantic_models.RPCResponseLogDatabase.model_validate(rpc_response)
        )

    # Get template

    return views.TemplateResponse(
        name="rpc_requests_overview.html",
        context={
            "request": request,
            "rpc_requests": rpc_requests_pydantic_models,
            "rpc_responses": {
                rpc_response.correlation_id: rpc_response
                for rpc_response in rpc_responses_pydantic_models
            },
            "total_rpc_requests": database_session.query(
                database.RPCRequestLog
            ).count(),
            "offset": offset,
            "limit": limit,
        },
    )


@router.get(  # type: ignore[untyped-decorator]
    "/rpc-requests/{correlation_id}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single RPC request",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect GUI password",
        },
        status.HTTP_404_NOT_FOUND: {"description": "RPC request doesn't exist"},
    },
)
def rpc_request_detail(
    request: Request,
    correlation_id: UUID4,
    database_session: Session = Depends(get_database_session),
) -> Any:
    rpc_request_database_model = (
        database_session.query(database.RPCRequestLog)
        .filter(database.RPCRequestLog.correlation_id == str(correlation_id))
        .first()
    )

    if not rpc_request_database_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    rpc_request_pydantic_model = pydantic_models.RPCRequestLogDatabase.model_validate(
        rpc_request_database_model
    )

    rpc_response_database_model = (
        database_session.query(database.RPCResponseLog)
        .filter(database.RPCResponseLog.correlation_id == str(correlation_id))
        .first()
    )

    if rpc_response_database_model:
        rpc_response_pydantic_model = (
            pydantic_models.RPCResponseLogDatabase.model_validate(
                rpc_response_database_model
            )
        )
    else:
        rpc_response_pydantic_model = None

    return views.TemplateResponse(
        name="rpc_request_detail.html",
        context={
            "request": request,
            "rpc_request": rpc_request_pydantic_model,
            "rpc_response": rpc_response_pydantic_model,
        },
    )
