from enum import Enum

from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel
from fia_api.db.models.learning_moment_model import LearningMomentModel


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

    # This is really conceptually a "OneToMany" relation.
    learning_moments: fields.ManyToManyRelation[
        LearningMomentModel
    ] = fields.ManyToManyField(
        "models.LearningMomentModel",
        null=True,
        required=False,
        related_name="conversation_element",
    )

    def __str__(self) -> str:
        return f"ConversationElement: {self.id}"

    class Meta:
        ordering = ["first_created"]
        table = "conversation_elements"
