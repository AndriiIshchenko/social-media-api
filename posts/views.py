from django.shortcuts import render

from django.db.models import F, Q, Count
from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from posts.models import Like, Post, UserProfile
from posts.serializers import LikeSerializer, PostDetailSerializer, PostSerializer, UserProfileDetailSerializer, UserProfileFollowSerializer, UserProfileImageSerializer, UserProfileListSerializer, UserProfileSerializer, UserProfileUnfollowSerializer


class LikeViewSet(GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class PostViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = Post.objects.all().annotate(
        likes_amount=Count("likes", filter=Q(likes__like_type="like")),
        dislikes_amount=Count("likes", filter=Q(likes__like_type="dislike")),
    )
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "like":
            return LikeSerializer
        return PostSerializer

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={"like_type": request.POST.get("like_type")},
        )
        if not created:
            like.like_type = request.POST.get("like_type")
            like.save()

        serializer = self.get_serializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()




class UserProfileViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    # permission_classes = (OwnerOrReadOnlyProfile,)

    def get_queryset(self):
        """Retrieve the user's profiles with filter"""
        nickname = self.request.query_params.get("nickname")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if self.action == "list":
            queryset = self.queryset.select_related("user", ).prefetch_related(
                # # "posts__comments",
                # "sent_messages",
                "user__likes__post",
                "following",
                "followers",
            )
        elif self.action == "retrieve":
            queryset = self.queryset.select_related()
        else:
            queryset = self.queryset

        if nickname:
            queryset = queryset.filter(nickname__icontains=nickname)
        if first_name:
            queryset = queryset.filter(user__first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(user__last_name__icontains=last_name)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileListSerializer
        if self.action == "retrieve":
            return UserProfileDetailSerializer
        if self.action == "upload_image":
            return UserProfileImageSerializer
        if self.action == "follow":
            return UserProfileFollowSerializer
        if self.action == "unfollow":
            return UserProfileUnfollowSerializer
        return UserProfileSerializer

    def perform_create(self, serializer):
        if UserProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError("User already has profile")
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
        # permission_classes=(IsAuthenticated,),
    )
    def follow(self, request, pk=None):
        profile_to_follow = self.get_object()

        serializer = self.get_serializer(
            data={"profile_to_follow": profile_to_follow.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            f"Successfully followed {profile_to_follow.nickname}",
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
        # permission_classes=(IsAuthenticated,),
    )
    def unfollow(self, request, pk=None):
        profile_to_unfollow = self.get_object()

        serializer = self.get_serializer(
            data={"profile_to_unfollow": profile_to_unfollow.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
           f"Successfully unfollowed: {profile_to_unfollow.nickname}",
            status=status.HTTP_200_OK,
        )

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             name="nickname",
    #             description="Filter by nickname",
    #             required=False,
    #             type=str,
    #         ),
    #         OpenApiParameter(
    #             name="first_name",
    #             description="Filter by first name",
    #             required=False,
    #             type=str,
    #         ),
    #         OpenApiParameter(
    #             name="last_name",
    #             description="Filter by last name",
    #             required=False,
    #             type=str,
    #         ),
    #     ]
    # )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

