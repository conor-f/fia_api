from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel


class TokenUsageModel(FiaBaseModel):
    """Model for tracking token usage per conversation."""

    conversation_id = fields.data.UUIDField(null=False, required=True)

    prompt_token_usage = fields.IntField(null=False, default=0)
    completion_token_usage = fields.IntField(null=False, default=0)

    def __str__(self) -> str:
        return f"TokenUsage: {self.id}"

    class Meta:
        table = "token_usage"
