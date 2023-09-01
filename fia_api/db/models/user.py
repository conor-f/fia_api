from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel


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
    is_fully_registered = fields.BooleanField(default=False)

    def __str__(self) -> str:
        return f"UserModel: {self.username}"
