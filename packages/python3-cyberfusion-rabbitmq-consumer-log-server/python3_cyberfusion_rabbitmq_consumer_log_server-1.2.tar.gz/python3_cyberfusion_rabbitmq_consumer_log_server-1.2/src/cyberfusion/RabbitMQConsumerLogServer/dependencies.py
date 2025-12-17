from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import HTTPBasic

from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer.settings import settings

http_basic = HTTPBasic()


def get_database_session() -> Session:
    """Get database session."""
    database_session = database.make_database_session()

    try:
        yield database_session
    finally:
        database_session.close()


def validate_api_token(x_api_token: str = Header(title="API token")) -> str:
    """Validate API token (used by REST API)."""
    if x_api_token != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token"
        )

    return x_api_token


def validate_credentials(
    credentials: HTTPBasicCredentials = Depends(http_basic),
) -> str:
    """Validate credentials (used by GUI)."""
    if credentials.password != settings.gui_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
