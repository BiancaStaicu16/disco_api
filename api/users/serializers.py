from rest_framework import serializers
from .models import UserImage, ExpiringUserImage
import os
from rest_framework.exceptions import ValidationError


class UserImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = [
            "id",
            "image",
            "thumbnail_200",
            "thumbnail_400",
        ]

    def to_representation(self, instance):
        account_tier = self.context["request"].user.account_tier
        if not account_tier:
            raise ValidationError("User must have an account tier to see images")
        account_tier_name = account_tier.name
        representation = super().to_representation(instance)

        # Delete fields based on the subscription the user is on.
        if account_tier_name == "Basic":
            del representation["image"]
            del representation["thumbnail_400"]

        return representation


class UserImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = [
            "id",
            "image",
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
