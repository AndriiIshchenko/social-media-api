from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from posts.models import Comment, Like, Post, UserProfile


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
            "user_profile",
            "created_at",
            "updated_at",
            "likes_amount",
            "dislikes_amount",
        )

class PostListSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    dislikes_amount = serializers.IntegerField(read_only=True)
    comments_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "content",
            "user_profile",
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
            "user_profile",
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
    posts = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "nickname", "bio", "photo", "following", "followers", "posts")

    def get_following(self, obj):
        return obj.following.count()

    def get_followers(self, obj):
        return obj.followers.count()
    
    def get_posts(self, obj):
        return obj.posts.count()

class UserProfileDetailSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    commented_posts = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "nickname",
            "bio",
            "photo",
            "birth_date",
            "following",
            "followers",
            "posts",
            "commented_posts"
        ]

    def get_following(self, obj):
        return [following.nickname for following in obj.following.all()]

    def get_followers(self, obj):
        return [followers.nickname for followers in obj.followers.all()]

    def get_posts(self, obj):
        return(post.content[:30] for post in obj.posts.all())
    
    def get_commented_posts(self, obj):
        return(
            f"{comment.user_profile.nickname} posted: '{comment.post.content[0:30]}'."
            f"Your comment: '{comment.content[:30]}'"  
            for comment in obj.comments.all()
            )

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
    

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user_profile", "post", "content", "created_at")
