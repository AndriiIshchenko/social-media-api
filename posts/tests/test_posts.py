import tempfile

import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient


from posts.models import Comment, Post, UserProfile
from posts.serializers import (
    CommentSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostSerializer,
)


COMMENT_URL = reverse("posts:comment-list")
POST_URL = reverse("posts:post-list")


class UnauthenticatedCinemaApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def comment_detail_url(comment_id) -> str:
    return reverse("posts:comment-detail", args=[comment_id])


def post_detail_url(post_id) -> str:
    return reverse("posts:post-detail", args=[post_id])


def add_comment_to_post_url(post_id) -> str:
    return reverse("posts:post-comment", args=[post_id])


def profile_detail_url(profile_id) -> str:
    return reverse("posts:profile-detail", args=[profile_id])


class TestCommentViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@myproject.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.profile = UserProfile.objects.create(user=self.user, nickname="testnick")
        self.post = Post.objects.create(
            user_profile=self.profile,
            content="Test Content",
            is_published=True,
        )
        self.comment = Comment.objects.create(
            user_profile=self.profile,
            post=self.post,
            content="Test Comment",
        )

    def test_create_comment(self):
        data = {
            "content": "New Comment",
            "post": self.post.id,
            "user_profile": self.profile.id,
        }
        response = self.client.post(add_comment_to_post_url(self.post.id), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_data = CommentSerializer(
            Comment.objects.get(id=response.data["id"])
        ).data
        self.assertEqual(response.data, expected_data)

    def test_retrieve_comment(self):
        url = comment_detail_url(self.comment.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = CommentSerializer(self.comment).data
        self.assertEqual(response.data, expected_data)

    def test_update_comment(self):
        url = comment_detail_url(self.comment.pk)
        data = {"content": "Updated Comment"}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        expected_data = CommentSerializer(self.comment).data
        self.assertEqual(response.data, expected_data)

    def test_delete_comment(self):
        url = comment_detail_url(self.comment.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.pk).exists())

    def test_create_comment_invalid_request(self):
        data = {"invalid": "data"}
        response = self.client.post(COMMENT_URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_comment_invalid_id(self):
        url = comment_detail_url(self.comment.pk + 1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment_invalid_id(self):
        url = comment_detail_url(self.comment.pk + 1)
        data = {"content": "Updated Comment"}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_comment_invalid_id(self):
        url = comment_detail_url(self.comment.pk + 1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestPostViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@myproject.com", password="testpass123"
        )
        self.profile = UserProfile.objects.create(user=self.user, nickname="testnick")
        self.post = Post.objects.create(
            user_profile=self.profile,
            content="Test Content",
            is_published=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        data = {"title": "New Post", "content": "New Content", "is_published": True}
        response = self.client.post(POST_URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_data = PostSerializer(Post.objects.get(id=response.data["id"])).data
        self.assertEqual(response.data, expected_data)

    def test_retrieve_post(self):
        url = post_detail_url(self.post.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = PostDetailSerializer(self.post).data
        self.assertEqual(response.data, expected_data)

    def test_update_post(self):
        url = post_detail_url(self.post.pk)
        data = {"title": "Updated Post", "content": "Updated Content"}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        expected_data = PostSerializer(self.post).data
        self.assertEqual(response.data, expected_data)

    def test_delete_post_unavailable(self):
        url = post_detail_url(self.post.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Post.objects.filter(id=self.post.pk).exists())

    def test_create_post_invalid_request(self):
        data = {"invalid": "data"}
        response = self.client.post(POST_URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_post_invalid_id(self):
        url = post_detail_url(self.post.pk + 1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_post_invalid_id(self):
        url = post_detail_url(self.post.pk + 1)
        data = {"title": "Updated Post", "content": "Updated Content"}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_posts(self):
        response = self.client.get(POST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = PostListSerializer(Post.objects.all(), many=True).data
        self.assertEqual(response.data, expected_data)


def post_image_upload_url(post_id):
    return reverse("posts:post-upload-image", args=[post_id])


class PostImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@myproject.com", password="testpass123"
        )
        self.profile = UserProfile.objects.create(user=self.user, nickname="testnick")
        self.post = Post.objects.create(
            user_profile=self.profile,
            content="Test Content",
            is_published=True,
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.post.image.delete()

    def test_upload_image_to_post(self):
        """Test uploading an image to post"""
        url = post_image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.post.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.post.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = post_image_upload_url(self.post.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_post_list(self):
        url = POST_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "content": "Some content",
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(content="Some content")
        self.assertFalse(post.image)

    def test_image_url_is_shown_on_post_detail(self):
        url = post_image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(post_detail_url(self.post.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_post_list(self):
        url = post_image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(POST_URL)

        self.assertIn("image", res.data[0].keys())
