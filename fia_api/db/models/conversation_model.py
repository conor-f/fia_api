from enum import Enum

from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel


class ConversationElementRole(Enum):
    """Enum for role the message content is from."""

    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class ConversationElementModel(FiaBaseModel):
    """Model for a snippet of a Conversation."""

    conversation_id = fields.data.UUIDField(null=False, required=True)
    role = fields.data.CharEnumField(ConversationElementRole, required=True)
    content = fields.data.TextField(null=False, required=True)

    def __str__(self) -> str:
        return f"ConversationElement: {self.id}"

    class Meta:
        ordering = ["first_created"]
        table = "conversation_elements"
