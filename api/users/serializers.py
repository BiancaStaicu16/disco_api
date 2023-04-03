from rest_framework import serializers
from .models import UserImage, ExpiringUserImage
import os


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = [
            "id",
            "image",
        ]
        read_only_fields = [
            "user",
        ]

    def validate_image(self, value):
        """
        The image extension must be either .png or .jpg.
        """
        valid_formats = [".png", ".jpg"]
        ext = os.path.splitext(value.name)[1]
        if not ext.lower() in valid_formats:
            raise serializers.ValidationError(
                "Image format not supported. Please upload a PNG or JPG image."
            )
        return value


class ExpiringUserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringUserImage
        fields = [
            "expires_in_seconds",
        ]
