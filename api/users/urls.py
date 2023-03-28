from django.urls import include, path
from rest_framework import routers

from api.users.viewsets import RetrieveExpiringUserImage, UserImageViewSet

router = routers.DefaultRouter()
router.register(r"images", UserImageViewSet, basename="images")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "images/expiring/<int:pk>/",
        RetrieveExpiringUserImage.as_view(),
        name="expiring_image",
    ),
]
