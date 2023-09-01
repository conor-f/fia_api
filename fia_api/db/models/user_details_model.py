from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel


class UserDetailsModel(FiaBaseModel):
    """Model for user details."""

    times_logged_in = fields.IntField(null=False, default=0)

    def __str__(self) -> str:
        return f"UserDetailsModel: {self.id}"

    class Meta:
        table = "user_details"
