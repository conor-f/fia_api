from tortoise import fields, models


class FiaBaseModel(models.Model):
    """Base model to be inherited by all others. Stores basic metadata."""

    id = fields.IntField(pk=True)
    last_modified = fields.DatetimeField(auto_now=True)
    first_created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True
