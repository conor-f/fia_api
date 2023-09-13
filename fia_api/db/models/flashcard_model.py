from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel
from fia_api.db.models.user_model import UserModel

FLASHCARD_EASE = [
    0,
    0.6,
    1.2,
    2.4,
]


class FlashcardModel(FiaBaseModel):
    """Model to represent a Flashcard."""

    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel",
    )

    # The conversation this card originated from.
    conversation_id = fields.UUIDField(null=False, required=True)

    # When to next review this card.
    next_review_date = fields.DatetimeField(auto_now_add=True)

    # The "front" and "back" of the card. i.e. the question/answer.
    front = fields.TextField(null=False, required=True)
    back = fields.TextField(null=False, required=True)
    explanation = fields.TextField(null=True, required=False)

    # The number of seconds added to get the next_review_date.
    last_review_interval = fields.IntField(null=False, default=60)

    def __str__(self) -> str:
        return f"FlashcardModel: {self.id}"

    class Meta:
        table = "flashcards"
