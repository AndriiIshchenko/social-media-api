from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from posts.models import Like, Post, UserProfile


class LikeSerializer(serializers.ModelSerializer):
    like_type = serializers.ChoiceField(choices=Like.CHOICES)

    class Meta:
        model = Like
        fields = ("like_type",)


class PostSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    dislikes_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "content",
            "user",
            "created_at",
            "updated_at",
            "likes_amount",
            "dislikes_amount",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    dislikes_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
            "content",
            "likes_amount",
            "dislikes_amount",
        )




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "user", "nickname", "bio", "birth_date"]
        read_only_fields = ["id", "user"]


