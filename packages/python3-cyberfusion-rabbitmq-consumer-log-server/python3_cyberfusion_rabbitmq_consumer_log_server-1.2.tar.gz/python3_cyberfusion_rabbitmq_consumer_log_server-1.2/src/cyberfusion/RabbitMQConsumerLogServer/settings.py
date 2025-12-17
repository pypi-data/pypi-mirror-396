from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings."""

    model_config = SettingsConfigDict(secrets_dir="/etc/rabbitmq-consumer-log-server")

    api_token: str = "change_me"
    gui_password: str = "change_me"
    database_path: str = "./rabbitmq-consumer-log-server.db"
    views_directory: str = "views"
    static_files_directory: str = "static"
    keep_days: int = 45


settings = Settings()
