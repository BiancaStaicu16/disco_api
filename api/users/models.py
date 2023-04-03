from django.conf import settings
from django.db import models
from api.models import TimestampedModel
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from PIL import Image
from django.core.files.images import get_image_dimensions
from sorl.thumbnail import ImageField as SorlImageField
from sorl.thumbnail import get_thumbnail
import os


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
    image = models.ImageField()
    thumbnail_200 = SorlImageField()
    thumbnail_400 = SorlImageField()

    def __str__(self):
        return f"{self.user.username} - {self.image.name}"

    def save(self, *args, **kwargs):
        if not settings.TESTING:  # Cannot get thumbnails for mocked images.
            # Get image extension.
            extension = os.path.splitext(self.image.name)[1].replace(".", "").upper()

            # Get image dimensions and adjust them to match the new ratio.
            width, height = get_image_dimensions(self.image)
            aspect_ratio = width / height
            size_200 = f"{int(aspect_ratio * 200)}x200"
            size_400 = f"{int(aspect_ratio * 400)}x400"

            # Save thumbnail images.
            self.thumbnail_200 = get_thumbnail(
                self.image, size_200, quality=99, extension=extension
            ).name
            self.thumbnail_400 = get_thumbnail(
                self.image, size_400, quality=99, extension=extension
            ).name
        super(UserImage, self).save(*args, **kwargs)


class ExpiringUserImage(TimestampedModel):
    image = models.ForeignKey(UserImage, on_delete=models.CASCADE)
    expires_in_seconds = models.IntegerField(
        default=300, validators=[MaxValueValidator(30_000), MinValueValidator(300)]
    )

    def __str__(self):
        return f"{self.user.username} - {self.image.image.name} - {self.expires_in_seconds}"
