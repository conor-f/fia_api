from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel
from fia_api.db.models.user_model import UserModel


class UserConversationModel(FiaBaseModel):
    """Model to simply map users to conversation IDs."""

    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel",
    )
    conversation_id = fields.UUIDField(null=False, required=True)

    # ISO 639-1 language code:
    # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    language_code = fields.CharField(
        null=False,
        unique=False,
        max_length=2,  # noqa: WPS432
    )

    def __str__(self) -> str:
        return f"UserConversationModel: {self.id}"

    class Meta:
        table = "user_conversations_map"
