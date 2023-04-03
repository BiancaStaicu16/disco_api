from django.conf import settings
from django.db import models
from api.models import TimestampedModel
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class AccountTier(TimestampedModel):
    name = models.CharField(max_length=100)
    thumbnail_sizes = models.CharField(max_length=100)  # TODO: Make this a list
    original_link = models.BooleanField()
    expiring_links = models.BooleanField()

    def __str__(self):
        return self.name


class User(TimestampedModel, AbstractUser):
    account_tier = models.ForeignKey(AccountTier, on_delete=models.SET_NULL, null=True)


class UserImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.FileField()
    thumbnail_200 = ImageSpecField(
        source="image",
        processors=[ResizeToFit(height=200)],
        format="JPEG",
        options={"quality": 80},
    )
    thumbnail_400 = ImageSpecField(
        source="image",
        processors=[ResizeToFit(height=400)],
        format="JPEG",
        options={"quality": 80},
    )

    def __str__(self):
        return f"{self.user.username} - {self.image.name}"


class ExpiringUserImage(TimestampedModel):
    image = models.ForeignKey(UserImage, on_delete=models.CASCADE)
    expires_in_seconds = models.IntegerField(
        default=300, validators=[MaxValueValidator(30_000), MinValueValidator(300)]
    )

    def __str__(self):
        return f"{self.user.username} - {self.image.image.name} - {self.expires_in_seconds}"
