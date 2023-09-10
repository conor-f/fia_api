# flake8: noqa

# Ignoring whole file as Flake8 _hates_ the prompts dict with line length and
# multiline strings.

import enum
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, Optional

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

    get_learning_moments_prompt = {
        "role": "assistant",
        "content": """You are an expert German language teacher who works with native English speakers to help them learn German. They give you a message and you explain each mistake in their message. You give them "Learning Moments" which they can review and learn from."""
    }
    prompts: Dict[str, Dict[str, str]] = {
        "p1": {
            "role": "system",
            "content": """You are an expert German language teacher. You hold basic conversations in German with users. You actively engage with the conversation and keep a pleasant tone. You use a simple vocabulary that the user can understand. If they don't understand you, use simpler words. If they understand you easily, use more complex words. Your response is in the following JSON object:

{
    "mistakes": A list of JSON objects. There is one object for each mistake
    made in the users message. Each object has an English language explanation
    and shows the part of the sentence the mistake was in. If there were no grammar mistakes, the list is empty.
    "fluency": A score from 0-100 of how natural sounding the users message was.
    "conversation_response": A string in the German language to continue the conversation with the user.
}

You must respond to every message in this exact structure. You must not respond in any other way.""",
        },
        "p2": {
            "role": "system",
            "content": """You are a German language teacher analyzing sentences.  You always respond in a JSON object. The JSON object has the following members: mistakes, response. mistakes is a list of every grammer/spelling/vocabulary mistake the user made. response is the German language response to the users message.""",
        },
        # BEST SO FAR!
        "p3": {
            "role": "system",
            "content": """You are a German language teacher. You correct any English words in a users message. You also explain any spelling or grammar mistakes they make in English. You are having a conversation with them. Don't translate every word, only the words that the user typed in English. Always try to continue the conversation.""",
        },
    }

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
