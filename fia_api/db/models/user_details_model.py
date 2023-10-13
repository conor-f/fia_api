from tortoise import fields

from fia_api.db.models.fia_base_model import FiaBaseModel


class UserDetailsModel(FiaBaseModel):
    """Model for user details."""

    times_logged_in = fields.IntField(null=False, default=0)

    # ISO 639-1 language code:
    # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    current_language_code = fields.CharField(
        null=False,
        unique=False,
        default="de",
        max_length=2,  # noqa: WPS432
    )

    def __str__(self) -> str:
        return f"UserDetailsModel: {self.id}"

    class Meta:
        table = "user_details"
