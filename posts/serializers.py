from rest_framework import serializers

from posts.models import Comment, Like, Post, Tag, UserProfile


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("like_type",)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "content")


class CommentForPostSerializer(serializers.ModelSerializer):
    user_profile = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="nickname"
    )

    class Meta:
        model = Comment
        fields = ("id", "user_profile", "content", "created_at")


class PostSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    dislikes_amount = serializers.IntegerField(read_only=True)
    tags = TagSerializer(many=True, required=False)

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
            "tags",
        )
        read_only_fields = ("id", "user_profile")

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        post = Post.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            post.tags.add(tag)
        return post

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", None)
        instance = super().update(instance, validated_data)

        if tags_data is not None:  # Only update tags if they were provided in the request
            if self.partial:
                # For PATCH requests, we'll add new tags without clearing existing ones
                for tag_data in tags_data:
                    tag, _ = Tag.objects.get_or_create(**tag_data)
                    if tag not in instance.tags.all():
                        instance.tags.add(tag)
            else:
                # For PUT requests, we'll replace all tags
                instance.tags.clear()
                for tag_data in tags_data:
                    tag, _ = Tag.objects.get_or_create(**tag_data)
                    instance.tags.add(tag)

        return instance


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "image"]


class PostListSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    dislikes_amount = serializers.IntegerField(read_only=True)
    comments_amount = serializers.SerializerMethodField()
    short_content = serializers.SerializerMethodField()
    user_profile = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="nickname"
    )
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Post
        fields = (
            "id",
            "user_profile",
            "created_at",
            "updated_at",
            "likes_amount",
            "dislikes_amount",
            "comments_amount",
            "short_content",
            "image",
            "tags",
        )

    def get_comments_amount(self, obj):
        return obj.comments.count()

    def get_short_content(self, obj):
        return f"{obj.content[:60]} ..."


class PostDetailSerializer(serializers.ModelSerializer):
    likes_amount = serializers.IntegerField(read_only=True)
    dislikes_amount = serializers.IntegerField(read_only=True)
    comments = CommentForPostSerializer(read_only=True, many=True)
    user_profile = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="nickname"
    )
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

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
            "comments",
            "image",
            "tags",
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
    liked_posts = serializers.SerializerMethodField()
    disliked_posts = serializers.SerializerMethodField()

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
            "commented_posts",
            "liked_posts",
            "disliked_posts",
        ]

    def get_following(self, obj):
        return [following.nickname for following in obj.following.all()]

    def get_followers(self, obj):
        return [followers.nickname for followers in obj.followers.all()]

    def get_posts(self, obj):
        return (
            f"'{post.content[:60]} ...' posted at {post.created_at} "
            for post in obj.posts.all()
        )

    def get_commented_posts(self, obj):
        return (
            f"{comment.user_profile.nickname} posted: '{comment.post.content[0:30]}'."
            f"Your comment: '{comment.content[:30]}'"
            for comment in obj.comments.all()
        )

    def get_liked_posts(self, obj):
        return (
            f"{like.post.user_profile.nickname} posted: '{like.post.content[:60]}'."
            # f"{like.post.nickname}: '{like.post.content[:60]}...'"
            for like in obj.user.likes.all()
            if like.like_type == "like"
        )

    def get_disliked_posts(self, obj):
        return (
            f"{like.post.user_profile.nickname} posted: '{like.post.content[:60]}'."
            # f"{like.post.nickname}: '{like.post.content[:60]}...'"
            for like in obj.user.likes.all()
            if like.like_type == "dislike"
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
            raise serializers.ValidationError("You are not following this user!")

        return profile_to_unfollow

    def save(self, **kwargs):
        user_profile = self.context["request"].user.profile
        profile_to_unfollow = self.validated_data["profile_to_unfollow"]
        user_profile.following.remove(profile_to_unfollow)
        return profile_to_unfollow
