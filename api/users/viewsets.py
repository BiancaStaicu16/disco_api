from rest_framework import viewsets, permissions, status, generics
from .models import ExpiringUserImage, UserImage
from .serializers import UserImageSerializer, ExpiringUserImageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
import os
from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.throttling import UserRateThrottle


class UserImageViewSet(viewsets.ModelViewSet):
    """
    This viewset provides operations for UserImage instances.

    list:
    Return a list of all UserImage instances associated with the authenticated user.

    create:
    Upload a new image for the authenticated user.
    """

    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        return UserImage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["POST"], url_path="generate_expiring_link")
    def generate_expiring_link(self, request, pk):
        """
        Create an expiring link for a specified UserImage instance.

        POST params:
            - expires_in_seconds: The number of seconds until the link expires.
        """
        # Check if the user has an account tier and if it supports expiring links.
        if not request.user.account_tier:
            return Response(
                {
                    "detail": "You need to have an account tier to generate expiring links."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.account_tier.expiring_links:
            return Response(
                {"detail": "Your account tier does not support expiring links."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Use ExpiringUserImageSerializer to save the instance.
        serializer = ExpiringUserImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expiring_user_image = serializer.save(image_id=pk)

        # Return the expiring link.
        expiring_link = request.build_absolute_uri(
            f"/api/users/images/expiring/{expiring_user_image.id}/"
        )
        return Response({"image": expiring_link}, status=status.HTTP_200_OK)


class RetrieveExpiringUserImage(generics.RetrieveAPIView):
    """
    Retrieve the image associated with the specified ExpiringUserImage instance.

    If the link is still valid (not expired), the image will be returned. If the link has expired, an error message will be returned.
    """

    queryset = ExpiringUserImage.objects.all()
    throttle_classes = [UserRateThrottle]

    def get(self, request, *args, **kwargs):
        expiring_user_image = self.get_object()

        # Check if the link has expired.
        if (
            expiring_user_image.created_at
            + timedelta(seconds=expiring_user_image.expires_in_seconds)
            < timezone.now()
        ):
            return Response(
                {"detail": "This link has expired."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Return the image.
        image = expiring_user_image.image.image
        ext = os.path.splitext(image.name)[1].replace(".", "")
        return HttpResponse(image, content_type=f"image/{ext}")
