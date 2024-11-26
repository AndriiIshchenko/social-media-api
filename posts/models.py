import os
import uuid

from django.utils.text import slugify
from django.conf import settings
from django.db import models


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Like(models.Model):
    class LikeChoices(models.TextChoices):
        NOTHING = "nothing"
        LIKE = "like"
        DISLIKE = "dislike"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
        blank=True,
        null=True,
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
   
    like_type = models.CharField(max_length=10, choices=LikeChoices, default=LikeChoices.NOTHING)


# class Comment(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     likes = models.ManyToManyField(Likes, related_name="comments")
#     replies = models.ManyToManyField("self", related_name="comment_replies")


def profile_image_path(instance, filename) -> str:
    _, extention = os.path.splitext(filename)
    filename = f"{slugify(instance.nickname)}-{uuid.uuid4()}{extention}"
    return os.path.join("uploads/profile/", filename)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    nickname = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(blank=True, null=True, upload_to=profile_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    following = models.ManyToManyField(
        "self",
        related_name="followers",
        blank=True,
        symmetrical=False,
    )

    def __str__(self):
        return self.nickname
