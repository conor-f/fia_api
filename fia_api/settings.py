# flake8: noqa

# Ignoring whole file as Flake8 _hates_ the prompts dict with line length and
# multiline strings.

import enum
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "fia_api"
    db_pass: str = "fia_api"
    db_base: str = "fia_api"
    db_echo: bool = False

    # Variables for Redis
    redis_host: str = "fia_api-redis"
    redis_port: int = 6379
    redis_user: Optional[str] = None
    redis_pass: Optional[str] = None
    redis_base: Optional[int] = None

    # Variables for Auth:
    # Override these in env.
    jwt_secret_key: str = "jwt_secret_key"
    jwt_refresh_secret_key: str = "jwt_refresh_secret_key"

    openai_api_key: str = "INVALID_OPENAI_API_KEY"

    get_learning_moments_prompt: str = """You are an expert German language teacher who works with native English speakers to help them learn German.  You analyze messages they send you and you find any mistakes they have made in them. You pay particular attention to grammar mistakes. If the user uses the English language in their sentence, help them by translating it into German. You are focusing on a colloquial spoken German style, and not formal written German."""
    conversation_continuation_prompt: str = """You are a native German speaker who is helping an English speaker learn to speak German. They are a beginner and want to try have a conversation only in German with you.  Sometimes they make spelling/grammar mistakes, but you always try to continue the conversation with them. You are friendly and ask questions to direct the conversation to help the user learn. You are allowed to use English if the user asks you what a word means, and to explain difficult words, but you don't have to. Apart from that, you only respond in German. You speak at a very basic level so the user can understand you. Some things you can use to get a conversation started with a user include: - Asking how their day has been. - Talking to them about their hobbies. - Playing the game Twenty Questions. - Asking them if they want to pretend to order something in a cafe. - etc"""

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgres",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FIA_API_",
        env_file_encoding="utf-8",
    )


settings = Settings()
