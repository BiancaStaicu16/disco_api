from rest_framework import serializers
from .models import UserImage


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = "__all__"
