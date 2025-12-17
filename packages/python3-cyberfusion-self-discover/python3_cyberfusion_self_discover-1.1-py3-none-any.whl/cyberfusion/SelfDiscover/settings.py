"""Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings."""

    IMAP_SERVER_HOSTNAME: str = "imap.test"
    POP3_SERVER_HOSTNAME: str = "pop3.test"
    SMTP_SERVER_HOSTNAME: str = "smtp.test"


settings = Settings()
