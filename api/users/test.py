from unittest.mock import MagicMock, patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from api.users.models import AccountTier, UserImage, ExpiringUserImage
from django.utils import timezone
from disco import settings
from rest_framework.exceptions import ErrorDetail

User = get_user_model()


class UserImageAPITestCase(APITestCase):
    def setUp(self):
        self.account_tier = AccountTier.objects.create(
            name="Basic",
            thumbnail_sizes="200,400",
            original_link=True,
            expiring_links=True,
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            account_tier=self.account_tier,
        )
        self.mock_image = MagicMock(spec=SimpleUploadedFile)
        self.client.force_authenticate(user=self.user)

    def test_create_user_image(self):
        # As a user, upload an image.
        self.mock_image.name = "test_image.jpg"
        self.mock_image.content_type = "image/jpeg"
        response = self.client.post("/api/users/images/", {"image": self.mock_image})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserImage.objects.filter(user=self.user).exists())

    def test_create_user_image__uses_authenticated_user(self):
        """
        Make sure that the authenticated user can only upload images to their own account.
        """
        self.mock_image.name = "test_image.jpg"
        self.mock_image.content_type = "image/jpeg"
        user_2 = User.objects.create_user(
            username="testuser2",
            password="testpassword",
            account_tier=self.account_tier,
        )
        response = self.client.post(
            "/api/users/images/", {"image": self.mock_image, "user": user_2.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserImage.objects.filter(user=self.user).exists())
        self.assertFalse(UserImage.objects.filter(user=user_2).exists())

    @patch("django.utils.timezone.now")
    def test_generate_expiring_link(self, mock_now):
        # Generate expiring link while mocking the current date.
        mock_now.return_value = timezone.datetime(2023, 1, 1, tzinfo=timezone.utc)
        self.mock_image.name = "test_image.jpg"
        self.mock_image.content_type = "image/jpeg"
        user_image = UserImage.objects.create(user=self.user, image=self.mock_image)
        response = self.client.post(
            f"/api/users/images/{user_image.pk}/generate_expiring_link/",
            {"expires_in_seconds": 300},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ExpiringUserImage.objects.filter(image=user_image).exists())

    @patch("django.utils.timezone.now")
    def test_generate_expiring_link__bad_expires_in_seconds(self, mock_now):
        # Generate expiring link while mocking the current date.
        mock_now.return_value = timezone.datetime(2023, 1, 1, tzinfo=timezone.utc)
        self.mock_image.name = "test_image.jpg"
        self.mock_image.content_type = "image/jpeg"
        user_image = UserImage.objects.create(user=self.user, image=self.mock_image)
        response = self.client.post(
            f"/api/users/images/{user_image.pk}/generate_expiring_link/",
            {"expires_in_seconds": 299},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "expires_in_seconds": [
                    ErrorDetail(
                        string="Ensure this value is greater than or equal to 300.",
                        code="min_value",
                    )
                ]
            },
        )
        self.assertFalse(ExpiringUserImage.objects.filter(image=user_image).exists())

    @patch("django.utils.timezone.now")
    def test_retrieve_expiring_image(self, mock_now):
        # Supported format.
        mock_now.return_value = timezone.datetime(2023, 1, 1, tzinfo=timezone.utc)
        self.mock_image.name = "test_image.jpg"
        self.mock_image.content_type = "image/jpeg"
        user_image = UserImage.objects.create(user=self.user, image=self.mock_image)
        expiring_user_image = ExpiringUserImage.objects.create(
            image=user_image, expires_in_seconds=300
        )

        response = self.client.get(
            f"/api/users/images/expiring/{expiring_user_image.pk}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_image_incorrect_format(self):
        # Unsupported format.
        self.mock_image.name = "test_image.bmp"
        self.mock_image.content_type = "image/bmp"
        response = self.client.post("/api/users/images/", {"image": self.mock_image})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(UserImage.objects.filter(user=self.user).exists())
        self.assertEqual(
            response.data,
            {
                "image": [
                    ErrorDetail(
                        string="Image format not supported. Please upload a PNG or JPG image.",
                        code="invalid",
                    )
                ]
            },
        )

    def test_list_user_images(self):
        # Create a few mock images for the user.
        for i in range(3):
            mock_image = MagicMock(spec=SimpleUploadedFile)
            mock_image.name = f"test_image_{i}.jpg"
            mock_image.content_type = "image/jpeg"
            UserImage.objects.create(user=self.user, image=mock_image)

        response = self.client.get("/api/users/images/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_list_user_images_unauthenticated(self):
        # Log out the test user.
        self.client.logout()
        response = self.client.get("/api/users/images/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rate_limiting(self):
        # Send requests within the allowed rate limit
        for _ in range(5):
            response = self.client.get("/api/users/images/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
