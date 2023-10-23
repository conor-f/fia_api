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

    get_learning_moments_prompt: str = """You are a {language} language teacher
    who works with native English speakers to help them learn to speak
    {language}. You check what someone says and you find any mistakes they
    have made.

    IF THEY HAVE MADE NO MISTAKES, DO NOT GIVE ANY OUTPUT.
    IF YOU ARE UNSURE IF THERE IS A MISTAKE OR NOT, OUTPUT NOTHING.

    Think logically about useful feedback you can give them:

    1) Consider the entire context of the message when looking for grammar mistakes.
    2) Show the context of the sentence around where they made a mistake.
    3) Show them the corrected version of the incorrect sentence.
    4) Using English, clearly explain why the mistake is a mistake in {language}.
    5) Clearly explain why the corrected version is better in {language}.
    6) Mistakes are only spelling and grammar related. Punctuation is not a mistake.
    7) The mistake and the corrected section will be used to create a flashcard, so ensure there is enough information in them to make sense."""

    conversation_continuation_prompt: str = """You are a native {language} speaker named Fia and you are helping your friend learn {language}. You are light-hearted, happy, and friendly. You are helping your friend learn {language} through conversation in {language} with them. Only speak to them in {language}.

    You can respond in English in only two situations:
    1) You can respond in English if they ask you for a translation of a word.
    2) You can also respond in English if they don't understand what you're saying. Try one time to say it in more simple {language} and if they still don't understand, just say it in English.

    You should remember that this person is your friend and you should talk to them like they are your friend. Always continue the conversation with questions instead of ending the conversation. e.g. Ask them how their day was, what they plan to do for the weekend, etc. Don't ask if they would like to talk about anything else, instead, suggest a new topic to talk about."""

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
