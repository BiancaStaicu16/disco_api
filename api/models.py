from django.db import models


class TimestampedModel(models.Model):
    """
    Generic timestamp model to be extended by all other models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
