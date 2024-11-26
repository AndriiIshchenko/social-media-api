from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from posts.models import Like, Post, UserProfile


class LikeSerializer(serializers.ModelSerializer):
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
        fields = ("id", "user", "nickname", "bio", "birth_date")
        read_only_fields = ("id", "user")


class UserProfileListSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "nickname", "bio", "photo", "following", "followers")

    def get_following(self, obj):
        return obj.following.count()

    def get_followers(self, obj):
        return obj.followers.count()


class UserProfileDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "nickname",
            "first_name",
            "last_name",
            "bio",
            "photo",
            "birth_date",
            "following",
            "followers",
        ]

    def get_following(self, obj):
        return [following.nickname for following in obj.following.all()]

    def get_followers(self, obj):
        return [followers.nickname for followers in obj.followers.all()]


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "photo"]


class UserProfileFollowSerializer(serializers.ModelSerializer):
    profile_to_follow = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all()
    )

    class Meta:
        model = UserProfile
        fields = ("profile_to_follow",)

    def validate_profile_to_follow(self, profile_to_follow):
        user_profile = self.context["request"].user.profile

        if profile_to_follow == user_profile:
            raise serializers.ValidationError("You can't follow yourself!")

        if profile_to_follow in user_profile.following.all():
            raise serializers.ValidationError("You already follow this user!")

        return profile_to_follow

    def save(self, **kwargs):
        user_profile = self.context["request"].user.profile
        profile_to_follow = self.validated_data["profile_to_follow"]
        user_profile.following.add(profile_to_follow)
        return profile_to_follow


class UserProfileUnfollowSerializer(serializers.ModelSerializer):
    profile_to_unfollow = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all()
    )

    class Meta:
        model = UserProfile
        fields = ["profile_to_unfollow"]

    def validate_profile_to_unfollow(self, profile_to_unfollow):
        user_profile = self.context["request"].user.profile

        if profile_to_unfollow == user_profile:
            raise serializers.ValidationError("You can't unfollow yourself!")

        if profile_to_unfollow not in user_profile.following.all():
            raise serializers.ValidationError(
                "You are not following this user!"
            )

        return profile_to_unfollow

    def save(self, **kwargs):
        user_profile = self.context["request"].user.profile
        profile_to_unfollow = self.validated_data["profile_to_unfollow"]
        user_profile.following.remove(profile_to_unfollow)
        return profile_to_unfollow
