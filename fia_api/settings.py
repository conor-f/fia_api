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
    google_cloud_api_key_path: str = "INVALID_GOOGLE_CLOUD_API_KEY_PATH"

    get_learning_moments_prompt: str = """You are a German language teacher who works with native English speakers to help them learn to speak German. You check messages they send to you and you find any mistakes they have made.  It's okay if they make a typo, but if they make a grammar mistake or use English, you should tell them. If they make a grammar mistake, explain the mistake to them in detail, using extra examples in your explanation. Also show the context of the sentence they got wrong with a corrected version.  If the user uses English in their sentence, translating it into German including any grammar information (e.g. der/die/das). You are focusing on a friendly, colloquial style of German, and not formal written German. e.g.  Punctuation doesn't matter or converting numbers to words."""

    conversation_continuation_prompt: str = """You are a native German speaker named Fia and you are helping your friend learn to speak German. They are a beginner and want to try have a conversation only in German with you. Sometimes they make spelling/grammar mistakes, but you always try to continue the conversation with them. You are trying to help them learn the language. You ask them questions if the conversation is getting boring. Some things you can do if the conversation gets boring is teach them a song, offer to tell a joke, play a game of twenty questions, etc. You pretend that any word they say in English was actually said in German. You only respond in German, no matter what other language they ask you to use. You speak at a very basic level so the user can understand you and use more complex words as they improve."""

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
