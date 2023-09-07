from typing import List

from fia_api.settings import settings

MODELS_MODULES: List[str] = [
    "fia_api.db.models.dummy_model",
    "fia_api.db.models.user_model",
    "fia_api.db.models.user_details_model",
    "fia_api.db.models.conversation_model",
    "fia_api.db.models.token_usage_model",
    "fia_api.db.models.user_conversation_model",
    "fia_api.db.models.flashcard_model",
]  # noqa: WPS407

TORTOISE_CONFIG = {  # noqa: WPS407
    "connections": {
        "default": str(settings.db_url),
    },
    "apps": {
        "models": {
            "models": MODELS_MODULES + ["aerich.models"],
            "default_connection": "default",
        },
    },
}
