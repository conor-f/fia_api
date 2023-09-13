from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel


class LearningMomentModel(FiaBaseModel):
    """Model to represent a LearningMoment."""

    conversation_element: fields.ReverseRelation[  # type: ignore
        "ConversationElementModel"  # type: ignore # noqa: F821
    ]

    # Leaving this generic as a JSONField as we don't know exactly what the
    # model will output. This should save almost exactly what the model
    # outputs.
    learning_moment = fields.data.JSONField(null=False, required=True)

    def __str__(self) -> str:
        return f"LearningMoment: {self.id}"

    class Meta:
        table = "learning_moments"
