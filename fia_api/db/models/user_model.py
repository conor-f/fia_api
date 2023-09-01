from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel
from fia_api.db.models.user_details_model import UserDetailsModel


class UserModel(FiaBaseModel):
    """Model for users."""

    username = fields.CharField(
        null=False,
        unique=True,
        max_length=255,  # noqa: WPS432
    )

    password_hash = fields.CharField(
        null=False,
        max_length=255,  # noqa: WPS432
    )

    # This is True if the user is fully registered and can use the site
    # featues.
    is_fully_registered = fields.BooleanField(null=False, default=False)

    # Stores more metadata about users. e.g. scores, token usage, etc
    user_details: fields.relational.OneToOneRelation[
        UserDetailsModel
    ] = fields.relational.OneToOneField("models.UserDetailsModel")

    def __str__(self) -> str:
        return f"UserModel: {self.username}"

    class Meta:
        table = "users"
