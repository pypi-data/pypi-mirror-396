from datetime import datetime, timedelta
from cyberfusion.RabbitMQConsumerLogServer import database
from cyberfusion.RabbitMQConsumerLogServer.settings import settings


def purge_logs() -> None:
    """Purge old RPC request and response logs based on settings."""
    database_session = database.make_database_session()

    cutoff_date = datetime.utcnow() - timedelta(days=settings.keep_days)

    database_session.query(database.RPCRequestLog).filter(
        database.RPCRequestLog.created_at < cutoff_date
    ).delete()

    database_session.commit()
