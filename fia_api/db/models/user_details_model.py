from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel
from fia_api.db.models.user_model import UserModel


class UserDetailsModel(FiaBaseModel):
    """Model for user details."""

    user_id: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel",
        related_name="UserModel.id",
    )

    times_logged_in = fields.IntField(null=False, default=0)

    def __str__(self) -> str:
        return f"UserDetailsModel: {self.id}"
